from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json
import os
import uuid

app = FastAPI()

# CORS middleware to allow frontend requests
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
    id: str
    title: str
    content: str
    createdAt: str
    updatedAt: str

# Storage file path
STORAGE_FILE = "backend/notes.json"

# Helper functions for file-based storage
def load_notes() -> List[dict]:
    """Load notes from JSON file"""
    if not os.path.exists(STORAGE_FILE):
        return []
    try:
        with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_notes(notes: List[dict]):
    """Save notes to JSON file"""
    os.makedirs(os.path.dirname(STORAGE_FILE), exist_ok=True)
    with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
        json.dump(notes, f, indent=2, ensure_ascii=False)

# API Endpoints
@app.get("/api/notes/", response_model=List[Note])
def get_all_notes():
    """Get all notes"""
    notes = load_notes()
    return notes

@app.get("/api/notes/{note_id}", response_model=Note)
def get_note(note_id: str):
    """Get a specific note by ID"""
    notes = load_notes()
    for note in notes:
        if note["id"] == note_id:
            return note
    raise HTTPException(status_code=404, detail="Note not found")

@app.post("/api/notes/", response_model=Note, status_code=201)
def create_note(note: NoteCreate):
    """Create a new note"""
    notes = load_notes()
    
    new_note = {
        "id": str(uuid.uuid4()),
        "title": note.title,
        "content": note.content,
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat()
    }
    
    notes.append(new_note)
    save_notes(notes)
    
    return new_note

@app.put("/api/notes/{note_id}", response_model=Note)
def update_note(note_id: str, note_update: NoteUpdate):
    """Update an existing note"""
    notes = load_notes()
    
    for i, note in enumerate(notes):
        if note["id"] == note_id:
            if note_update.title is not None:
                notes[i]["title"] = note_update.title
            if note_update.content is not None:
                notes[i]["content"] = note_update.content
            notes[i]["updatedAt"] = datetime.now().isoformat()
            
            save_notes(notes)
            return notes[i]
    
    raise HTTPException(status_code=404, detail="Note not found")

@app.delete("/api/notes/{note_id}", status_code=204)
def delete_note(note_id: str):
    """Delete a note"""
    notes = load_notes()
    
    for i, note in enumerate(notes):
        if note["id"] == note_id:
            notes.pop(i)
            save_notes(notes)
            return
    
    raise HTTPException(status_code=404, detail="Note not found")

# Serve frontend static files
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

