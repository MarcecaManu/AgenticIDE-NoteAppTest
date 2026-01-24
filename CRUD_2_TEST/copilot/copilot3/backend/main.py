from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional
from database import Database

app = FastAPI()

# Configure CORS to allow frontend to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
db = Database()


class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, description="Note title must not be empty")
    content: str


class NoteUpdate(BaseModel):
    title: str = Field(..., min_length=1, description="Note title must not be empty")
    content: str


@app.get("/api/notes/")
def get_all_notes():
    """Get all notes"""
    notes = db.get_all_notes()
    return notes


@app.get("/api/notes/{note_id}")
def get_note(note_id: int):
    """Get a specific note by ID"""
    note = db.get_note_by_id(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@app.post("/api/notes/", status_code=201)
def create_note(note: NoteCreate):
    """Create a new note"""
    created_note = db.create_note(note.title, note.content)
    return created_note


@app.put("/api/notes/{note_id}")
def update_note(note_id: int, note: NoteUpdate):
    """Update an existing note"""
    updated_note = db.update_note(note_id, note.title, note.content)
    if updated_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return updated_note


@app.delete("/api/notes/{note_id}", status_code=204)
def delete_note(note_id: int):
    """Delete a note"""
    deleted = db.delete_note(note_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Note not found")
    return None


@app.get("/")
def read_root():
    """Root endpoint"""
    return {"message": "Note Manager API is running"}
