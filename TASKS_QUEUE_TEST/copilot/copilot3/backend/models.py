"""Database models for task queue system."""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


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


class Task(Base):
    """Task model for background processing."""
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, index=True)
    task_type = Column(String, nullable=False)
    status = Column(String, default=TaskStatus.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    result_data = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    progress = Column(Float, default=0.0)
    input_params = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)

    def to_dict(self):
        """Convert task to dictionary."""
        return {
            "id": self.id,
            "task_type": self.task_type,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result_data": self.result_data,
            "error_message": self.error_message,
            "progress": self.progress,
            "input_params": self.input_params,
            "retry_count": self.retry_count,
        }
