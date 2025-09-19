import sqlite3
import os
from typing import Optional, Dict, Any
from datetime import datetime

DATABASE_FILE = "users.db"

def get_db_connection():
    """Get a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
    return conn

def init_database():
    """Initialize the database with the users table."""
    conn = get_db_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create blacklisted tokens table for logout functionality
        conn.execute("""
            CREATE TABLE IF NOT EXISTS blacklisted_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token TEXT UNIQUE NOT NULL,
                blacklisted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
    finally:
        conn.close()

def create_user(username: str, hashed_password: str) -> Optional[int]:
    """Create a new user and return the user ID."""
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO users (username, hashed_password) VALUES (?, ?)",
            (username, hashed_password)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None  # Username already exists
    finally:
        conn.close()

def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """Get a user by username."""
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "SELECT id, username, hashed_password, created_at FROM users WHERE username = ?",
            (username,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Get a user by ID."""
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "SELECT id, username, created_at FROM users WHERE id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def blacklist_token(token: str) -> bool:
    """Add a token to the blacklist."""
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO blacklisted_tokens (token) VALUES (?)",
            (token,)
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def is_token_blacklisted(token: str) -> bool:
    """Check if a token is blacklisted."""
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "SELECT 1 FROM blacklisted_tokens WHERE token = ?",
            (token,)
        )
        return cursor.fetchone() is not None
    finally:
        conn.close()

def cleanup_old_tokens(days: int = 30):
    """Clean up old blacklisted tokens."""
    conn = get_db_connection()
    try:
        conn.execute(
            "DELETE FROM blacklisted_tokens WHERE blacklisted_at < datetime('now', '-{} days')".format(days)
        )
        conn.commit()
    finally:
        conn.close()