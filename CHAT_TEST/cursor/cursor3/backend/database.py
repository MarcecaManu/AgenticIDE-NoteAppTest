"""
Database layer for the chat system using SQLite with persistent storage.
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
from contextlib import contextmanager
import os


DB_PATH = os.path.join(os.path.dirname(__file__), "chat.db")


@contextmanager
def get_db():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Initialize the database schema."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Create rooms table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rooms (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        
        # Create messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                room_id TEXT NOT NULL,
                username TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_room_id 
            ON messages(room_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_timestamp 
            ON messages(timestamp)
        """)


class ChatDatabase:
    """Database operations for the chat system."""
    
    @staticmethod
    def create_room(room_id: str, name: str) -> Dict:
        """Create a new chat room."""
        created_at = datetime.utcnow().isoformat()
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO rooms (id, name, created_at) VALUES (?, ?, ?)",
                (room_id, name, created_at)
            )
        return {
            "id": room_id,
            "name": name,
            "created_at": created_at
        }
    
    @staticmethod
    def get_room(room_id: str) -> Optional[Dict]:
        """Get a room by ID."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM rooms WHERE id = ?",
                (room_id,)
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None
    
    @staticmethod
    def get_all_rooms() -> List[Dict]:
        """Get all chat rooms."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM rooms ORDER BY created_at DESC"
            )
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def delete_room(room_id: str) -> bool:
        """Delete a room and all its messages."""
        with get_db() as conn:
            cursor = conn.cursor()
            # Delete messages first
            cursor.execute("DELETE FROM messages WHERE room_id = ?", (room_id,))
            # Delete room
            cursor.execute("DELETE FROM rooms WHERE id = ?", (room_id,))
            return cursor.rowcount > 0
    
    @staticmethod
    def create_message(message_id: str, room_id: str, username: str, 
                      content: str, timestamp: str) -> Dict:
        """Create a new message."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO messages 
                   (id, room_id, username, content, timestamp) 
                   VALUES (?, ?, ?, ?, ?)""",
                (message_id, room_id, username, content, timestamp)
            )
        return {
            "id": message_id,
            "room_id": room_id,
            "username": username,
            "content": content,
            "timestamp": timestamp
        }
    
    @staticmethod
    def get_room_messages(room_id: str, limit: int = 100) -> List[Dict]:
        """Get messages for a room."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT * FROM messages 
                   WHERE room_id = ? 
                   ORDER BY timestamp DESC 
                   LIMIT ?""",
                (room_id, limit)
            )
            messages = [dict(row) for row in cursor.fetchall()]
            # Return in chronological order
            return list(reversed(messages))
    
    @staticmethod
    def get_message(message_id: str) -> Optional[Dict]:
        """Get a message by ID."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM messages WHERE id = ?",
                (message_id,)
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None

