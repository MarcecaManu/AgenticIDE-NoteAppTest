from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import timedelta

from database import engine, get_db, Base
from models import User
from schemas import UserRegister, UserLogin, Token, UserProfile, Message
from auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_user,
    invalidate_token,
    security,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Authentication API", version="1.0.0")

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/auth/register", response_model=UserProfile, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user with username and password.
    Password is hashed before storage.
    """
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Create new user with hashed password
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            username=user_data.username,
            hashed_password=hashed_password
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return new_user
    except HTTPException:
        # Re-raise HTTPException as-is
        raise
    except ValueError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except IntegrityError:
        # Handle duplicate username at database level
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@app.post("/api/auth/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate a user and return a JWT access token.
    """
    user = authenticate_user(db, user_data.username, user_data.password)
    if not user:
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


@app.post("/api/auth/logout", response_model=Message)
def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Invalidate the user session/token by adding it to blacklist.
    """
    token = credentials.credentials
    invalidate_token(token)
    return {"message": "Successfully logged out"}


@app.get("/api/auth/profile", response_model=UserProfile)
def get_profile(current_user: User = Depends(get_current_user)):
    """
    Return the current user profile (requires valid Authorization header with Bearer token).
    """
    return current_user


@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "Authentication API is running"}

