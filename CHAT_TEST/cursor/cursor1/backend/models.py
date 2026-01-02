"""
Database models for the chat system
Uses SQLAlchemy for ORM and SQLite for persistence
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

# SQLAlchemy setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./chat.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models (SQLAlchemy)

class ChatRoomModel(Base):
    """Chat room database model"""
    __tablename__ = "chat_rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(String(500), default="")
    created_at = Column(DateTime, default=datetime.utcnow)

class MessageModel(Base):
    """Message database model"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("chat_rooms.id"), nullable=False, index=True)
    username = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

# Pydantic Models (API Schemas)

class RoomCreate(BaseModel):
    """Schema for creating a new room"""
    name: str
    description: Optional[str] = None

class ChatRoom(BaseModel):
    """Schema for chat room response"""
    id: int
    name: str
    description: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class MessageCreate(BaseModel):
    """Schema for creating a new message"""
    username: str
    content: str

class Message(BaseModel):
    """Schema for message response"""
    id: int
    room_id: int
    username: str
    content: str
    timestamp: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Database utilities

def init_db():
    """Initialize the database tables"""
    Base.metadata.create_all(bind=engine)

def get_db_session() -> Session:
    """Get a database session"""
    return SessionLocal()

