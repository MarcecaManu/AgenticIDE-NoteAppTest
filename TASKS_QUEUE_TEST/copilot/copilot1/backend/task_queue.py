"""Task queue implementation using asyncio."""
import asyncio
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
import logging

from .models import Task, TaskType, TaskStatus
from .storage import TaskStorage
from .task_handlers import TaskHandlers

logger = logging.getLogger(__name__)


class TaskQueue:
    """Asyncio-based task queue for background processing."""
    
    def __init__(self, storage: TaskStorage):
        self.storage = storage
        self.queue: asyncio.Queue = asyncio.Queue()
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.handlers = TaskHandlers()
        self._worker_task: Optional[asyncio.Task] = None
        self._is_running = False
        
        # Map task types to handlers
        self.task_type_handlers = {
            TaskType.DATA_PROCESSING: self.handlers.data_processing_task,
            TaskType.EMAIL_SIMULATION: self.handlers.email_simulation_task,
            TaskType.IMAGE_PROCESSING: self.handlers.image_processing_task,
        }
    
    async def start(self):
        """Start the task queue worker."""
        if not self._is_running:
            self._is_running = True
            self._worker_task = asyncio.create_task(self._worker())
            logger.info("Task queue worker started")
            
            # Re-queue any pending tasks from storage
            await self._requeue_pending_tasks()
    
    async def stop(self):
        """Stop the task queue worker."""
        self._is_running = False
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        
        # Cancel all running tasks
        for task_id, running_task in list(self.running_tasks.items()):
            running_task.cancel()
            try:
                await running_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Task queue worker stopped")
    
    async def _requeue_pending_tasks(self):
        """Re-queue any pending tasks from storage on startup."""
        pending_tasks = self.storage.get_tasks_by_status(TaskStatus.PENDING)
        for task in pending_tasks:
            await self.queue.put(task.id)
            logger.info(f"Re-queued pending task: {task.id}")
    
    async def submit_task(self, task_type: TaskType, parameters: Optional[Dict[str, Any]] = None) -> Task:
        """Submit a new task to the queue."""
        task_id = str(uuid.uuid4())
        task = Task(task_id=task_id, task_type=task_type, parameters=parameters)
        
        # Save to storage
        self.storage.add_task(task)
        
        # Add to queue
        await self.queue.put(task_id)
        
        logger.info(f"Task submitted: {task_id} (type: {task_type})")
        return task
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a task."""
        task = self.storage.get_task(task_id)
        if not task:
            return False
        
        # Check if task can be cancelled
        if task.status not in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            return False
        
        # If task is running, cancel it
        if task_id in self.running_tasks:
            self.running_tasks[task_id].cancel()
            try:
                await self.running_tasks[task_id]
            except (asyncio.CancelledError, Exception) as e:
                # Handle any exception during cancellation
                logger.debug(f"Exception during task cancellation: {e}")
            
            # Clean up running tasks dict
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
        
        # Update task status
        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.now()
        self.storage.update_task(task)
        logger.info(f"Task cancelled: {task_id}")
        return True
    
    async def retry_task(self, task_id: str) -> Optional[Task]:
        """Retry a failed task."""
        task = self.storage.get_task(task_id)
        if not task or task.status != TaskStatus.FAILED:
            return None
        
        # Create a new task with the same parameters
        new_task = await self.submit_task(task.task_type, task.parameters)
        logger.info(f"Task retried: {task_id} -> {new_task.id}")
        return new_task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        return self.storage.get_task(task_id)
    
    def get_all_tasks(self) -> list[Task]:
        """Get all tasks."""
        return self.storage.get_all_tasks()
    
    async def _worker(self):
        """Background worker that processes tasks from the queue."""
        while self._is_running:
            try:
                # Get next task from queue with timeout
                try:
                    task_id = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                
                # Get task from storage
                task = self.storage.get_task(task_id)
                if not task:
                    logger.warning(f"Task not found in storage: {task_id}")
                    continue
                
                # Skip if task was cancelled
                if task.status == TaskStatus.CANCELLED:
                    logger.info(f"Skipping cancelled task: {task_id}")
                    continue
                
                # Execute task
                asyncio.create_task(self._execute_task(task))
                
            except Exception as e:
                logger.error(f"Error in worker loop: {e}")
    
    async def _execute_task(self, task: Task):
        """Execute a single task."""
        task_id = task.id
        
        try:
            # Update task status to RUNNING
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()
            task.progress = 0.0
            self.storage.update_task(task)
            
            # Get handler for task type
            handler = self.task_type_handlers.get(task.task_type)
            if not handler:
                raise ValueError(f"No handler for task type: {task.task_type}")
            
            # Create progress callback
            def update_progress(progress: float):
                task.progress = min(100.0, max(0.0, progress))
                self.storage.update_task(task)
            
            # Execute handler
            execution_task = asyncio.create_task(handler(task, update_progress))
            self.running_tasks[task_id] = execution_task
            
            result = await execution_task
            
            # Task completed successfully
            task.status = TaskStatus.SUCCESS
            task.completed_at = datetime.now()
            task.result_data = result
            task.progress = 100.0
            self.storage.update_task(task)
            
            logger.info(f"Task completed successfully: {task_id}")
            
        except asyncio.CancelledError:
            # Task was cancelled
            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.now()
            task.error_message = "Task was cancelled"
            self.storage.update_task(task)
            logger.info(f"Task cancelled during execution: {task_id}")
            
        except Exception as e:
            # Task failed
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now()
            task.error_message = str(e)
            self.storage.update_task(task)
            logger.error(f"Task failed: {task_id} - {e}")
        
        finally:
            # Remove from running tasks
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
