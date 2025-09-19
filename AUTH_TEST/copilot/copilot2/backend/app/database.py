from tinydb import TinyDB, Query
from .config import DB_PATH, User

class Database:
    def __init__(self):
        self.db = TinyDB(DB_PATH)
        self.users = self.db.table('users')

    def get_user(self, username: str) -> User | None:
        UserQuery = Query()
        result = self.users.get(UserQuery.username == username)
        if result:
            return User(**result)
        return None

    def create_user(self, user: User) -> bool:
        if self.get_user(user.username):
            return False
        self.users.insert(user.dict())
        return True

    def update_user(self, username: str, user_data: dict) -> bool:
        User = Query()
        return self.users.update(user_data, User.username == username) != []

db = Database()
