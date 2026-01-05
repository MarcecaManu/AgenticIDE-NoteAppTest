from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TaskSubmit(BaseModel):
    task_type: str
    input_params: Optional[dict] = None


class TaskResponse(BaseModel):
    id: str
    task_type: str
    status: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result_data: Optional[str] = None
    error_message: Optional[str] = None
    progress: float = 0.0
    input_params: Optional[str] = None

    class Config:
        from_attributes = True


class TaskList(BaseModel):
    tasks: list[TaskResponse]
    total: int

