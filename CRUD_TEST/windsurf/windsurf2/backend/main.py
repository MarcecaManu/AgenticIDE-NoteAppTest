from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from tinydb import TinyDB, Query
from functools import lru_cache
import os

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@lru_cache()
def get_db():
    # Ensure the data directory exists
    os.makedirs("data", exist_ok=True)
    return TinyDB('data/notes.json')

def get_notes_table():
    return get_db().table('notes')

class NoteCreate(BaseModel):
    title: str
    content: str

class Note(NoteCreate):
    id: int
    created_at: str
    updated_at: str

@app.get("/api/notes/", response_model=List[Note])
async def get_notes(search: Optional[str] = None, notes=Depends(get_notes_table)):
    all_notes = notes.all()
    if search:
        Note = Query()
        # Use case-insensitive regex search
        import re
        all_notes = notes.search(Note.title.matches(f'.*{re.escape(search)}.*', flags=re.IGNORECASE))
    return all_notes

@app.get("/api/notes/{note_id}", response_model=Note)
async def get_note(note_id: int, notes=Depends(get_notes_table)):
    Note = Query()
    note = notes.get(Note.id == note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@app.post("/api/notes/", response_model=Note)
async def create_note(note: NoteCreate, notes=Depends(get_notes_table)):
    current_time = datetime.now().isoformat()
    new_note = {
        "id": len(notes) + 1,
        "title": note.title,
        "content": note.content,
        "created_at": current_time,
        "updated_at": current_time
    }
    notes.insert(new_note)
    return new_note

@app.put("/api/notes/{note_id}", response_model=Note)
async def update_note(note_id: int, note: NoteCreate, notes=Depends(get_notes_table)):
    Note = Query()
    existing_note = notes.get(Note.id == note_id)
    if existing_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    updated_note = {
        "id": note_id,
        "title": note.title,
        "content": note.content,
        "created_at": existing_note["created_at"],
        "updated_at": datetime.now().isoformat()
    }
    notes.update(updated_note, Note.id == note_id)
    return updated_note

@app.delete("/api/notes/{note_id}")
async def delete_note(note_id: int, notes=Depends(get_notes_table)):
    Note = Query()
    if not notes.remove(Note.id == note_id):
        raise HTTPException(status_code=404, detail="Note not found")
    return {"message": "Note deleted successfully"}
