"""
Database models for task queue system
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Integer, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Task(Base):
    """Task model representing a background job"""
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, index=True)
    task_type = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False, default="PENDING", index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    result_data = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    progress = Column(Float, default=0.0, nullable=False)
    parameters = Column(Text, nullable=True)

    def to_dict(self):
        """Convert task to dictionary"""
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
            "parameters": self.parameters
        }

