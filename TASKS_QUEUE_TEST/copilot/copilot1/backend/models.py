"""Data models for task queue system."""
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Task status enumeration."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class TaskType(str, Enum):
    """Task type enumeration."""
    DATA_PROCESSING = "DATA_PROCESSING"
    EMAIL_SIMULATION = "EMAIL_SIMULATION"
    IMAGE_PROCESSING = "IMAGE_PROCESSING"


class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    task_type: TaskType
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)


class TaskResponse(BaseModel):
    """Schema for task response."""
    id: str
    task_type: TaskType
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    progress: Optional[float] = 0.0  # 0.0 to 100.0


class Task:
    """Internal task representation."""
    
    def __init__(
        self,
        task_id: str,
        task_type: TaskType,
        parameters: Optional[Dict[str, Any]] = None
    ):
        self.id = task_id
        self.task_type = task_type
        self.status = TaskStatus.PENDING
        self.parameters = parameters or {}
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.result_data: Optional[Dict[str, Any]] = None
        self.error_message: Optional[str] = None
        self.progress: float = 0.0
        
    def to_response(self) -> TaskResponse:
        """Convert to response schema."""
        return TaskResponse(
            id=self.id,
            task_type=self.task_type,
            status=self.status,
            created_at=self.created_at,
            started_at=self.started_at,
            completed_at=self.completed_at,
            result_data=self.result_data,
            error_message=self.error_message,
            progress=self.progress
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for persistence."""
        return {
            'id': self.id,
            'task_type': self.task_type.value,
            'status': self.status.value,
            'parameters': self.parameters,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'result_data': self.result_data,
            'error_message': self.error_message,
            'progress': self.progress
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create task from dictionary."""
        task = cls(
            task_id=data['id'],
            task_type=TaskType(data['task_type']),
            parameters=data.get('parameters', {})
        )
        task.status = TaskStatus(data['status'])
        task.created_at = datetime.fromisoformat(data['created_at'])
        task.started_at = datetime.fromisoformat(data['started_at']) if data.get('started_at') else None
        task.completed_at = datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None
        task.result_data = data.get('result_data')
        task.error_message = data.get('error_message')
        task.progress = data.get('progress', 0.0)
        return task
