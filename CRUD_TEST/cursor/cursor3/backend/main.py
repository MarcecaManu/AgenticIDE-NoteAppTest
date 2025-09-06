from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import Note, NoteCreate, NoteUpdate
import database

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/notes/", response_model=Note)
async def create_note(note: NoteCreate):
    return database.create_note(note)

@app.get("/api/notes/", response_model=list[Note])
async def get_notes():
    return database.get_all_notes()

@app.get("/api/notes/{note_id}", response_model=Note)
async def get_note(note_id: int):
    note = database.get_note(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@app.put("/api/notes/{note_id}", response_model=Note)
async def update_note(note_id: int, note_update: NoteUpdate):
    updated_note = database.update_note(note_id, note_update)
    if updated_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return updated_note

@app.delete("/api/notes/{note_id}")
async def delete_note(note_id: int):
    if not database.delete_note(note_id):
        raise HTTPException(status_code=404, detail="Note not found")
    return {"message": "Note deleted successfully"} 