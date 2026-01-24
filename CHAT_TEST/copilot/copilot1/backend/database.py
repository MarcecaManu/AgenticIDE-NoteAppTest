"""Database models and operations for the chat system."""
import sqlite3
from datetime import datetime
from typing import List, Optional, Dict
import json
from contextlib import contextmanager


class Database:
    """Handles all database operations for the chat system."""
    
    def __init__(self, db_path: str = "chat.db"):
        self.db_path = db_path
        self.init_db()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def init_db(self):
        """Initialize database tables."""
        with self.get_connection() as conn:
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
                    FOREIGN KEY (room_id) REFERENCES rooms (id) ON DELETE CASCADE
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
    
    # Room operations
    def create_room(self, room_id: str, name: str) -> Dict:
        """Create a new chat room."""
        created_at = datetime.utcnow().isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO rooms (id, name, created_at) VALUES (?, ?, ?)",
                (room_id, name, created_at)
            )
        return {"id": room_id, "name": name, "created_at": created_at}
    
    def get_all_rooms(self) -> List[Dict]:
        """Get all chat rooms."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM rooms ORDER BY created_at DESC")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_room(self, room_id: str) -> Optional[Dict]:
        """Get a specific room by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM rooms WHERE id = ?", (room_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def delete_room(self, room_id: str) -> bool:
        """Delete a room and all its messages."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Delete messages first
            cursor.execute("DELETE FROM messages WHERE room_id = ?", (room_id,))
            # Delete room
            cursor.execute("DELETE FROM rooms WHERE id = ?", (room_id,))
            return cursor.rowcount > 0
    
    # Message operations
    def create_message(self, message_id: str, room_id: str, username: str, 
                      content: str, timestamp: str) -> Dict:
        """Create a new message."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO messages (id, room_id, username, content, timestamp) 
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
    
    def get_room_messages(self, room_id: str, limit: int = 100) -> List[Dict]:
        """Get all messages for a room."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT * FROM messages 
                   WHERE room_id = ? 
                   ORDER BY timestamp ASC 
                   LIMIT ?""",
                (room_id, limit)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_message(self, message_id: str) -> Optional[Dict]:
        """Get a specific message by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM messages WHERE id = ?", (message_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
