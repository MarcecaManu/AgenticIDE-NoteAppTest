from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List
import database
import crud
from models import Note, NoteCreate, NoteUpdate
from pathlib import Path

# Initialize FastAPI app
app = FastAPI(title="Note Manager API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    database.init_db()


# API Endpoints - Define these BEFORE mounting static files

@app.get("/api/notes/", response_model=List[Note])
def get_all_notes():
    """Get all notes"""
    return crud.get_all_notes()


@app.get("/api/notes/{note_id}", response_model=Note)
def get_note(note_id: int):
    """Get a specific note by ID"""
    note = crud.get_note_by_id(note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found"
        )
    return note


@app.post("/api/notes/", response_model=Note, status_code=status.HTTP_201_CREATED)
def create_note(note: NoteCreate):
    """Create a new note"""
    return crud.create_note(note)


@app.put("/api/notes/{note_id}", response_model=Note)
def update_note(note_id: int, note: NoteUpdate):
    """Update an existing note"""
    updated_note = crud.update_note(note_id, note)
    if not updated_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found"
        )
    return updated_note


@app.delete("/api/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int):
    """Delete a note"""
    if not crud.delete_note(note_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found"
        )
    return None


# Mount frontend static files AFTER API routes
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    # Serve static files (CSS, JS)
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")
    
    # Serve index.html at root
    @app.get("/")
    def serve_frontend():
        return FileResponse(str(frontend_path / "index.html"))

