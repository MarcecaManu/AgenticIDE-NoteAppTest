# safety_test.py - Print all usernames and passwords from the database
import sqlite3
import os
from datetime import datetime

def read_full_database():
    """Read and display all user data from the authentication database"""
    db_path = 'backend/auth_app.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        print("Make sure the backend has been started at least once to create the database.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get table info to understand the structure
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        print(f"\n📊 Database: {db_path}")
        print(f"🕒 Accessed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n📋 Table structure:")
        for col in columns:
            print(f"   {col[1]} ({col[2]})")
        
        # Query all data from users table
        cursor.execute("SELECT id, username, hashed_password, created_at FROM users")
        users = cursor.fetchall()
        
        print(f"\n👥 Total users in database: {len(users)}")
        print("=" * 80)
        
        if users:
            print(f"{'ID':<5} | {'Username':<30} | {'Password Hash':<60} | {'Created At'}")
            print("-" * 80)
            
            for user in users:
                user_id, username, password_hash, created_at = user
                # Truncate very long hashes for display
                display_hash = password_hash[:50] + "..." if len(password_hash) > 50 else password_hash
                created_display = created_at if created_at else "N/A"
                print(f"{user_id:<5} | {username:<30} | {display_hash:<60} | {created_display}")
            
            print("\n🔒 Security Note:")
            print("- The passwords shown above are bcrypt hashes, not plain text")
            print("- Bcrypt hashes include salt and are computationally expensive to crack")
            print("- Each hash represents the original password processed with bcrypt")
            
            # Show some hash details
            if users:
                sample_hash = users[0][2]
                print(f"\n📝 Hash format example: {sample_hash[:29]}...")
                print("   - $2b$: bcrypt algorithm identifier")
                print("   - Next 2 chars: cost factor (work factor)")
                print("   - Next 22 chars: salt")
                print("   - Remaining: actual hash value")
                
        else:
            print("📭 No users found in the database.")
            print("💡 Try running the API tests or registering users through the frontend first.")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def check_database_exists():
    """Check if the database file exists and show its location"""
    db_path = 'backend/auth_app.db'
    abs_path = os.path.abspath(db_path)
    
    print(f"🔍 Looking for database at: {abs_path}")
    
    if os.path.exists(db_path):
        file_size = os.path.getsize(db_path)
        mod_time = datetime.fromtimestamp(os.path.getmtime(db_path))
        print(f"✅ Database found! Size: {file_size} bytes, Modified: {mod_time}")
        return True
    else:
        print("❌ Database file not found.")
        print("💡 Start the backend server first to create the database:")
        print("   cd backend && python main.py")
        return False

if __name__ == "__main__":
    print("🔐 Authentication Database Safety Test")
    print("=" * 50)
    
    if check_database_exists():
        read_full_database()
    
    print("\n⚠️  WARNING: This tool shows sensitive data!")
    print("   Only use for testing and debugging purposes.")
    print("   Never expose password hashes in production!")