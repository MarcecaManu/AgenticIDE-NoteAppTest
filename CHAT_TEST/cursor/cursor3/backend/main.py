"""
FastAPI application with REST API and WebSocket endpoints for real-time chat.
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Set
import uuid
from datetime import datetime
import json

from database import init_db, ChatDatabase
from models import RoomCreate, Room, Message, WebSocketMessage, ErrorResponse


app = FastAPI(title="Real-time Chat API")

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# WebSocket connection manager
class ConnectionManager:
    """Manages WebSocket connections for chat rooms."""
    
    def __init__(self):
        # room_id -> {username -> websocket}
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, room_id: str, username: str):
        """Connect a user to a room."""
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = {}
        self.active_connections[room_id][username] = websocket
    
    def disconnect(self, room_id: str, username: str):
        """Disconnect a user from a room."""
        if room_id in self.active_connections:
            self.active_connections[room_id].pop(username, None)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
    
    async def broadcast(self, room_id: str, message: dict):
        """Broadcast a message to all users in a room."""
        if room_id in self.active_connections:
            disconnected = []
            for username, websocket in self.active_connections[room_id].items():
                try:
                    await websocket.send_json(message)
                except Exception:
                    disconnected.append(username)
            
            # Clean up disconnected users
            for username in disconnected:
                self.disconnect(room_id, username)
    
    def get_room_users(self, room_id: str) -> list:
        """Get list of users in a room."""
        if room_id in self.active_connections:
            return list(self.active_connections[room_id].keys())
        return []


manager = ConnectionManager()


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()


# REST API Endpoints

@app.post("/api/chat/rooms", response_model=Room, status_code=201)
async def create_room(room_data: RoomCreate):
    """Create a new chat room."""
    room_id = str(uuid.uuid4())
    try:
        room = ChatDatabase.create_room(room_id, room_data.name)
        return room
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/chat/rooms", response_model=list[Room])
async def get_rooms():
    """Get all chat rooms."""
    rooms = ChatDatabase.get_all_rooms()
    return rooms


@app.get("/api/chat/rooms/{room_id}/messages", response_model=list[Message])
async def get_room_messages(room_id: str, limit: int = 100):
    """Get message history for a room."""
    # Verify room exists
    room = ChatDatabase.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    messages = ChatDatabase.get_room_messages(room_id, limit)
    return messages


@app.delete("/api/chat/rooms/{room_id}", status_code=204)
async def delete_room(room_id: str):
    """Delete a room and all its messages."""
    success = ChatDatabase.delete_room(room_id)
    if not success:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Notify connected users
    await manager.broadcast(room_id, {
        "type": "room_deleted",
        "message": "This room has been deleted"
    })
    
    # Clear connections
    if room_id in manager.active_connections:
        del manager.active_connections[room_id]


# WebSocket Endpoint

@app.websocket("/ws/chat/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    """WebSocket endpoint for real-time chat."""
    # Get username from query params
    username = websocket.query_params.get("username")
    
    if not username:
        await websocket.close(code=1008, reason="Username required")
        return
    
    # Verify room exists
    room = ChatDatabase.get_room(room_id)
    if not room:
        await websocket.close(code=1008, reason="Room not found")
        return
    
    # Connect user
    await manager.connect(websocket, room_id, username)
    
    # Send join notification
    join_message = {
        "type": "join",
        "username": username,
        "timestamp": datetime.utcnow().isoformat()
    }
    await manager.broadcast(room_id, join_message)
    
    # Send updated user list
    users = manager.get_room_users(room_id)
    user_list_message = {
        "type": "user_list",
        "users": users
    }
    await manager.broadcast(room_id, user_list_message)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "message":
                # Store message in database
                message_id = str(uuid.uuid4())
                timestamp = datetime.utcnow().isoformat()
                content = data.get("content", "")
                
                message = ChatDatabase.create_message(
                    message_id, room_id, username, content, timestamp
                )
                
                # Broadcast message to all users
                broadcast_data = {
                    "type": "message",
                    "message": message
                }
                await manager.broadcast(room_id, broadcast_data)
            
            elif message_type == "typing":
                # Broadcast typing indicator (not stored)
                typing_data = {
                    "type": "typing",
                    "username": username,
                    "timestamp": datetime.utcnow().isoformat()
                }
                await manager.broadcast(room_id, typing_data)
            
    except WebSocketDisconnect:
        # User disconnected
        manager.disconnect(room_id, username)
        
        # Send leave notification
        leave_message = {
            "type": "leave",
            "username": username,
            "timestamp": datetime.utcnow().isoformat()
        }
        await manager.broadcast(room_id, leave_message)
        
        # Send updated user list
        users = manager.get_room_users(room_id)
        user_list_message = {
            "type": "user_list",
            "users": users
        }
        await manager.broadcast(room_id, user_list_message)
    
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(room_id, username)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Real-time Chat API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

