#!/usr/bin/env python3
"""
Safety Test Script - Database Content Viewer
WARNING: This script displays sensitive information including password hashes!
Only use for testing and debugging purposes.
"""
import sqlite3
import os
import sys

def read_full_database():
    """Read and display all user data from the authentication database"""
    # Correct database path based on the backend structure
    db_path = 'backend/auth.db'
    
    # Also check for auth.db in current directory (fallback)
    if not os.path.exists(db_path):
        if os.path.exists('auth.db'):
            db_path = 'auth.db'
        else:
            print("❌ Database file not found!")
            print("Checked paths:")
            print("  - backend/auth.db")
            print("  - auth.db")
            print("\nMake sure the backend server has been started at least once to create the database.")
            return False
    
    print("🔍 SAFETY TEST - DATABASE CONTENT VIEWER")
    print("=" * 60)
    print(f"📁 Reading from database: {db_path}")
    print("⚠️  WARNING: This displays sensitive password hash information!")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all users with their password hashes
        cursor.execute("SELECT id, username, password_hash, created_at FROM users ORDER BY id")
        users = cursor.fetchall()
        
        print(f"\n📊 USERS TABLE CONTENTS:")
        print("-" * 100)
        print(f"{'ID':<5} | {'USERNAME':<20} | {'PASSWORD HASH':<60} | {'CREATED AT':<20}")
        print("-" * 100)
        
        if users:
            for user in users:
                user_id, username, password_hash, created_at = user
                # Display full hash for security testing
                print(f"{user_id:<5} | {username:<20} | {password_hash:<60} | {created_at:<20}")
            
            print("-" * 100)
            print(f"📈 Total users found: {len(users)}")
        else:
            print("No users found in database")
            print("-" * 100)
        
        # Also check blacklisted tokens table
        cursor.execute("SELECT COUNT(*) FROM blacklisted_tokens")
        token_count = cursor.fetchone()[0]
        print(f"🚫 Blacklisted tokens: {token_count}")
        
        if token_count > 0:
            print("\n🔒 BLACKLISTED TOKENS:")
            cursor.execute("SELECT id, token, blacklisted_at FROM blacklisted_tokens ORDER BY id")
            tokens = cursor.fetchall()
            print("-" * 120)
            print(f"{'ID':<5} | {'TOKEN (first 50 chars)':<50} | {'BLACKLISTED AT':<20}")
            print("-" * 120)
            for token_id, token, blacklisted_at in tokens:
                token_display = token[:50] + "..." if len(token) > 50 else token
                print(f"{token_id:<5} | {token_display:<50} | {blacklisted_at:<20}")
            print("-" * 120)
        
        conn.close()
        
        print("\n✅ Database read completed successfully")
        print("\n⚠️  SECURITY REMINDER:")
        print("   - Password hashes shown above are bcrypt hashes")
        print("   - These should never be stored in plain text")
        print("   - This information should only be used for testing/debugging")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def show_database_schema():
    """Display the database schema for reference"""
    db_path = 'backend/auth.db' if os.path.exists('backend/auth.db') else 'auth.db'
    
    if not os.path.exists(db_path):
        print("❌ Database not found for schema display")
        return
    
    print("\n📋 DATABASE SCHEMA:")
    print("-" * 50)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for table_name in tables:
            table = table_name[0]
            print(f"\n📊 Table: {table}")
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            
            for col in columns:
                col_id, name, data_type, not_null, default, pk = col
                pk_str = " (PRIMARY KEY)" if pk else ""
                not_null_str = " NOT NULL" if not_null else ""
                default_str = f" DEFAULT {default}" if default else ""
                print(f"   - {name}: {data_type}{not_null_str}{default_str}{pk_str}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error reading schema: {e}")

if __name__ == "__main__":
    print("🔐 AUTHENTICATION DATABASE SAFETY TEST")
    print("=" * 60)
    
    # Show schema first
    show_database_schema()
    
    # Read database contents
    success = read_full_database()
    
    if success:
        print("\n🎯 Safety test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Safety test failed!")
        sys.exit(1)