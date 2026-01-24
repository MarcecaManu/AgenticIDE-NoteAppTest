"""Asyncio-based task queue manager."""
import asyncio
import uuid
import json
from datetime import datetime
from typing import Dict, Optional, List, Callable
from sqlalchemy.orm import Session

from database import Task, TaskStatus, TaskType, SessionLocal
from task_workers import get_worker


class TaskQueue:
    """Asyncio-based task queue manager."""
    
    def __init__(self, session_factory: Callable = None):
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.task_workers: Dict[str, object] = {}
        self.loop = None
        self.session_factory = session_factory or SessionLocal
    
    def start(self):
        """Start the task queue background processor."""
        if not self.loop:
            self.loop = asyncio.get_event_loop()
    
    def submit_task(self, task_type: str, parameters: Dict) -> str:
        """Submit a new task to the queue."""
        task_id = str(uuid.uuid4())
        
        # Create task in database
        db = self.session_factory()
        try:
            task = Task(
                id=task_id,
                task_type=TaskType[task_type],
                status=TaskStatus.PENDING,
                parameters=json.dumps(parameters)
            )
            db.add(task)
            db.commit()
        finally:
            db.close()
        
        # Start processing the task
        asyncio.create_task(self._process_task(task_id, task_type, parameters))
        
        return task_id
    
    async def _process_task(self, task_id: str, task_type: str, parameters: Dict):
        """Process a task asynchronously."""
        db = self.session_factory()
        try:
            # Update task status to RUNNING
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                return
            
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.utcnow()
            db.commit()
            
            # Create and execute worker
            worker = get_worker(task_type, task_id, parameters, self._update_progress)
            self.task_workers[task_id] = worker
            
            try:
                result = await worker.execute()
                
                # Update task with success (only if not cancelled)
                # Refresh task from DB to get latest status
                db.expire_all()
                task = db.query(Task).filter(Task.id == task_id).first()
                if task and task.status != TaskStatus.CANCELLED:
                    task.status = TaskStatus.SUCCESS
                    task.completed_at = datetime.utcnow()
                    task.result_data = json.dumps(result)
                    task.progress = "100"
                    db.commit()
                
            except Exception as e:
                # Update task with failure (only if not cancelled)
                # Refresh task from DB to get latest status
                db.expire_all()
                task = db.query(Task).filter(Task.id == task_id).first()
                if task and task.status != TaskStatus.CANCELLED:
                    task.status = TaskStatus.FAILED
                    task.completed_at = datetime.utcnow()
                    task.error_message = str(e)
                    db.commit()
            
            finally:
                # Clean up worker
                if task_id in self.task_workers:
                    del self.task_workers[task_id]
        
        finally:
            db.close()
    
    def _update_progress(self, task_id: str, progress: int):
        """Update task progress."""
        db = self.session_factory()
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if task:
                task.progress = str(progress)
                db.commit()
        finally:
            db.close()
    
    def get_task(self, task_id: str, db: Session) -> Optional[Task]:
        """Get a task by ID."""
        return db.query(Task).filter(Task.id == task_id).first()
    
    def get_all_tasks(self, db: Session, status: Optional[str] = None, 
                      task_type: Optional[str] = None) -> List[Task]:
        """Get all tasks, optionally filtered by status and type."""
        query = db.query(Task)
        
        if status:
            query = query.filter(Task.status == TaskStatus[status])
        
        if task_type:
            query = query.filter(Task.task_type == TaskType[task_type])
        
        return query.order_by(Task.created_at.desc()).all()
    
    def cancel_task(self, task_id: str, db: Session) -> bool:
        """Cancel a pending or running task."""
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return False
        
        if task.status in [TaskStatus.SUCCESS, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            return False
        
        # Update task status first
        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.utcnow()
        db.commit()
        
        # Then cancel the worker if it's running
        if task_id in self.task_workers:
            self.task_workers[task_id].cancel()
        
        return True
    
    def retry_task(self, task_id: str, db: Session) -> Optional[str]:
        """Retry a failed task."""
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task or task.status != TaskStatus.FAILED:
            return None
        
        # Create a new task with the same parameters
        parameters = json.loads(task.parameters) if task.parameters else {}
        new_task_id = self.submit_task(task.task_type.value, parameters)
        
        return new_task_id


# Global task queue instance
task_queue = TaskQueue()

