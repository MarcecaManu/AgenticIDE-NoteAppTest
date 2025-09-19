from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    username: str
    id: int

class Token(BaseModel):
    access_token: str
    token_type: str

class User:
    def __init__(self, id: int, username: str, hashed_password: str):
        self.id = id
        self.username = username
        self.hashed_password = hashed_password
    
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "hashed_password": self.hashed_password
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(data["id"], data["username"], data["hashed_password"])