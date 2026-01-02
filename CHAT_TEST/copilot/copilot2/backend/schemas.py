"""Pydantic schemas for request/response models."""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class RoomCreate(BaseModel):
    """Schema for creating a new chat room."""
    name: str


class RoomResponse(BaseModel):
    """Schema for chat room response."""
    id: int
    name: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Schema for message response."""
    id: int
    room_id: int
    username: str
    content: str
    timestamp: datetime
    
    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    """Schema for creating a message via WebSocket."""
    username: str
    content: str
    message_type: Optional[str] = "message"  # message, join, leave, typing
