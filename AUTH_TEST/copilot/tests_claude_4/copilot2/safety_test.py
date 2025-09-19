import sqlite3

def read_full_database():
    conn = sqlite3.connect('backend/users.db')
    cursor = conn.cursor()
    
    # Query all data from users table
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    
    print("\nDatabase contents:")
    print("-" * 80)
    print(f"{'ID':<5} | {'Username':<20} | {'Password Hash':<50}")
    print("-" * 80)
    
    for user in users:
        print(f"{user[0]:<5} | {user[1]:<20} | {user[2]:<50}")
    
    conn.close()

if __name__ == "__main__":
    read_full_database()