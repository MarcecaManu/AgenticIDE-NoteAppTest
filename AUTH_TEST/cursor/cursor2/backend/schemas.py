from pydantic import BaseModel, Field
from datetime import datetime


class UserRegister(BaseModel):
    """Schema for user registration"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=72)


class UserLogin(BaseModel):
    """Schema for user login"""
    username: str
    password: str


class Token(BaseModel):
    """Schema for authentication token response"""
    access_token: str
    token_type: str


class UserProfile(BaseModel):
    """Schema for user profile response"""
    id: int
    username: str
    created_at: datetime

    class Config:
        from_attributes = True


class Message(BaseModel):
    """Schema for generic message response"""
    message: str

