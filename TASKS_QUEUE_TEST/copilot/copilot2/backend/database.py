"""
Database configuration and models for the Task Queue system.
Uses SQLAlchemy with SQLite for persistent storage.
"""

from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Create database directory if it doesn't exist
db_dir = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(db_dir, exist_ok=True)

DATABASE_URL = f"sqlite:///{os.path.join(db_dir, 'tasks.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class TaskDB(Base):
    """Database model for tasks"""
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, index=True)
    task_type = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False, index=True)  # PENDING, RUNNING, SUCCESS, FAILED, CANCELLED
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    result_data = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    progress = Column(Integer, default=0)  # 0-100
    input_data = Column(Text, nullable=True)  # Store task input parameters


def init_db():
    """Initialize the database"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
