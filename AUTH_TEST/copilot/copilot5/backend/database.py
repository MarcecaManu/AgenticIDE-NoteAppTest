import json
from typing import Dict

class UserDB:
    def __init__(self, file_path: str = "users.json"):
        self.file_path = file_path
        self.users: Dict = self._load_users()

    def _load_users(self) -> Dict:
        try:
            with open(self.file_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def _save_users(self):
        with open(self.file_path, "w") as f:
            json.dump(self.users, f)

    def get_user(self, username: str):
        return self.users.get(username)

    def create_user(self, username: str, hashed_password: str):
        if username in self.users:
            return False
        self.users[username] = {
            "username": username,
            "hashed_password": hashed_password,
            "id": len(self.users) + 1
        }
        self._save_users()
        return True

    def get_all_users(self):
        return list(self.users.values())
