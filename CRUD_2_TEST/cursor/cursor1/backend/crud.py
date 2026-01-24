from typing import List, Optional
from datetime import datetime
from database import get_db
from models import Note, NoteCreate, NoteUpdate


def get_all_notes() -> List[Note]:
    """Get all notes from the database"""
    with get_db() as conn:
        cursor = conn.execute("SELECT * FROM notes ORDER BY updatedAt DESC")
        rows = cursor.fetchall()
        return [
            Note(
                id=row["id"],
                title=row["title"],
                content=row["content"],
                createdAt=row["createdAt"],
                updatedAt=row["updatedAt"]
            )
            for row in rows
        ]


def get_note_by_id(note_id: int) -> Optional[Note]:
    """Get a specific note by ID"""
    with get_db() as conn:
        cursor = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
        row = cursor.fetchone()
        if row:
            return Note(
                id=row["id"],
                title=row["title"],
                content=row["content"],
                createdAt=row["createdAt"],
                updatedAt=row["updatedAt"]
            )
        return None


def create_note(note: NoteCreate) -> Note:
    """Create a new note"""
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO notes (title, content) VALUES (?, ?)",
            (note.title, note.content)
        )
        note_id = cursor.lastrowid
        # Fetch the newly created note from the same connection
        cursor = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
        row = cursor.fetchone()
        if row:
            return Note(
                id=row["id"],
                title=row["title"],
                content=row["content"],
                createdAt=row["createdAt"],
                updatedAt=row["updatedAt"]
            )
        return None


def update_note(note_id: int, note: NoteUpdate) -> Optional[Note]:
    """Update an existing note"""
    with get_db() as conn:
        cursor = conn.execute(
            """UPDATE notes 
               SET title = ?, content = ?, updatedAt = CURRENT_TIMESTAMP 
               WHERE id = ?""",
            (note.title, note.content, note_id)
        )
        if cursor.rowcount == 0:
            return None
        # Fetch the updated note from the same connection
        cursor = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
        row = cursor.fetchone()
        if row:
            return Note(
                id=row["id"],
                title=row["title"],
                content=row["content"],
                createdAt=row["createdAt"],
                updatedAt=row["updatedAt"]
            )
        return None


def delete_note(note_id: int) -> bool:
    """Delete a note by ID"""
    with get_db() as conn:
        cursor = conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        return cursor.rowcount > 0

