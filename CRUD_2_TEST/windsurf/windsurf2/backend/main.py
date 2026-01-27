from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import sqlite3
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.join(os.path.dirname(__file__), "notes.db")

def init_db():
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

init_db()

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

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.post("/api/notes/", response_model=Note, status_code=201)
def create_note(note: NoteCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    
    cursor.execute(
        "INSERT INTO notes (title, content, createdAt, updatedAt) VALUES (?, ?, ?, ?)",
        (note.title, note.content, now, now)
    )
    conn.commit()
    note_id = cursor.lastrowid
    
    cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    row = cursor.fetchone()
    conn.close()
    
    return {
        "id": row["id"],
        "title": row["title"],
        "content": row["content"],
        "createdAt": row["createdAt"],
        "updatedAt": row["updatedAt"]
    }

@app.get("/api/notes/", response_model=list[Note])
def get_all_notes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes ORDER BY updatedAt DESC")
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {
            "id": row["id"],
            "title": row["title"],
            "content": row["content"],
            "createdAt": row["createdAt"],
            "updatedAt": row["updatedAt"]
        }
        for row in rows
    ]

@app.get("/api/notes/{note_id}", response_model=Note)
def get_note(note_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return {
        "id": row["id"],
        "title": row["title"],
        "content": row["content"],
        "createdAt": row["createdAt"],
        "updatedAt": row["updatedAt"]
    }

@app.put("/api/notes/{note_id}", response_model=Note)
def update_note(note_id: int, note_update: NoteUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    existing_note = cursor.fetchone()
    
    if existing_note is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Note not found")
    
    title = note_update.title if note_update.title is not None else existing_note["title"]
    content = note_update.content if note_update.content is not None else existing_note["content"]
    updated_at = datetime.now(timezone.utc).isoformat()
    
    cursor.execute(
        "UPDATE notes SET title = ?, content = ?, updatedAt = ? WHERE id = ?",
        (title, content, updated_at, note_id)
    )
    conn.commit()
    
    cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    row = cursor.fetchone()
    conn.close()
    
    return {
        "id": row["id"],
        "title": row["title"],
        "content": row["content"],
        "createdAt": row["createdAt"],
        "updatedAt": row["updatedAt"]
    }

@app.delete("/api/notes/{note_id}", status_code=204)
def delete_note(note_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    existing_note = cursor.fetchone()
    
    if existing_note is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Note not found")
    
    cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()
    
    return None
