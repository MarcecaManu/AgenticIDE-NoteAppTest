import sqlite3

def read_full_database():
    conn = sqlite3.connect('backend/users.db')
    cursor = conn.cursor()
    
    # Query all data from users table
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    
    print("\nDatabase contents:")
    print("-" * 50)
    print("Username | Password Hash")
    print("-" * 50)
    
    for user in users:
        print(f"{user[0]} | {user[1]}")
    
    conn.close()

if _name_ == "_main_":
    read_full_database()