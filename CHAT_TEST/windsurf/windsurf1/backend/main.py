from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime, timezone
import json
import os
import uuid
import asyncio

app = FastAPI(title="Real-time Chat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = "data"
ROOMS_FILE = os.path.join(DATA_DIR, "rooms.json")
MESSAGES_FILE = os.path.join(DATA_DIR, "messages.json")

os.makedirs(DATA_DIR, exist_ok=True)

class Room(BaseModel):
    id: str
    name: str
    created_at: str

class Message(BaseModel):
    id: str
    room_id: str
    username: str
    content: str
    timestamp: str

class CreateRoomRequest(BaseModel):
    name: str

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[Dict]] = {}
        self.typing_users: Dict[str, set] = {}
    
    async def connect(self, websocket: WebSocket, room_id: str, username: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
            self.typing_users[room_id] = set()
        
        self.active_connections[room_id].append({
            "websocket": websocket,
            "username": username
        })
        
        await self.broadcast_system_message(
            room_id, 
            f"{username} joined the room",
            exclude_ws=None
        )
        
        await self.broadcast_user_list(room_id)
    
    def disconnect(self, websocket: WebSocket, room_id: str, username: str):
        if room_id in self.active_connections:
            self.active_connections[room_id] = [
                conn for conn in self.active_connections[room_id] 
                if conn["websocket"] != websocket
            ]
            
            if username in self.typing_users.get(room_id, set()):
                self.typing_users[room_id].discard(username)
            
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
                if room_id in self.typing_users:
                    del self.typing_users[room_id]
    
    async def broadcast_message(self, room_id: str, message: dict):
        if room_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[room_id]:
                try:
                    await connection["websocket"].send_json(message)
                except:
                    disconnected.append(connection)
            
            for conn in disconnected:
                self.disconnect(conn["websocket"], room_id, conn["username"])
    
    async def broadcast_system_message(self, room_id: str, content: str, exclude_ws=None):
        message = {
            "type": "system",
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                if exclude_ws is None or connection["websocket"] != exclude_ws:
                    try:
                        await connection["websocket"].send_json(message)
                    except:
                        pass
    
    async def broadcast_user_list(self, room_id: str):
        if room_id in self.active_connections:
            users = [conn["username"] for conn in self.active_connections[room_id]]
            message = {
                "type": "user_list",
                "users": users
            }
            await self.broadcast_message(room_id, message)
    
    async def broadcast_typing(self, room_id: str):
        if room_id in self.typing_users:
            typing_list = list(self.typing_users[room_id])
            message = {
                "type": "typing",
                "users": typing_list
            }
            await self.broadcast_message(room_id, message)
    
    def set_typing(self, room_id: str, username: str, is_typing: bool):
        if room_id not in self.typing_users:
            self.typing_users[room_id] = set()
        
        if is_typing:
            self.typing_users[room_id].add(username)
        else:
            self.typing_users[room_id].discard(username)

manager = ConnectionManager()

def load_rooms() -> Dict[str, Room]:
    if os.path.exists(ROOMS_FILE):
        with open(ROOMS_FILE, 'r') as f:
            data = json.load(f)
            return {k: Room(**v) for k, v in data.items()}
    return {}

def save_rooms(rooms: Dict[str, Room]):
    with open(ROOMS_FILE, 'w') as f:
        json.dump({k: v.dict() for k, v in rooms.items()}, f, indent=2)

def load_messages() -> List[Message]:
    if os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, 'r') as f:
            data = json.load(f)
            return [Message(**msg) for msg in data]
    return []

def save_messages(messages: List[Message]):
    with open(MESSAGES_FILE, 'w') as f:
        json.dump([msg.dict() for msg in messages], f, indent=2)

def add_message(message: Message):
    messages = load_messages()
    messages.append(message)
    save_messages(messages)

@app.post("/api/chat/rooms", response_model=Room)
async def create_room(request: CreateRoomRequest):
    rooms = load_rooms()
    room_id = str(uuid.uuid4())
    room = Room(
        id=room_id,
        name=request.name,
        created_at=datetime.now(timezone.utc).isoformat()
    )
    rooms[room_id] = room
    save_rooms(rooms)
    return room

@app.get("/api/chat/rooms", response_model=List[Room])
async def get_rooms():
    rooms = load_rooms()
    return list(rooms.values())

@app.get("/api/chat/rooms/{room_id}/messages", response_model=List[Message])
async def get_room_messages(room_id: str):
    rooms = load_rooms()
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    messages = load_messages()
    room_messages = [msg for msg in messages if msg.room_id == room_id]
    return room_messages

@app.delete("/api/chat/rooms/{room_id}")
async def delete_room(room_id: str):
    rooms = load_rooms()
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    del rooms[room_id]
    save_rooms(rooms)
    
    messages = load_messages()
    messages = [msg for msg in messages if msg.room_id != room_id]
    save_messages(messages)
    
    if room_id in manager.active_connections:
        for connection in manager.active_connections[room_id][:]:
            try:
                await connection["websocket"].close()
            except:
                pass
        manager.active_connections.pop(room_id, None)
        manager.typing_users.pop(room_id, None)
    
    return {"message": "Room deleted successfully"}

@app.websocket("/ws/chat/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, username: str = "Anonymous"):
    rooms = load_rooms()
    if room_id not in rooms:
        await websocket.close(code=1008, reason="Room not found")
        return
    
    await manager.connect(websocket, room_id, username)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "message":
                message = Message(
                    id=str(uuid.uuid4()),
                    room_id=room_id,
                    username=username,
                    content=data.get("content", ""),
                    timestamp=datetime.now(timezone.utc).isoformat()
                )
                add_message(message)
                
                await manager.broadcast_message(room_id, {
                    "type": "message",
                    "message": message.dict()
                })
                
                manager.set_typing(room_id, username, False)
                await manager.broadcast_typing(room_id)
            
            elif data.get("type") == "typing":
                is_typing = data.get("is_typing", False)
                manager.set_typing(room_id, username, is_typing)
                await manager.broadcast_typing(room_id)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id, username)
        await manager.broadcast_system_message(
            room_id,
            f"{username} left the room"
        )
        await manager.broadcast_user_list(room_id)
    except Exception as e:
        manager.disconnect(websocket, room_id, username)
        await manager.broadcast_system_message(
            room_id,
            f"{username} left the room"
        )
        await manager.broadcast_user_list(room_id)

@app.get("/")
async def root():
    return {"message": "Real-time Chat API is running"}
