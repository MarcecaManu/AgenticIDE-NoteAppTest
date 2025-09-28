import sqlite3
import os

def read_full_database():
    # Use the correct backend database path
    db_path = 'backend/users.db'
    
    if not os.path.exists(db_path):
        print("Database file not found! Make sure the backend server has been started.")
        return
    
    print(f"Reading from database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Query all data from users table
    cursor.execute("SELECT id, username, hashed_password, created_at FROM users")
    users = cursor.fetchall()
    
    print("\nDatabase contents:")
    print("-" * 80)
    print("ID | Username | Password Hash | Created At")
    print("-" * 80)
    
    if users:
        for user in users:
            user_id, username, hashed_password, created_at = user
            # Truncate hash for display
            hash_display = hashed_password[:20] + "..." if len(hashed_password) > 20 else hashed_password
            print(f"{user_id} | {username} | {hash_display} | {created_at}")
    else:
        print("No users found in database")
    
    conn.close()

if __name__ == "__main__":
    read_full_database()