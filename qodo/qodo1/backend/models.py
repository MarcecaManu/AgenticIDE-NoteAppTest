from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class NoteCreate(BaseModel):
    title: str
    content: str
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Sample Note",
                    "content": "This is a sample note content"
                }
            ]
        }
    }

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Updated Title",
                    "content": "Updated content"
                }
            ]
        }
    }

class Note(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "title": "Sample Note",
                    "content": "This is a sample note content",
                    "created_at": "2024-01-01T00:00:00",
                    "updated_at": "2024-01-01T00:00:00"
                }
            ]
        }
    }
