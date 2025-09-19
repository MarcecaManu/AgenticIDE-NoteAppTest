from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import json
import os
from typing import Optional

# FastAPI app initialization
app = FastAPI(title="Authentication API", version="1.0.0")

# CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security configuration
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token security
security = HTTPBearer()

# User storage file
USERS_FILE = "users.json"

# Pydantic models
class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserProfile(BaseModel):
    username: str
    created_at: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Utility functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def load_users():
    """Load users from JSON file."""
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_users(users_dict):
    """Save users to JSON file."""
    with open(USERS_FILE, 'w') as f:
        json.dump(users_dict, f, indent=2)

def get_user(username: str):
    """Get user from storage."""
    users = load_users()
    return users.get(username)

def create_user(username: str, password: str):
    """Create a new user."""
    users = load_users()
    if username in users:
        return None
    
    hashed_password = get_password_hash(password)
    user_data = {
        "username": username,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow().isoformat()
    }
    users[username] = user_data
    save_users(users)
    return user_data

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user

# Global blacklist for logout (in production, use Redis or database)
token_blacklist = set()

def is_token_blacklisted(token: str) -> bool:
    """Check if token is blacklisted."""
    return token in token_blacklist

def blacklist_token(token: str):
    """Add token to blacklist."""
    token_blacklist.add(token)

# Enhanced current user dependency that checks blacklist
def get_current_active_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user and check if token is blacklisted."""
    token = credentials.credentials
    
    # Check if token is blacklisted
    if is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been invalidated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user normally
    return get_current_user(credentials)

# API Endpoints
@app.post("/api/auth/register", response_model=dict)
async def register(user: UserRegister):
    """Register a new user."""
    # Validate input
    if not user.username or not user.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password are required"
        )
    
    if len(user.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long"
        )
    
    # Check if user already exists
    if get_user(user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create user
    created_user = create_user(user.username, user.password)
    if not created_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    
    return {"message": "User registered successfully", "username": user.username}

@app.post("/api/auth/login", response_model=Token)
async def login(user: UserLogin):
    """Authenticate user and return JWT token."""
    # Validate user credentials
    stored_user = get_user(user.username)
    if not stored_user or not verify_password(user.password, stored_user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/auth/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Logout user by blacklisting the token."""
    token = credentials.credentials
    
    # Check if token is valid before blacklisting
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # Blacklist the token
    blacklist_token(token)
    
    return {"message": "Successfully logged out"}

@app.get("/api/auth/profile", response_model=UserProfile)
async def get_profile(current_user: dict = Depends(get_current_active_user)):
    """Get current user profile."""
    return UserProfile(
        username=current_user["username"],
        created_at=current_user["created_at"]
    )

# Health check endpoint
@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Authentication API is running"}

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)