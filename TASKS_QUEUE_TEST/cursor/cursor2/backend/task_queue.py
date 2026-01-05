"""
Asyncio-based task queue manager
"""
import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from backend.database import get_db
from backend.models import Task
from backend.task_workers import TASK_WORKERS


class TaskQueue:
    """Manages background task execution using asyncio"""
    
    def __init__(self, db_session_maker=None):
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.queue = asyncio.Queue()
        self.worker_task: Optional[asyncio.Task] = None
        self.is_running = False
        self.db_session_maker = db_session_maker  # Allow injection for testing
    
    async def start(self):
        """Start the task queue worker"""
        if not self.is_running:
            self.is_running = True
            self.worker_task = asyncio.create_task(self._process_queue())
    
    async def stop(self):
        """Stop the task queue worker"""
        self.is_running = False
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass
    
    async def submit_task(self, task_type: str, parameters: Dict[str, Any]) -> str:
        """Submit a new task to the queue"""
        task_id = str(uuid.uuid4())
        
        # Create task in database (use injected session maker if available)
        if self.db_session_maker:
            db = self.db_session_maker()
            try:
                task = Task(
                    id=task_id,
                    task_type=task_type,
                    status="PENDING",
                    created_at=datetime.utcnow(),
                    parameters=json.dumps(parameters),
                    progress=0.0
                )
                db.add(task)
                db.commit()
            finally:
                db.close()
        else:
            with get_db() as db:
                task = Task(
                    id=task_id,
                    task_type=task_type,
                    status="PENDING",
                    created_at=datetime.utcnow(),
                    parameters=json.dumps(parameters),
                    progress=0.0
                )
                db.add(task)
                db.commit()
        
        # Add to queue
        await self.queue.put(task_id)
        
        return task_id
    
    async def _process_queue(self):
        """Process tasks from the queue"""
        while self.is_running:
            try:
                # Get next task from queue
                task_id = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                
                # Start task execution in background
                task_coro = self._execute_task(task_id)
                self.running_tasks[task_id] = asyncio.create_task(task_coro)
                
            except asyncio.TimeoutError:
                # No tasks in queue, continue
                continue
            except Exception as e:
                print(f"Error processing queue: {e}")
    
    async def _execute_task(self, task_id: str):
        """Execute a single task"""
        try:
            # Get task from database (use injected session maker if available)
            if self.db_session_maker:
                db = self.db_session_maker()
                try:
                    task = db.query(Task).filter(Task.id == task_id).first()
                    if not task:
                        return
                    
                    task_type = task.task_type
                    parameters = json.loads(task.parameters) if task.parameters else {}
                    
                    # Update task status to RUNNING
                    task.status = "RUNNING"
                    task.started_at = datetime.utcnow()
                    db.commit()
                finally:
                    db.close()
            else:
                with get_db() as db:
                    task = db.query(Task).filter(Task.id == task_id).first()
                    if not task:
                        return
                    
                    task_type = task.task_type
                    parameters = json.loads(task.parameters) if task.parameters else {}
                    
                    # Update task status to RUNNING
                    task.status = "RUNNING"
                    task.started_at = datetime.utcnow()
                    db.commit()
            
            # Get worker for task type
            worker_class = TASK_WORKERS.get(task_type)
            if not worker_class:
                raise ValueError(f"Unknown task type: {task_type}")
            
            # Execute task
            result = await worker_class.execute(task_id, parameters)
            
            # Update task as SUCCESS
            if self.db_session_maker:
                db = self.db_session_maker()
                try:
                    task = db.query(Task).filter(Task.id == task_id).first()
                    if task:
                        task.status = "SUCCESS"
                        task.completed_at = datetime.utcnow()
                        task.result_data = json.dumps(result)
                        task.progress = 100.0
                        db.commit()
                finally:
                    db.close()
            else:
                with get_db() as db:
                    task = db.query(Task).filter(Task.id == task_id).first()
                    if task:
                        task.status = "SUCCESS"
                        task.completed_at = datetime.utcnow()
                        task.result_data = json.dumps(result)
                        task.progress = 100.0
                        db.commit()
        
        except Exception as e:
            # Update task as FAILED
            if self.db_session_maker:
                db = self.db_session_maker()
                try:
                    task = db.query(Task).filter(Task.id == task_id).first()
                    if task and task.status != "CANCELLED":
                        task.status = "FAILED"
                        task.completed_at = datetime.utcnow()
                        task.error_message = str(e)
                        db.commit()
                finally:
                    db.close()
            else:
                with get_db() as db:
                    task = db.query(Task).filter(Task.id == task_id).first()
                    if task and task.status != "CANCELLED":
                        task.status = "FAILED"
                        task.completed_at = datetime.utcnow()
                        task.error_message = str(e)
                        db.commit()
        
        finally:
            # Remove from running tasks
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or running task"""
        if self.db_session_maker:
            db = self.db_session_maker()
            try:
                task = db.query(Task).filter(Task.id == task_id).first()
                if not task:
                    return False
                
                if task.status in ["SUCCESS", "FAILED", "CANCELLED"]:
                    return False
                
                # Cancel if running
                if task_id in self.running_tasks:
                    self.running_tasks[task_id].cancel()
                
                # Update status
                task.status = "CANCELLED"
                task.completed_at = datetime.utcnow()
                db.commit()
                
                return True
            finally:
                db.close()
        else:
            with get_db() as db:
                task = db.query(Task).filter(Task.id == task_id).first()
                if not task:
                    return False
                
                if task.status in ["SUCCESS", "FAILED", "CANCELLED"]:
                    return False
                
                # Cancel if running
                if task_id in self.running_tasks:
                    self.running_tasks[task_id].cancel()
                
                # Update status
                task.status = "CANCELLED"
                task.completed_at = datetime.utcnow()
                db.commit()
                
                return True
    
    async def retry_task(self, task_id: str) -> Optional[str]:
        """Retry a failed task"""
        if self.db_session_maker:
            db = self.db_session_maker()
            try:
                task = db.query(Task).filter(Task.id == task_id).first()
                if not task or task.status != "FAILED":
                    return None
                
                # Get original parameters
                parameters = json.loads(task.parameters) if task.parameters else {}
            finally:
                db.close()
        else:
            with get_db() as db:
                task = db.query(Task).filter(Task.id == task_id).first()
                if not task or task.status != "FAILED":
                    return None
                
                # Get original parameters
                parameters = json.loads(task.parameters) if task.parameters else {}
        
        # Submit new task
        new_task_id = await self.submit_task(task.task_type, parameters)
        
        return new_task_id


# Global task queue instance
task_queue = TaskQueue()

