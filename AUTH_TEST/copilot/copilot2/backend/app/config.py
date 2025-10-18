from pydantic import BaseModel
from typing import Optional

# JWT Settings
SECRET_KEY = "your-secret-key-keep-it-secret"  # In production, use environment variables
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database path
DB_PATH = "users.json"

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    hashed_password: str

class UserCreate(BaseModel):
    username: str
    password: str

class UserInDB(User):
    pass

class UserProfile(BaseModel):
    username: str
