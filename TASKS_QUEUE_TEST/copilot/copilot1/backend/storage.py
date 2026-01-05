"""Persistent storage for tasks using JSON file."""
import json
import os
from typing import Dict, List, Optional
from pathlib import Path
from .models import Task, TaskStatus, TaskType


class TaskStorage:
    """Handles persistent storage of tasks."""
    
    def __init__(self, storage_path: str = "data/tasks.json"):
        self.storage_path = storage_path
        self._ensure_storage_dir()
        self.tasks: Dict[str, Task] = {}
        self._load_tasks()
    
    def _ensure_storage_dir(self):
        """Ensure storage directory exists."""
        Path(self.storage_path).parent.mkdir(parents=True, exist_ok=True)
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, 'w') as f:
                json.dump([], f)
    
    def _load_tasks(self):
        """Load tasks from storage."""
        try:
            with open(self.storage_path, 'r') as f:
                tasks_data = json.load(f)
                for task_data in tasks_data:
                    task = Task.from_dict(task_data)
                    self.tasks[task.id] = task
        except (FileNotFoundError, json.JSONDecodeError):
            self.tasks = {}
    
    def _save_tasks(self):
        """Save tasks to storage."""
        tasks_data = [task.to_dict() for task in self.tasks.values()]
        with open(self.storage_path, 'w') as f:
            json.dump(tasks_data, f, indent=2)
    
    def add_task(self, task: Task):
        """Add a new task."""
        self.tasks[task.id] = task
        self._save_tasks()
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[Task]:
        """Get all tasks."""
        return list(self.tasks.values())
    
    def update_task(self, task: Task):
        """Update an existing task."""
        if task.id in self.tasks:
            self.tasks[task.id] = task
            self._save_tasks()
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task."""
        if task_id in self.tasks:
            del self.tasks[task_id]
            self._save_tasks()
            return True
        return False
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get tasks by status."""
        return [task for task in self.tasks.values() if task.status == status]
    
    def get_tasks_by_type(self, task_type: TaskType) -> List[Task]:
        """Get tasks by type."""
        return [task for task in self.tasks.values() if task.task_type == task_type]
