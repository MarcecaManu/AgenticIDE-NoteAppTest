"""
Pydantic models for request/response validation.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Union
from datetime import datetime
from enum import Enum


class TaskType(str, Enum):
    """Available task types"""
    DATA_PROCESSING = "data_processing"
    EMAIL_SIMULATION = "email_simulation"
    IMAGE_PROCESSING = "image_processing"


class TaskStatus(str, Enum):
    """Task execution statuses"""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class TaskSubmitRequest(BaseModel):
    """Request model for task submission"""
    task_type: str
    input_data: Optional[dict] = Field(default=None)
    parameters: Optional[dict] = Field(default=None)
    
    @field_validator('task_type')
    @classmethod
    def normalize_task_type(cls, v: str) -> str:
        """Accept both uppercase and lowercase task types"""
        v_lower = v.lower()
        valid_types = ['data_processing', 'email_simulation', 'image_processing']
        if v_lower not in valid_types:
            raise ValueError(f"Input should be 'data_processing', 'email_simulation' or 'image_processing'")
        return v_lower
    
    def get_input_data(self) -> dict:
        """Get input data from either input_data or parameters field"""
        data = self.input_data or self.parameters or {}
        
        # Normalize parameter names for compatibility
        normalized = {}
        param_mapping = {
            'num_rows': 'rows',
            'rows': 'rows',
            'processing_time': 'processing_time',
            'num_emails': 'recipient_count',
            'recipient_count': 'recipient_count',
            'delay_per_email': 'delay_per_email',
            'subject': 'subject',
            'num_images': 'image_count',
            'image_count': 'image_count',
            'target_size': 'target_size',
            'output_format': 'operation',
            'operation': 'operation'
        }
        
        for key, value in data.items():
            normalized_key = param_mapping.get(key, key)
            normalized[normalized_key] = value
        
        return normalized


class TaskResponse(BaseModel):
    """Response model for task data"""
    id: str
    task_type: str
    status: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result_data: Optional[str] = None
    error_message: Optional[str] = None
    progress: int = 0

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Response model for task list"""
    tasks: list[TaskResponse]
    total: int


class TaskRetryResponse(BaseModel):
    """Response model for task retry"""
    new_task_id: str
    message: str
