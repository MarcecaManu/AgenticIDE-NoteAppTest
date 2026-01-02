"""
Main FastAPI application for real-time chat system.
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import uuid
import json
from datetime import datetime

from database import Database, init_db
from models import RoomCreate, Room, Message
from websocket_manager import ConnectionManager

app = FastAPI(title="Real-time Chat System", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
manager = ConnectionManager()

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    await init_db()


# REST API Endpoints
@app.post("/api/chat/rooms", response_model=Room, status_code=status.HTTP_201_CREATED)
async def create_room(room: RoomCreate):
    """Create a new chat room."""
    room_id = str(uuid.uuid4())
    created_room = await Database.create_room(room_id, room.name)
    return created_room


@app.get("/api/chat/rooms", response_model=list[Room])
async def get_rooms():
    """Get all chat rooms."""
    rooms = await Database.get_all_rooms()
    return rooms


@app.get("/api/chat/rooms/{room_id}/messages", response_model=list[Message])
async def get_messages(room_id: str, limit: int = 100):
    """Get message history for a specific room."""
    # Check if room exists
    room = await Database.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    messages = await Database.get_messages(room_id, limit)
    return messages


@app.delete("/api/chat/rooms/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(room_id: str):
    """Delete a room and all its messages."""
    deleted = await Database.delete_room(room_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Room not found")
    return None


# WebSocket Endpoint
@app.websocket("/ws/chat/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    """WebSocket endpoint for real-time chat in a specific room."""
    # Get username from query parameters
    username = websocket.query_params.get("username", "Anonymous")
    
    # Check if room exists
    room = await Database.get_room(room_id)
    if not room:
        await websocket.close(code=4004, reason="Room not found")
        return
    
    # Connect the user
    await manager.connect(websocket, room_id, username)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            message_type = message_data.get("type")
            
            if message_type == "message":
                # Handle chat message
                content = message_data.get("content", "").strip()
                if content:
                    message_id = str(uuid.uuid4())
                    timestamp = datetime.utcnow().isoformat()
                    
                    # Save message to database
                    saved_message = await Database.save_message(
                        message_id, room_id, username, content, timestamp
                    )
                    
                    # Broadcast to all users in the room
                    await manager.broadcast_to_room(
                        room_id,
                        {
                            "type": "message",
                            "data": saved_message
                        }
                    )
            
            elif message_type == "typing":
                # Handle typing indicator
                is_typing = message_data.get("is_typing", False)
                await manager.handle_typing(room_id, username, is_typing)
            
            elif message_type == "get_users":
                # Send current user list
                await manager.send_user_list(room_id, websocket)
    
    except WebSocketDisconnect:
        # Handle disconnection
        manager.disconnect(websocket, room_id, username)
        
        # Notify others
        await manager.broadcast_to_room(
            room_id,
            {
                "type": "leave",
                "data": {
                    "username": username,
                    "message": f"{username} left the room"
                }
            }
        )
        
        # Update user list for remaining users
        await manager.send_user_list(room_id)
    
    except Exception as e:
        print(f"Error in websocket: {e}")
        manager.disconnect(websocket, room_id, username)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Serve frontend
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    @app.get("/")
    async def serve_frontend():
        """Serve the frontend HTML."""
        return FileResponse(frontend_path / "index.html")
    
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

