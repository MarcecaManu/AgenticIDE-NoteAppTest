from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from tinydb import TinyDB, Query
import os

# Initialize FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure the data directory exists
os.makedirs("data", exist_ok=True)

# Initialize database
db = TinyDB("data/notes.json")
Note = Query()

class NoteCreate(BaseModel):
    title: str
    content: str

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: str
    updated_at: str

@app.get("/api/notes/", response_model=List[NoteResponse])
async def get_notes(search: Optional[str] = None):
    if search:
        notes = db.search(Note.title.search(search))
    else:
        notes = db.all()
    
    # Add document IDs to the response
    return [{**note, "id": note.doc_id} for note in notes]

@app.get("/api/notes/{note_id}", response_model=NoteResponse)
async def get_note(note_id: int):
    note = db.get(doc_id=note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return {**note, "id": note_id}

@app.post("/api/notes/", response_model=NoteResponse)
async def create_note(note: NoteCreate):
    now = datetime.utcnow().isoformat()
    new_note = {
        "title": note.title,
        "content": note.content,
        "created_at": now,
        "updated_at": now
    }
    note_id = db.insert(new_note)
    return {**new_note, "id": note_id}

@app.put("/api/notes/{note_id}", response_model=NoteResponse)
async def update_note(note_id: int, note: NoteUpdate):
    existing_note = db.get(doc_id=note_id)
    if not existing_note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    update_data = note.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow().isoformat()
    
    db.update(update_data, doc_ids=[note_id])
    updated_note = db.get(doc_id=note_id)
    return {**updated_note, "id": note_id}

@app.delete("/api/notes/{note_id}")
async def delete_note(note_id: int):
    if not db.get(doc_id=note_id):
        raise HTTPException(status_code=404, detail="Note not found")
    db.remove(doc_ids=[note_id])
    return {"message": "Note deleted successfully"} 