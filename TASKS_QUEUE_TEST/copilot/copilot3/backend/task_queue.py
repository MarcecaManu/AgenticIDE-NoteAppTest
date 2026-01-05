"""Task queue manager with asyncio-based background processing."""
import asyncio
import uuid
import json
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from models import Task, TaskStatus
from database import get_db
from task_handlers import TASK_HANDLERS


class TaskQueue:
    """Asyncio-based task queue manager."""
    
    def __init__(self):
        """Initialize task queue."""
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.worker_task: Optional[asyncio.Task] = None
        self.queue: asyncio.Queue = asyncio.Queue()
        self.is_running = False
        
    async def start_worker(self):
        """Start background worker."""
        if self.is_running:
            print("[TaskQueue] Worker already running")
            return
            
        print("[TaskQueue] Starting worker...")
        self.is_running = True
        self.worker_task = asyncio.create_task(self._worker())
        print(f"[TaskQueue] Worker task created: {self.worker_task}")
        
    async def stop_worker(self):
        """Stop background worker."""
        self.is_running = False
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass
                
    async def _worker(self):
        """Background worker that processes tasks from queue."""
        print(f"[TaskQueue] Worker started, is_running={self.is_running}")
        while self.is_running:
            try:
                task_id = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                print(f"[TaskQueue] Got task from queue: {task_id}")
                asyncio.create_task(self._execute_task(task_id))
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"[TaskQueue] Worker error: {e}")
                
    async def submit_task(self, task_type: str, params: Dict[str, Any], db_session: Optional[Session] = None) -> str:
        """
        Submit a new task to the queue.
        
        Args:
            task_type: Type of task to execute
            params: Task input parameters
            db_session: Optional database session (for testing)
            
        Returns:
            Task ID
        """
        task_id = str(uuid.uuid4())
        
        # Create task in database
        if db_session:
            # Use provided session - MUST commit before queueing so worker can find it
            task = Task(
                id=task_id,
                task_type=task_type,
                status=TaskStatus.PENDING,
                input_params=json.dumps(params),
                created_at=datetime.utcnow(),
            )
            db_session.add(task)
            # Commit immediately so worker can find the task
            db_session.commit()
        else:
            # Use context manager for production (auto-commits)
            with get_db() as db:
                task = Task(
                    id=task_id,
                    task_type=task_type,
                    status=TaskStatus.PENDING,
                    input_params=json.dumps(params),
                    created_at=datetime.utcnow(),
                )
                db.add(task)
                db.commit()
        
        # Add to queue AFTER commit so worker can find the task
        await self.queue.put(task_id)
        print(f"[TaskQueue] Task {task_id} added to queue. Queue size: {self.queue.qsize()}")
        
        return task_id
        
    async def _execute_task(self, task_id: str):
        """
        Execute a task.
        
        Args:
            task_id: Task identifier
        """
        print(f"[TaskQueue] Executing task: {task_id}")
        try:
            # Update task status to RUNNING
            with get_db() as db:
                task = db.query(Task).filter(Task.id == task_id).first()
                if not task:
                    print(f"[TaskQueue] Task {task_id} not found in database")
                    return
                    
                # Check if task was cancelled
                if task.status == TaskStatus.CANCELLED:
                    return
                    
                task.status = TaskStatus.RUNNING
                task.started_at = datetime.utcnow()
                db.commit()
                
                task_type = task.task_type
                input_params = json.loads(task.input_params) if task.input_params else {}
            
            # Get task handler
            handler = TASK_HANDLERS.get(task_type)
            if not handler:
                raise Exception(f"Unknown task type: {task_type}")
            
            # Execute task
            result = await handler(task_id, input_params, self._update_progress)
            
            # Update task with success
            with get_db() as db:
                task = db.query(Task).filter(Task.id == task_id).first()
                if task and task.status != TaskStatus.CANCELLED:
                    task.status = TaskStatus.SUCCESS
                    task.completed_at = datetime.utcnow()
                    task.result_data = json.dumps(result)
                    task.progress = 100.0
                    db.commit()
                    
        except Exception as e:
            # Update task with failure
            with get_db() as db:
                task = db.query(Task).filter(Task.id == task_id).first()
                if task and task.status != TaskStatus.CANCELLED:
                    task.status = TaskStatus.FAILED
                    task.completed_at = datetime.utcnow()
                    task.error_message = str(e)
                    db.commit()
                    
        finally:
            # Remove from running tasks
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
                
    async def _update_progress(self, task_id: str, progress: float):
        """
        Update task progress.
        
        Args:
            task_id: Task identifier
            progress: Progress percentage (0-100)
        """
        with get_db() as db:
            task = db.query(Task).filter(Task.id == task_id).first()
            if task:
                task.progress = progress
                db.commit()
                
    async def cancel_task(self, task_id: str, db_session: Optional[Session] = None) -> bool:
        """
        Cancel a task.
        
        Args:
            task_id: Task identifier
            db_session: Optional database session (for testing)
            
        Returns:
            True if cancelled, False otherwise
        """
        if db_session:
            task = db_session.query(Task).filter(Task.id == task_id).first()
            if not task:
                return False
                
            if task.status in [TaskStatus.SUCCESS, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                return False
                
            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.utcnow()
            db_session.flush()
        else:
            with get_db() as db:
                task = db.query(Task).filter(Task.id == task_id).first()
                if not task:
                    return False
                    
                if task.status in [TaskStatus.SUCCESS, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                    return False
                    
                task.status = TaskStatus.CANCELLED
                task.completed_at = datetime.utcnow()
                db.commit()
            
        # Cancel running task if exists
        if task_id in self.running_tasks:
            self.running_tasks[task_id].cancel()
            
        return True
        
    async def retry_task(self, task_id: str, db_session: Optional[Session] = None) -> Optional[str]:
        """
        Retry a failed task.
        
        Args:
            task_id: Task identifier
            db_session: Optional database session (for testing)
            
        Returns:
            New task ID or None if task cannot be retried
        """
        new_task_id = str(uuid.uuid4())
        
        if db_session:
            task = db_session.query(Task).filter(Task.id == task_id).first()
            if not task or task.status != TaskStatus.FAILED:
                return None
                
            # Create new task with same parameters
            new_task = Task(
                id=new_task_id,
                task_type=task.task_type,
                status=TaskStatus.PENDING,
                input_params=task.input_params,
                created_at=datetime.utcnow(),
                retry_count=task.retry_count + 1,
            )
            db_session.add(new_task)
            db_session.flush()
        else:
            with get_db() as db:
                task = db.query(Task).filter(Task.id == task_id).first()
                if not task or task.status != TaskStatus.FAILED:
                    return None
                    
                # Create new task with same parameters
                new_task = Task(
                    id=new_task_id,
                    task_type=task.task_type,
                    status=TaskStatus.PENDING,
                    input_params=task.input_params,
                    created_at=datetime.utcnow(),
                    retry_count=task.retry_count + 1,
                )
                db.add(new_task)
                db.commit()
        
        # Add to queue
        await self.queue.put(new_task_id)
        
        return new_task_id


# Global task queue instance
task_queue = TaskQueue()
