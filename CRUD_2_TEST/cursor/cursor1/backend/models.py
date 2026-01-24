from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NoteBase(BaseModel):
    """Base model for note data"""
    title: str
    content: str


class NoteCreate(NoteBase):
    """Model for creating a new note"""
    pass


class NoteUpdate(NoteBase):
    """Model for updating an existing note"""
    pass


class Note(NoteBase):
    """Complete note model with all fields"""
    id: int
    createdAt: str
    updatedAt: str

    class Config:
        from_attributes = True

