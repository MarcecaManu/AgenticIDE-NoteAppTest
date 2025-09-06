from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List, Optional

from models import Note, NoteCreate, NoteUpdate
from database import Database

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = Database()

@app.post("/api/notes/", response_model=Note)
async def create_note(note: NoteCreate):
    return db.create_note(note.title, note.content)

@app.get("/api/notes/", response_model=List[Note])
async def get_notes(search: Optional[str] = None):
    notes = db.get_all_notes()
    if search:
        notes = [note for note in notes if search.lower() in note['title'].lower()]
    return notes

@app.get("/api/notes/{note_id}", response_model=Note)
async def get_note(note_id: int):
    note = db.get_note(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@app.put("/api/notes/{note_id}", response_model=Note)
async def update_note(note_id: int, note: NoteUpdate):
    updated_note = db.update_note(note_id, note.title, note.content)
    if updated_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return updated_note

@app.delete("/api/notes/{note_id}")
async def delete_note(note_id: int):
    if not db.delete_note(note_id):
        raise HTTPException(status_code=404, detail="Note not found")
    return {"message": "Note deleted"}
