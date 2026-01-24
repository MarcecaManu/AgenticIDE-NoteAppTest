from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json
import os
from pathlib import Path

app = FastAPI()

# CORS middleware to allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class NoteCreate(BaseModel):
    title: str
    content: str

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class Note(BaseModel):
    id: int
    title: str
    content: str
    createdAt: str
    updatedAt: str

# Persistent storage setup
DATA_FILE = Path(__file__).parent / "notes_data.json"

def load_notes() -> List[dict]:
    """Load notes from JSON file"""
    if not DATA_FILE.exists():
        return []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_notes(notes: List[dict]):
    """Save notes to JSON file"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(notes, f, indent=2, ensure_ascii=False)

def get_next_id(notes: List[dict]) -> int:
    """Get next available ID"""
    if not notes:
        return 1
    return max(note['id'] for note in notes) + 1

# API Endpoints

@app.get("/api/notes/", response_model=List[Note])
async def get_all_notes():
    """Get all notes"""
    notes = load_notes()
    return notes

@app.get("/api/notes/{note_id}", response_model=Note)
async def get_note(note_id: int):
    """Get a specific note by ID"""
    notes = load_notes()
    for note in notes:
        if note['id'] == note_id:
            return note
    raise HTTPException(status_code=404, detail="Note not found")

@app.post("/api/notes/", response_model=Note, status_code=201)
async def create_note(note: NoteCreate):
    """Create a new note"""
    notes = load_notes()
    now = datetime.now().isoformat()
    
    new_note = {
        "id": get_next_id(notes),
        "title": note.title,
        "content": note.content,
        "createdAt": now,
        "updatedAt": now
    }
    
    notes.append(new_note)
    save_notes(notes)
    
    return new_note

@app.put("/api/notes/{note_id}", response_model=Note)
async def update_note(note_id: int, note_update: NoteUpdate):
    """Update an existing note"""
    notes = load_notes()
    
    for i, note in enumerate(notes):
        if note['id'] == note_id:
            # Update only provided fields
            if note_update.title is not None:
                note['title'] = note_update.title
            if note_update.content is not None:
                note['content'] = note_update.content
            note['updatedAt'] = datetime.now().isoformat()
            
            notes[i] = note
            save_notes(notes)
            return note
    
    raise HTTPException(status_code=404, detail="Note not found")

@app.delete("/api/notes/{note_id}", status_code=204)
async def delete_note(note_id: int):
    """Delete a note"""
    notes = load_notes()
    
    for i, note in enumerate(notes):
        if note['id'] == note_id:
            notes.pop(i)
            save_notes(notes)
            return
    
    raise HTTPException(status_code=404, detail="Note not found")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Note Manager API"}
