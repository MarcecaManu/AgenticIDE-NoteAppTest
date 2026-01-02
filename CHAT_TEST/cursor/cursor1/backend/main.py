"""
FastAPI backend for Real-time Chat System
Provides REST API and WebSocket endpoints for chat functionality
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List, Dict, Set
from datetime import datetime
from contextlib import asynccontextmanager
import json
import asyncio
import os
from pathlib import Path

from models import (
    ChatRoom, Message, RoomCreate, MessageCreate,
    ChatRoomModel, MessageModel,
    get_db_session, init_db
)

# Get absolute paths
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown (if needed)

app = FastAPI(title="Real-time Chat API", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connection manager for WebSocket connections
class ConnectionManager:
    def __init__(self):
        # room_id -> Set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # room_id -> Set of usernames
        self.room_users: Dict[str, Set[str]] = {}
        # WebSocket -> username mapping
        self.connection_usernames: Dict[WebSocket, str] = {}
        # Typing indicators: room_id -> Set of usernames
        self.typing_users: Dict[str, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, room_id: str, username: str):
        """Connect a user to a chat room"""
        await websocket.accept()
        
        if room_id not in self.active_connections:
            self.active_connections[room_id] = set()
            self.room_users[room_id] = set()
            self.typing_users[room_id] = set()
        
        self.active_connections[room_id].add(websocket)
        self.room_users[room_id].add(username)
        self.connection_usernames[websocket] = username
        
        # Notify others about new user
        await self.broadcast_system_message(
            room_id,
            f"{username} joined the room",
            exclude=websocket
        )
        
        # Send current users list to everyone
        await self.broadcast_users_list(room_id)
    
    def disconnect(self, websocket: WebSocket, room_id: str):
        """Disconnect a user from a chat room"""
        if room_id in self.active_connections:
            self.active_connections[room_id].discard(websocket)
            
            username = self.connection_usernames.get(websocket)
            if username:
                self.room_users[room_id].discard(username)
                self.typing_users[room_id].discard(username)
                del self.connection_usernames[websocket]
                
                # Clean up empty rooms
                if not self.active_connections[room_id]:
                    del self.active_connections[room_id]
                    del self.room_users[room_id]
                    del self.typing_users[room_id]
                
                return username
        return None
    
    async def broadcast_message(self, room_id: str, message: dict):
        """Broadcast a message to all users in a room"""
        if room_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[room_id].copy():
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.add(connection)
            
            # Clean up disconnected connections
            for conn in disconnected:
                self.disconnect(conn, room_id)
    
    async def broadcast_system_message(self, room_id: str, content: str, exclude: WebSocket = None):
        """Broadcast a system message"""
        message = {
            "type": "system",
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                if connection != exclude:
                    try:
                        await connection.send_json(message)
                    except Exception:
                        pass
    
    async def broadcast_users_list(self, room_id: str):
        """Broadcast the current users list to all connections in a room"""
        if room_id in self.room_users:
            users_list = list(self.room_users[room_id])
            message = {
                "type": "users_list",
                "users": users_list,
                "count": len(users_list)
            }
            await self.broadcast_message(room_id, message)
    
    async def broadcast_typing_status(self, room_id: str):
        """Broadcast typing indicators"""
        if room_id in self.typing_users:
            typing_list = list(self.typing_users[room_id])
            message = {
                "type": "typing",
                "users": typing_list
            }
            await self.broadcast_message(room_id, message)
    
    def set_typing(self, room_id: str, username: str, is_typing: bool):
        """Update typing status for a user"""
        if room_id in self.typing_users:
            if is_typing:
                self.typing_users[room_id].add(username)
            else:
                self.typing_users[room_id].discard(username)

manager = ConnectionManager()

# REST API Endpoints

@app.post("/api/chat/rooms", response_model=ChatRoom)
async def create_room(room: RoomCreate):
    """Create a new chat room"""
    db = get_db_session()
    try:
        # Check if room name already exists
        existing = db.query(ChatRoomModel).filter(ChatRoomModel.name == room.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Room name already exists")
        
        new_room = ChatRoomModel(
            name=room.name,
            description=room.description or "",
            created_at=datetime.utcnow()
        )
        db.add(new_room)
        db.commit()
        db.refresh(new_room)
        return new_room
    finally:
        db.close()

@app.get("/api/chat/rooms", response_model=List[ChatRoom])
async def list_rooms():
    """List all chat rooms"""
    db = get_db_session()
    try:
        rooms = db.query(ChatRoomModel).order_by(ChatRoomModel.created_at.desc()).all()
        return rooms
    finally:
        db.close()

@app.get("/api/chat/rooms/{room_id}/messages", response_model=List[Message])
async def get_room_messages(room_id: int, limit: int = 100):
    """Get message history for a room"""
    db = get_db_session()
    try:
        # Check if room exists
        room = db.query(ChatRoomModel).filter(ChatRoomModel.id == room_id).first()
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        
        messages = (
            db.query(MessageModel)
            .filter(MessageModel.room_id == room_id)
            .order_by(MessageModel.timestamp.desc())
            .limit(limit)
            .all()
        )
        return list(reversed(messages))
    finally:
        db.close()

@app.delete("/api/chat/rooms/{room_id}")
async def delete_room(room_id: int):
    """Delete a room and all its messages"""
    db = get_db_session()
    try:
        room = db.query(ChatRoomModel).filter(ChatRoomModel.id == room_id).first()
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        
        # Delete all messages in the room
        db.query(MessageModel).filter(MessageModel.room_id == room_id).delete()
        
        # Delete the room
        db.delete(room)
        db.commit()
        
        # Disconnect all users from this room
        room_id_str = str(room_id)
        if room_id_str in manager.active_connections:
            connections = list(manager.active_connections[room_id_str])
            for conn in connections:
                try:
                    await conn.send_json({
                        "type": "room_deleted",
                        "message": "This room has been deleted"
                    })
                    await conn.close()
                except Exception:
                    pass
            # Clean up
            if room_id_str in manager.active_connections:
                del manager.active_connections[room_id_str]
            if room_id_str in manager.room_users:
                del manager.room_users[room_id_str]
            if room_id_str in manager.typing_users:
                del manager.typing_users[room_id_str]
        
        return {"message": "Room deleted successfully"}
    finally:
        db.close()

# WebSocket Endpoint

@app.websocket("/ws/chat/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: int):
    """WebSocket endpoint for real-time chat"""
    # Wait for initial authentication message
    await websocket.accept()
    
    try:
        # First message should contain username
        auth_data = await websocket.receive_json()
        username = auth_data.get("username", "Anonymous")
        
        if not username or username.strip() == "":
            username = "Anonymous"
        
        username = username.strip()[:50]  # Limit username length
        
        # Verify room exists
        db = get_db_session()
        try:
            room = db.query(ChatRoomModel).filter(ChatRoomModel.id == room_id).first()
            if not room:
                await websocket.send_json({
                    "type": "error",
                    "content": "Room not found"
                })
                await websocket.close()
                return
        finally:
            db.close()
        
        # Connect user to room
        room_id_str = str(room_id)
        await manager.connect(websocket, room_id_str, username)
        
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "username": username,
            "room_id": room_id
        })
        
        # Main message loop
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type", "message")
            
            if message_type == "message":
                # Regular chat message
                content = data.get("content", "").strip()
                if content:
                    # Save message to database
                    db = get_db_session()
                    try:
                        new_message = MessageModel(
                            room_id=room_id,
                            username=username,
                            content=content,
                            timestamp=datetime.utcnow()
                        )
                        db.add(new_message)
                        db.commit()
                        db.refresh(new_message)
                        
                        # Broadcast message to all users in room
                        await manager.broadcast_message(room_id_str, {
                            "type": "message",
                            "id": new_message.id,
                            "room_id": new_message.room_id,
                            "username": new_message.username,
                            "content": new_message.content,
                            "timestamp": new_message.timestamp.isoformat()
                        })
                    finally:
                        db.close()
            
            elif message_type == "typing":
                # Typing indicator
                is_typing = data.get("is_typing", False)
                manager.set_typing(room_id_str, username, is_typing)
                await manager.broadcast_typing_status(room_id_str)
    
    except WebSocketDisconnect:
        # Handle disconnection
        username = manager.disconnect(websocket, room_id_str)
        if username:
            await manager.broadcast_system_message(room_id_str, f"{username} left the room")
            await manager.broadcast_users_list(room_id_str)
    
    except Exception as e:
        # Handle other errors
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, room_id_str)

# Serve frontend (only if directory exists, for production use)
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
    
    @app.get("/")
    async def read_root():
        """Serve the frontend HTML"""
        return FileResponse(str(FRONTEND_DIR / "index.html"))
else:
    @app.get("/")
    async def read_root():
        """API root endpoint"""
        return {
            "message": "Real-time Chat API",
            "docs": "/docs",
            "api": "/api/chat/"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

