import json
import os
from typing import Dict, List, Optional
from datetime import datetime, timezone
from models import Task, TaskStatus
import asyncio

class TaskStorage:
    def __init__(self, storage_file: str = "tasks_data.json"):
        self.storage_file = storage_file
        self.tasks: Dict[str, Task] = {}
        self.lock = asyncio.Lock()
        self._load_tasks()
    
    def _load_tasks(self):
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    for task_id, task_data in data.items():
                        # Parse datetime and ensure it's timezone-aware
                        created_at = datetime.fromisoformat(task_data['created_at'])
                        if created_at.tzinfo is None:
                            created_at = created_at.replace(tzinfo=timezone.utc)
                        task_data['created_at'] = created_at
                        
                        if task_data.get('started_at'):
                            started_at = datetime.fromisoformat(task_data['started_at'])
                            if started_at.tzinfo is None:
                                started_at = started_at.replace(tzinfo=timezone.utc)
                            task_data['started_at'] = started_at
                            
                        if task_data.get('completed_at'):
                            completed_at = datetime.fromisoformat(task_data['completed_at'])
                            if completed_at.tzinfo is None:
                                completed_at = completed_at.replace(tzinfo=timezone.utc)
                            task_data['completed_at'] = completed_at
                            
                        self.tasks[task_id] = Task(**task_data)
            except Exception as e:
                print(f"Error loading tasks: {e}")
                self.tasks = {}
    
    async def _save_tasks(self):
        async with self.lock:
            try:
                data = {}
                for task_id, task in self.tasks.items():
                    task_dict = task.model_dump()
                    task_dict['created_at'] = task.created_at.isoformat()
                    if task.started_at:
                        task_dict['started_at'] = task.started_at.isoformat()
                    if task.completed_at:
                        task_dict['completed_at'] = task.completed_at.isoformat()
                    data[task_id] = task_dict
                
                with open(self.storage_file, 'w') as f:
                    json.dump(data, f, indent=2)
            except Exception as e:
                print(f"Error saving tasks: {e}")
    
    async def create_task(self, task: Task) -> Task:
        self.tasks[task.id] = task
        await self._save_tasks()
        return task
    
    async def get_task(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)
    
    async def get_all_tasks(self) -> List[Task]:
        return list(self.tasks.values())
    
    async def update_task(self, task_id: str, task: Task) -> Optional[Task]:
        if task_id in self.tasks:
            self.tasks[task_id] = task
            await self._save_tasks()
            return task
        return None
    
    async def delete_task(self, task_id: str) -> bool:
        if task_id in self.tasks:
            del self.tasks[task_id]
            await self._save_tasks()
            return True
        return False
    
    async def update_task_status(self, task_id: str, status: TaskStatus, 
                                 started_at: Optional[datetime] = None,
                                 completed_at: Optional[datetime] = None,
                                 result_data: Optional[Dict] = None,
                                 error_message: Optional[str] = None,
                                 progress: Optional[int] = None) -> Optional[Task]:
        task = self.tasks.get(task_id)
        if task:
            task.status = status
            if started_at:
                task.started_at = started_at
            if completed_at:
                task.completed_at = completed_at
            if result_data is not None:
                task.result_data = result_data
            if error_message is not None:
                task.error_message = error_message
            if progress is not None:
                task.progress = progress
            await self._save_tasks()
            return task
        return None
