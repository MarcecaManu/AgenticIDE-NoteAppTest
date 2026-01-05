"""Database models and connection for the task queue system."""
import json
from datetime import datetime
from typing import Optional, List
from sqlalchemy import create_engine, Column, String, DateTime, Text, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import enum

DATABASE_URL = "sqlite:///./tasks.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class TaskStatus(str, enum.Enum):
    """Task status enumeration."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class TaskType(str, enum.Enum):
    """Task type enumeration."""
    DATA_PROCESSING = "DATA_PROCESSING"
    EMAIL_SIMULATION = "EMAIL_SIMULATION"
    IMAGE_PROCESSING = "IMAGE_PROCESSING"


class Task(Base):
    """Task model for persistent storage."""
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, index=True)
    task_type = Column(SQLEnum(TaskType), nullable=False)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    result_data = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    progress = Column(String, default="0", nullable=True)
    parameters = Column(Text, nullable=True)

    def to_dict(self):
        """Convert task to dictionary."""
        return {
            "id": self.id,
            "task_type": self.task_type.value if self.task_type else None,
            "status": self.status.value if self.status else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result_data": json.loads(self.result_data) if self.result_data else None,
            "error_message": self.error_message,
            "progress": self.progress,
            "parameters": json.loads(self.parameters) if self.parameters else None
        }


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


