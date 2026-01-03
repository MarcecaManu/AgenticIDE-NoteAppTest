import sqlite3
from datetime import datetime, UTC
from typing import List, Optional
import json


class Database:
    def __init__(self, db_path: str = "notes.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize the database with notes table"""
        conn = sqlite3.connect(self.db_path)
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
    
    def get_connection(self):
        """Get a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def create_note(self, title: str, content: str) -> dict:
        """Create a new note"""
        conn = self.get_connection()
        cursor = conn.cursor()
        now = datetime.now(UTC).isoformat()
        
        cursor.execute(
            "INSERT INTO notes (title, content, createdAt, updatedAt) VALUES (?, ?, ?, ?)",
            (title, content, now, now)
        )
        note_id = cursor.lastrowid
        conn.commit()
        
        cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
        note = dict(cursor.fetchone())
        conn.close()
        
        return note
    
    def get_all_notes(self) -> List[dict]:
        """Get all notes"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM notes ORDER BY updatedAt DESC")
        notes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return notes
    
    def get_note_by_id(self, note_id: int) -> Optional[dict]:
        """Get a note by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def update_note(self, note_id: int, title: str, content: str) -> Optional[dict]:
        """Update an existing note"""
        conn = self.get_connection()
        cursor = conn.cursor()
        now = datetime.now(UTC).isoformat()
        
        cursor.execute(
            "UPDATE notes SET title = ?, content = ?, updatedAt = ? WHERE id = ?",
            (title, content, now, note_id)
        )
        conn.commit()
        
        if cursor.rowcount == 0:
            conn.close()
            return None
        
        cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
        note = dict(cursor.fetchone())
        conn.close()
        
        return note
    
    def delete_note(self, note_id: int) -> bool:
        """Delete a note"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return deleted
