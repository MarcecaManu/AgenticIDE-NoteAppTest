"""
Script to check how passwords are stored in the database.
This verifies that passwords are properly hashed, not stored in plain text.
"""
import sqlite3
from pathlib import Path

# Path to the database
db_path = Path("backend") / "auth_database.db"

if not db_path.exists():
    print(f"❌ Database not found at {db_path}")
    print("Make sure the backend has been run at least once to create the database.")
    exit(1)

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Query all users
cursor.execute("SELECT id, username, hashed_password, created_at FROM users")
users = cursor.fetchall()

if not users:
    print("📭 No users found in the database.")
    print("Register a user first by running the backend and using the frontend.")
else:
    print(f"🔍 Found {len(users)} user(s) in the database:\n")
    print("=" * 80)
    
    for user_id, username, hashed_password, created_at in users:
        print(f"ID: {user_id}")
        print(f"Username: {username}")
        print(f"Hashed Password: {hashed_password}")
        print(f"Created At: {created_at}")
        print()
        
        # Verify it's a bcrypt hash
        if hashed_password.startswith("$2b$"):
            print("✅ Password is properly hashed with bcrypt!")
            print(f"   - Hash length: {len(hashed_password)} characters")
            print(f"   - Hash starts with: $2b$ (bcrypt identifier)")
            print(f"   - This is NOT the plain text password - it's secure!")
        else:
            print("⚠️  Warning: Password doesn't look like a bcrypt hash!")
        
        print("=" * 80)

conn.close()

print("\n💡 What you're seeing:")
print("   - The 'hashed_password' field contains a bcrypt hash")
print("   - Bcrypt hashes start with '$2b$' followed by cost factor and salt")
print("   - The original password CANNOT be recovered from this hash")
print("   - This is secure and follows best practices!")

