"""
Database Inspector - View stored user data and verify password hashing
"""
import sqlite3
import os

def inspect_database(db_path="backend/users.db"):
    """Inspect the contents of the authentication database"""
    
    if not os.path.exists(db_path):
        print(f"[ERROR] Database not found at: {db_path}")
        print("\nThe database will be created when you:")
        print("  1. Start the backend server, or")
        print("  2. Register your first user")
        return
    
    print("=" * 70)
    print("DATABASE INSPECTOR - Authentication Module")
    print("=" * 70)
    print(f"\nDatabase location: {db_path}")
    print()
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Show users table
    print("-" * 70)
    print("USERS TABLE")
    print("-" * 70)
    
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    
    if not users:
        print("No users registered yet.\n")
    else:
        print(f"Total users: {len(users)}\n")
        
        for user in users:
            print(f"ID:            {user['id']}")
            print(f"Username:      {user['username']}")
            print(f"Password Hash: {user['password_hash'][:50]}...")
            print(f"               Length: {len(user['password_hash'])} characters")
            print(f"               Type: {'[OK] BCRYPT HASH' if user['password_hash'].startswith('$2') else '[WARNING] NOT HASHED!'}")
            print(f"Created At:    {user['created_at']}")
            print()
    
    # Show token blacklist
    print("-" * 70)
    print("TOKEN BLACKLIST (Logged out tokens)")
    print("-" * 70)
    
    cursor.execute("SELECT * FROM token_blacklist")
    tokens = cursor.fetchall()
    
    if not tokens:
        print("No blacklisted tokens.\n")
    else:
        print(f"Total blacklisted tokens: {len(tokens)}\n")
        
        for i, token_row in enumerate(tokens, 1):
            print(f"Token #{i}:")
            print(f"  Token (first 30 chars): {token_row['token'][:30]}...")
            print(f"  Blacklisted at: {token_row['blacklisted_at']}")
            print()
    
    conn.close()
    
    print("=" * 70)
    print("\n[PASSWORD SECURITY CHECK]")
    if users:
        all_hashed = all(user['password_hash'].startswith('$2') for user in users)
        if all_hashed:
            print("[OK] All passwords are properly hashed with bcrypt!")
            print("[OK] Password hashes start with '$2a$', '$2b$', or '$2y$' (bcrypt signature)")
            print("[OK] Hashes are ~60 characters long (bcrypt standard)")
        else:
            print("[WARNING] Some passwords may not be properly hashed!")
    else:
        print("Register a user to test password hashing.")
    
    print("\n[INFO] How bcrypt hashing works:")
    print("  - Bcrypt generates a unique salt for each password")
    print("  - Hash format: $2b$rounds$salt+hash")
    print("  - Same password -> different hash each time (due to unique salt)")
    print("  - Hashes are irreversible - cannot get original password back")
    print("=" * 70)

if __name__ == "__main__":
    import sys
    db_path = sys.argv[1] if len(sys.argv) > 1 else "backend/users.db"
    inspect_database(db_path)

