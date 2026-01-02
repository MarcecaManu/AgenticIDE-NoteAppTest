"""
Pydantic models for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RoomCreate(BaseModel):
    """Request model for creating a new room."""
    name: str = Field(..., min_length=1, max_length=100)


class Room(BaseModel):
    """Response model for a chat room."""
    id: str
    name: str
    created_at: str


class MessageCreate(BaseModel):
    """Request model for creating a message (via WebSocket)."""
    username: str = Field(..., min_length=1, max_length=50)
    content: str = Field(..., min_length=1, max_length=1000)


class Message(BaseModel):
    """Response model for a message."""
    id: str
    room_id: str
    username: str
    content: str
    timestamp: str


class WebSocketMessage(BaseModel):
    """WebSocket message format."""
    type: str  # 'message', 'join', 'leave', 'typing', 'user_list'
    username: Optional[str] = None
    content: Optional[str] = None
    message: Optional[Message] = None
    users: Optional[list] = None
    timestamp: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str

