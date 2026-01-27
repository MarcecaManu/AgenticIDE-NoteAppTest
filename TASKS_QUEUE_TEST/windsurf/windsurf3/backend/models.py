from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class TaskType(str, Enum):
    DATA_PROCESSING = "data_processing"
    EMAIL_SIMULATION = "email_simulation"
    IMAGE_PROCESSING = "image_processing"

class TaskSubmit(BaseModel):
    task_type: TaskType
    parameters: Dict[str, Any] = Field(default_factory=dict)

class Task(BaseModel):
    id: str
    task_type: TaskType
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    progress: int = 0

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class TaskResponse(BaseModel):
    id: str
    task_type: TaskType
    status: TaskStatus
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    progress: int = 0
