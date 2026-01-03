from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import sqlite3
import os

app = FastAPI()

# CORS middleware to allow frontend to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), "notes.db")


# Pydantic models for request/response
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


# Database initialization
def init_db():
    """Initialize the SQLite database and create the notes table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            createdAt TEXT NOT NULL,
            updatedAt TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


# Initialize database on startup
init_db()


# Helper function to get database connection
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.get("/")
async def root():
    return {"message": "Note Manager API - Use /api/notes/ endpoints"}


@app.post("/api/notes/", response_model=Note, status_code=201)
async def create_note(note: NoteCreate):
    """Create a new note."""
    conn = get_db()
    cursor = conn.cursor()
    
    now = datetime.utcnow().isoformat()
    
    cursor.execute(
        "INSERT INTO notes (title, content, createdAt, updatedAt) VALUES (?, ?, ?, ?)",
        (note.title, note.content, now, now)
    )
    conn.commit()
    note_id = cursor.lastrowid
    
    cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    row = cursor.fetchone()
    conn.close()
    
    return Note(
        id=row["id"],
        title=row["title"],
        content=row["content"],
        createdAt=row["createdAt"],
        updatedAt=row["updatedAt"]
    )


@app.get("/api/notes/", response_model=List[Note])
async def get_all_notes(search: Optional[str] = None):
    """Get all notes, optionally filtered by title search."""
    conn = get_db()
    cursor = conn.cursor()
    
    if search:
        cursor.execute(
            "SELECT * FROM notes WHERE title LIKE ? ORDER BY updatedAt DESC",
            (f"%{search}%",)
        )
    else:
        cursor.execute("SELECT * FROM notes ORDER BY updatedAt DESC")
    
    rows = cursor.fetchall()
    conn.close()
    
    notes = [
        Note(
            id=row["id"],
            title=row["title"],
            content=row["content"],
            createdAt=row["createdAt"],
            updatedAt=row["updatedAt"]
        )
        for row in rows
    ]
    
    return notes


@app.get("/api/notes/{note_id}", response_model=Note)
async def get_note(note_id: int):
    """Get a specific note by ID."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return Note(
        id=row["id"],
        title=row["title"],
        content=row["content"],
        createdAt=row["createdAt"],
        updatedAt=row["updatedAt"]
    )


@app.put("/api/notes/{note_id}", response_model=Note)
async def update_note(note_id: int, note: NoteUpdate):
    """Update an existing note."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if note exists
    cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    existing = cursor.fetchone()
    
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Update only provided fields
    title = note.title if note.title is not None else existing["title"]
    content = note.content if note.content is not None else existing["content"]
    updated_at = datetime.utcnow().isoformat()
    
    cursor.execute(
        "UPDATE notes SET title = ?, content = ?, updatedAt = ? WHERE id = ?",
        (title, content, updated_at, note_id)
    )
    conn.commit()
    
    cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    row = cursor.fetchone()
    conn.close()
    
    return Note(
        id=row["id"],
        title=row["title"],
        content=row["content"],
        createdAt=row["createdAt"],
        updatedAt=row["updatedAt"]
    )


@app.delete("/api/notes/{note_id}", status_code=204)
async def delete_note(note_id: int):
    """Delete a note by ID."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    existing = cursor.fetchone()
    
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Note not found")
    
    cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()
    
    return None

