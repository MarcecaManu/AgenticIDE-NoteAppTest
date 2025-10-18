import json
import os
from typing import Optional, List
from models import User

class FileDatabase:
    def __init__(self, db_file: str = "users.json"):
        self.db_file = db_file
        self.users = []
        self.next_id = 1
        self.load_users()
    
    def load_users(self):
        """Load users from JSON file"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f:
                    data = json.load(f)
                    self.users = [User.from_dict(user_data) for user_data in data.get('users', [])]
                    self.next_id = data.get('next_id', 1)
            except (json.JSONDecodeError, KeyError):
                self.users = []
                self.next_id = 1
    
    def save_users(self):
        """Save users to JSON file"""
        data = {
            'users': [user.to_dict() for user in self.users],
            'next_id': self.next_id
        }
        with open(self.db_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        for user in self.users:
            if user.username == username:
                return user
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        for user in self.users:
            if user.id == user_id:
                return user
        return None
    
    def create_user(self, username: str, hashed_password: str) -> User:
        """Create a new user"""
        user = User(self.next_id, username, hashed_password)
        self.users.append(user)
        self.next_id += 1
        self.save_users()
        return user
    
    def user_exists(self, username: str) -> bool:
        """Check if user exists"""
        return self.get_user_by_username(username) is not None

# Global database instance
db = FileDatabase()