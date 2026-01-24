"""FastAPI backend for real-time chat system with WebSockets."""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, List, Set
from datetime import datetime
import uuid
import json
from pathlib import Path

from database import Database


app = FastAPI(title="Real-time Chat API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
db = Database("chat.db")

# Mount frontend static files
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")


# Pydantic models
class CreateRoomRequest(BaseModel):
    name: str


class RoomResponse(BaseModel):
    id: str
    name: str
    created_at: str


class MessageResponse(BaseModel):
    id: str
    room_id: str
    username: str
    content: str
    timestamp: str


class WebSocketMessage(BaseModel):
    type: str  # "message", "join", "leave", "typing"
    username: str
    content: str = ""
    timestamp: str = ""


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        # room_id -> {websocket: username}
        self.active_connections: Dict[str, Dict[WebSocket, str]] = {}
    
    async def connect(self, websocket: WebSocket, room_id: str, username: str):
        """Connect a user to a room."""
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = {}
        self.active_connections[room_id][websocket] = username
    
    def disconnect(self, websocket: WebSocket, room_id: str):
        """Disconnect a user from a room."""
        if room_id in self.active_connections:
            if websocket in self.active_connections[room_id]:
                del self.active_connections[room_id][websocket]
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
    
    async def broadcast(self, room_id: str, message: dict, exclude: WebSocket = None):
        """Broadcast a message to all users in a room."""
        if room_id not in self.active_connections:
            return
        
        disconnected = []
        for websocket in self.active_connections[room_id].keys():
            if websocket != exclude:
                try:
                    await websocket.send_json(message)
                except Exception:
                    disconnected.append(websocket)
        
        # Clean up disconnected websockets
        for ws in disconnected:
            self.disconnect(ws, room_id)
    
    def get_online_users(self, room_id: str) -> List[str]:
        """Get list of online users in a room."""
        if room_id not in self.active_connections:
            return []
        return list(self.active_connections[room_id].values())
    
    def get_username(self, websocket: WebSocket, room_id: str) -> str:
        """Get username for a websocket connection."""
        if room_id in self.active_connections:
            return self.active_connections[room_id].get(websocket, "Unknown")
        return "Unknown"


manager = ConnectionManager()


# REST API Endpoints
@app.post("/api/chat/rooms", response_model=RoomResponse, status_code=201)
async def create_room(request: CreateRoomRequest):
    """Create a new chat room."""
    room_id = str(uuid.uuid4())
    room = db.create_room(room_id, request.name)
    return room


@app.get("/api/chat/rooms", response_model=List[RoomResponse])
async def get_rooms():
    """Get all chat rooms."""
    rooms = db.get_all_rooms()
    return rooms


@app.get("/api/chat/rooms/{room_id}/messages", response_model=List[MessageResponse])
async def get_room_messages(room_id: str):
    """Get message history for a room."""
    # Verify room exists
    room = db.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    messages = db.get_room_messages(room_id)
    return messages


@app.delete("/api/chat/rooms/{room_id}", status_code=204)
async def delete_room(room_id: str):
    """Delete a room and its messages."""
    success = db.delete_room(room_id)
    if not success:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Notify all connected users in the room
    await manager.broadcast(room_id, {
        "type": "room_deleted",
        "message": "This room has been deleted"
    })
    
    # Clean up connections
    if room_id in manager.active_connections:
        del manager.active_connections[room_id]


@app.get("/api/chat/rooms/{room_id}/online", response_model=List[str])
async def get_online_users(room_id: str):
    """Get list of online users in a room."""
    room = db.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    return manager.get_online_users(room_id)


# WebSocket endpoint
@app.websocket("/ws/chat/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    """WebSocket endpoint for real-time chat."""
    # Verify room exists
    room = db.get_room(room_id)
    if not room:
        await websocket.close(code=1008, reason="Room not found")
        return
    
    # Get username from query params
    username = websocket.query_params.get("username", "Anonymous")
    
    # Connect user
    await manager.connect(websocket, room_id, username)
    
    # Send join notification
    join_message = {
        "type": "join",
        "username": username,
        "content": f"{username} joined the room",
        "timestamp": datetime.utcnow().isoformat(),
        "online_users": manager.get_online_users(room_id)
    }
    await manager.broadcast(room_id, join_message)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            message_type = message_data.get("type", "message")
            
            if message_type == "message":
                # Save message to database
                message_id = str(uuid.uuid4())
                timestamp = datetime.utcnow().isoformat()
                content = message_data.get("content", "")
                
                db.create_message(
                    message_id=message_id,
                    room_id=room_id,
                    username=username,
                    content=content,
                    timestamp=timestamp
                )
                
                # Broadcast message to all users
                broadcast_message = {
                    "type": "message",
                    "id": message_id,
                    "username": username,
                    "content": content,
                    "timestamp": timestamp
                }
                await manager.broadcast(room_id, broadcast_message)
            
            elif message_type == "typing":
                # Broadcast typing indicator (don't save to DB)
                typing_message = {
                    "type": "typing",
                    "username": username,
                    "content": message_data.get("content", "")
                }
                await manager.broadcast(room_id, typing_message, exclude=websocket)
    
    except WebSocketDisconnect:
        # Handle disconnection
        manager.disconnect(websocket, room_id)
        
        # Send leave notification
        leave_message = {
            "type": "leave",
            "username": username,
            "content": f"{username} left the room",
            "timestamp": datetime.utcnow().isoformat(),
            "online_users": manager.get_online_users(room_id)
        }
        await manager.broadcast(room_id, leave_message)
    
    except Exception as e:
        # Handle other errors
        manager.disconnect(websocket, room_id)
        print(f"WebSocket error: {e}")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Real-time Chat API",
        "endpoints": {
            "rooms": "/api/chat/rooms",
            "websocket": "/ws/chat/{room_id}",
            "frontend": "/static/index.html"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
