from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class MessageBase(BaseModel):
    username: str
    content: str


class MessageCreate(MessageBase):
    room_id: int


class Message(MessageBase):
    id: int
    room_id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class RoomBase(BaseModel):
    name: str


class RoomCreate(RoomBase):
    pass


class Room(RoomBase):
    id: int
    created_at: datetime
    messages: List[Message] = []

    class Config:
        from_attributes = True


class RoomList(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


class WebSocketMessage(BaseModel):
    type: str  # "message", "join", "leave", "typing", "user_list"
    username: Optional[str] = None
    content: Optional[str] = None
    timestamp: Optional[datetime] = None
    users: Optional[List[str]] = None
