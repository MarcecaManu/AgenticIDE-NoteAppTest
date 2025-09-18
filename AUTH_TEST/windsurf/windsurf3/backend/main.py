from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta
from models import UserRegister, UserLogin, Token, UserProfile, Message
from auth import (
    authenticate_user, register_user, create_access_token, 
    get_current_user, logout_user, ACCESS_TOKEN_EXPIRE_MINUTES
)

app = FastAPI(title="Authentication API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

def get_token_from_credentials(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Extract token from Authorization header"""
    return credentials.credentials

@app.post("/api/auth/register", response_model=Message)
async def register(user: UserRegister):
    """Register a new user"""
    if len(user.username.strip()) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be at least 3 characters long"
        )
    
    if len(user.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long"
        )
    
    success = register_user(user.username.strip(), user.password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    return Message(message="User registered successfully")

@app.post("/api/auth/login", response_model=Token)
async def login(user: UserLogin):
    """Authenticate user and return JWT token"""
    authenticated_user = authenticate_user(user.username.strip(), user.password)
    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": authenticated_user["username"]}, 
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")

@app.get("/api/auth/profile", response_model=UserProfile)
async def get_profile(token: str = Depends(get_token_from_credentials)):
    """Get current user profile"""
    user = get_current_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return UserProfile(
        id=user["id"],
        username=user["username"],
        created_at=user["created_at"]
    )

@app.post("/api/auth/logout", response_model=Message)
async def logout(token: str = Depends(get_token_from_credentials)):
    """Logout user by blacklisting token"""
    success = logout_user(token)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to logout"
        )
    
    return Message(message="Successfully logged out")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Authentication API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
