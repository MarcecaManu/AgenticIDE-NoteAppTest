"""
Database layer for chat application using SQLite with async support.
"""
import aiosqlite
import json
from datetime import datetime
from typing import List, Optional, Dict
from pathlib import Path


DB_PATH = Path(__file__).parent / "chat.db"


async def init_db():
    """Initialize the database with required tables."""
    async with aiosqlite.connect(DB_PATH) as db:
        # Create rooms table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS rooms (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        
        # Create messages table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                room_id TEXT NOT NULL,
                username TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (room_id) REFERENCES rooms (id) ON DELETE CASCADE
            )
        """)
        
        await db.commit()


class Database:
    """Database operations for chat system."""
    
    @staticmethod
    async def create_room(room_id: str, name: str) -> Dict:
        """Create a new chat room."""
        async with aiosqlite.connect(DB_PATH) as db:
            created_at = datetime.utcnow().isoformat()
            await db.execute(
                "INSERT INTO rooms (id, name, created_at) VALUES (?, ?, ?)",
                (room_id, name, created_at)
            )
            await db.commit()
            return {
                "id": room_id,
                "name": name,
                "created_at": created_at
            }
    
    @staticmethod
    async def get_all_rooms() -> List[Dict]:
        """Get all chat rooms."""
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM rooms ORDER BY created_at DESC") as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    @staticmethod
    async def get_room(room_id: str) -> Optional[Dict]:
        """Get a specific room by ID."""
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM rooms WHERE id = ?", (room_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
    
    @staticmethod
    async def delete_room(room_id: str) -> bool:
        """Delete a room and all its messages."""
        async with aiosqlite.connect(DB_PATH) as db:
            # Delete messages first
            await db.execute("DELETE FROM messages WHERE room_id = ?", (room_id,))
            # Delete room
            cursor = await db.execute("DELETE FROM rooms WHERE id = ?", (room_id,))
            await db.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    async def save_message(message_id: str, room_id: str, username: str, 
                          content: str, timestamp: str) -> Dict:
        """Save a message to the database."""
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT INTO messages (id, room_id, username, content, timestamp) VALUES (?, ?, ?, ?, ?)",
                (message_id, room_id, username, content, timestamp)
            )
            await db.commit()
            return {
                "id": message_id,
                "room_id": room_id,
                "username": username,
                "content": content,
                "timestamp": timestamp
            }
    
    @staticmethod
    async def get_messages(room_id: str, limit: int = 100) -> List[Dict]:
        """Get messages for a specific room."""
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM messages WHERE room_id = ? ORDER BY timestamp ASC LIMIT ?",
                (room_id, limit)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

