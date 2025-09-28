import sqlite3
import os
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_test_users():
    # Ensure backend directory exists
    os.makedirs("backend", exist_ok=True)
    
    # Connect to database
    db_path = 'backend/users.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blacklisted_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT UNIQUE NOT NULL,
            blacklisted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Test users to create
    test_users = [
        ("testuser1", "password123"),
        ("alice", "securepass456"),
        ("bob", "mypassword789"),
        ("admin", "adminpass000")
    ]
    
    print("Creating test users...")
    
    for username, password in test_users:
        # Hash the password
        hashed_password = pwd_context.hash(password)
        
        try:
            cursor.execute(
                "INSERT INTO users (username, hashed_password) VALUES (?, ?)",
                (username, hashed_password)
            )
            print(f"✓ Created user: {username}")
        except sqlite3.IntegrityError:
            print(f"- User {username} already exists")
    
    conn.commit()
    conn.close()
    print(f"\nTest users created in {db_path}")

if __name__ == "__main__":
    create_test_users()
