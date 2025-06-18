from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, UTC
from typing import List, Optional
from pydantic import BaseModel
from . import models

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class NoteBase(BaseModel):
    title: str
    content: str

class NoteCreate(NoteBase):
    pass

class NoteResponse(NoteBase):
    id: int
    created_at: str
    updated_at: str

@app.get("/api/notes/", response_model=List[NoteResponse])
def get_notes():
    db = models.get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM notes ORDER BY created_at DESC")
    notes = cursor.fetchall()
    db.close()
    return notes

@app.get("/api/notes/{note_id}", response_model=NoteResponse)
def get_note(note_id: int):
    db = models.get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    note = cursor.fetchone()
    db.close()
    
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@app.post("/api/notes/", response_model=NoteResponse)
def create_note(note: NoteCreate):
    db = models.get_db()
    cursor = db.cursor()
    now = datetime.now(UTC).isoformat()
    cursor.execute(
        "INSERT INTO notes (title, content, created_at, updated_at) VALUES (?, ?, ?, ?)",
        (note.title, note.content, now, now)
    )
    note_id = cursor.lastrowid
    db.commit()
    
    # Fetch the created note
    cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    created_note = cursor.fetchone()
    db.close()
    return created_note

@app.put("/api/notes/{note_id}", response_model=NoteResponse)
def update_note(note_id: int, note: NoteCreate):
    db = models.get_db()
    cursor = db.cursor()
    
    # Check if note exists
    cursor.execute("SELECT id FROM notes WHERE id = ?", (note_id,))
    if cursor.fetchone() is None:
        db.close()
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Update the note
    now = datetime.now(UTC).isoformat()
    cursor.execute(
        "UPDATE notes SET title = ?, content = ?, updated_at = ? WHERE id = ?",
        (note.title, note.content, now, note_id)
    )
    db.commit()
    
    # Fetch the updated note
    cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    updated_note = cursor.fetchone()
    db.close()
    return updated_note

@app.delete("/api/notes/{note_id}")
def delete_note(note_id: int):
    db = models.get_db()
    cursor = db.cursor()
    
    # Check if note exists
    cursor.execute("SELECT id FROM notes WHERE id = ?", (note_id,))
    if cursor.fetchone() is None:
        db.close()
        raise HTTPException(status_code=404, detail="Note not found")
    
    cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    db.commit()
    db.close()
    return {"message": "Note deleted successfully"}