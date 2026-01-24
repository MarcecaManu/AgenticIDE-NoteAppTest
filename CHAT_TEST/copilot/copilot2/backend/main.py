"""Main FastAPI application with REST and WebSocket endpoints."""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Union
import json
import os
from datetime import datetime

from .database import get_db, init_db, ChatRoom, Message
from .schemas import RoomCreate, RoomResponse, MessageResponse, MessageCreate
from .connection_manager import ConnectionManager

app = FastAPI(title="Real-time Chat API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize connection manager
manager = ConnectionManager()

# Mount static files early
static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()


# REST API Endpoints

@app.post("/api/chat/rooms", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(room: RoomCreate, db: Session = Depends(get_db)):
    """Create a new chat room."""
    # Check if room already exists
    existing_room = db.query(ChatRoom).filter(ChatRoom.name == room.name).first()
    if existing_room:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Room '{room.name}' already exists"
        )
    
    # Create new room
    db_room = ChatRoom(name=room.name)
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room


@app.get("/api/chat/rooms", response_model=List[RoomResponse])
async def list_rooms(db: Session = Depends(get_db)):
    """List all chat rooms."""
    rooms = db.query(ChatRoom).all()
    return rooms


@app.get("/api/chat/rooms/{room_id}/messages", response_model=List[MessageResponse])
async def get_room_messages(room_id: str, db: Session = Depends(get_db)):
    """Get message history for a specific room."""
    # Validate room_id is an integer
    try:
        room_id_int = int(room_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with id {room_id} not found"
        )
    
    # Check if room exists
    room = db.query(ChatRoom).filter(ChatRoom.id == room_id_int).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with id {room_id} not found"
        )
    
    # Get messages ordered by timestamp
    messages = db.query(Message).filter(
        Message.room_id == room_id_int
    ).order_by(Message.timestamp.asc()).all()
    
    return messages


@app.delete("/api/chat/rooms/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(room_id: str, db: Session = Depends(get_db)):
    """Delete a room and all its messages."""
    # Validate room_id is an integer
    try:
        room_id_int = int(room_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with id {room_id} not found"
        )
    
    room = db.query(ChatRoom).filter(ChatRoom.id == room_id_int).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with id {room_id} not found"
        )
    
    db.delete(room)
    db.commit()
    return None


# WebSocket Endpoint

@app.websocket("/ws/chat/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: str,
    username: str,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time chat."""
    # Validate and convert room_id
    try:
        room_id_int = int(room_id)
    except ValueError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    # Verify room exists
    room = db.query(ChatRoom).filter(ChatRoom.id == room_id_int).first()
    if not room:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    # Connect user
    await manager.connect(websocket, room_id_int, username)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            message_type = message_data.get("message_type", "message")
            
            if message_type == "typing":
                # Broadcast typing indicator
                is_typing = message_data.get("is_typing", False)
                await manager.broadcast_typing(room_id_int, username, is_typing)
            
            elif message_type == "message":
                # Save message to database
                content = message_data.get("content", "")
                if content.strip():
                    db_message = Message(
                        room_id=room_id_int,
                        username=username,
                        content=content
                    )
                    db.add(db_message)
                    db.commit()
                    db.refresh(db_message)
                    
                    # Broadcast message to all connected clients
                    broadcast_data = {
                        "id": db_message.id,
                        "room_id": db_message.room_id,
                        "username": db_message.username,
                        "content": db_message.content,
                        "timestamp": db_message.timestamp.isoformat(),
                        "message_type": "message"
                    }
                    await manager.broadcast_message(room_id_int, broadcast_data)
    
    except WebSocketDisconnect:
        # Handle disconnection
        manager.disconnect(websocket, room_id_int, username)
        await manager.broadcast_system_message(
            room_id_int,
            f"{username} left the room",
            "leave",
            username
        )
        await manager.broadcast_user_list(room_id_int)
    
    except Exception as e:
        # Handle other errors
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, room_id_int, username)


@app.get("/")
async def root():
    """Root endpoint - serve frontend."""
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "index.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    return {
        "message": "Real-time Chat API",
        "version": "1.0.0",
        "endpoints": {
            "rest_api": "/api/chat/",
            "websocket": "/ws/chat/{room_id}?username={username}",
            "frontend": "/chat"
        }
    }


@app.get("/chat")
async def serve_chat():
    """Serve the chat frontend."""
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "index.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    raise HTTPException(status_code=404, detail="Frontend not found")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
