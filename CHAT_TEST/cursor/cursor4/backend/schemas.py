"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class RoomCreate(BaseModel):
    """Schema for creating a new room"""
    name: str = Field(..., min_length=1, max_length=100)


class RoomResponse(BaseModel):
    """Schema for room response"""
    id: int
    name: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    """Schema for creating a message"""
    username: str = Field(..., min_length=1, max_length=50)
    content: str = Field(..., min_length=1, max_length=1000)


class MessageResponse(BaseModel):
    """Schema for message response"""
    id: int
    room_id: int
    username: str
    content: str
    timestamp: datetime
    
    class Config:
        from_attributes = True


class WebSocketMessage(BaseModel):
    """Schema for WebSocket messages"""
    type: str  # "message", "join", "leave", "typing"
    username: Optional[str] = None
    content: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class RoomListResponse(BaseModel):
    """Schema for listing rooms"""
    rooms: List[RoomResponse]
    count: int

