import sqlite3
import os
from typing import Optional, Dict, Any
from pathlib import Path

class Database:
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default to backend/auth.db relative to the backend directory
            backend_dir = Path(__file__).parent
            self.db_path = str(backend_dir / "auth.db")
        else:
            self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize the database with users and blacklisted_tokens tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create blacklisted tokens table for logout functionality
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS blacklisted_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    token TEXT UNIQUE NOT NULL,
                    blacklisted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def create_user(self, username: str, password_hash: str) -> bool:
        """Create a new user. Returns True if successful, False if username exists"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, password_hash)
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False
    
    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, password_hash, created_at FROM users WHERE username = ?",
                (username,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, created_at FROM users WHERE id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def blacklist_token(self, token: str) -> bool:
        """Add token to blacklist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR IGNORE INTO blacklisted_tokens (token) VALUES (?)",
                    (token,)
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return True  # Token already blacklisted, still success
    
    def is_token_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM blacklisted_tokens WHERE token = ?",
                (token,)
            )
            return cursor.fetchone() is not None
