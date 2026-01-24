"""
Pydantic models for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class RoomCreate(BaseModel):
    """Model for creating a new room."""
    name: str = Field(..., min_length=1, max_length=100, description="Room name")


class Room(BaseModel):
    """Model for room data."""
    id: str
    name: str
    created_at: str


class Message(BaseModel):
    """Model for message data."""
    id: str
    room_id: str
    username: str
    content: str
    timestamp: str


class MessageCreate(BaseModel):
    """Model for creating a new message via WebSocket."""
    username: str = Field(..., min_length=1, max_length=50)
    content: str = Field(..., min_length=1, max_length=1000)


class WebSocketMessage(BaseModel):
    """Model for WebSocket message protocol."""
    type: str  # "message", "join", "leave", "typing", "user_list"
    data: dict


class TypingIndicator(BaseModel):
    """Model for typing indicator."""
    username: str
    is_typing: bool

