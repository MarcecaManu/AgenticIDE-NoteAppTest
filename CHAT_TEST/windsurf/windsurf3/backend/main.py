from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime, timezone
import sqlite3
import json
import asyncio
from contextlib import asynccontextmanager

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[Dict]] = {}
    
    async def connect(self, websocket: WebSocket, room_id: str, username: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append({
            "websocket": websocket,
            "username": username
        })
    
    def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self.active_connections:
            self.active_connections[room_id] = [
                conn for conn in self.active_connections[room_id]
                if conn["websocket"] != websocket
            ]
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
    
    async def broadcast(self, message: dict, room_id: str):
        if room_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[room_id]:
                try:
                    await connection["websocket"].send_json(message)
                except:
                    disconnected.append(connection)
            
            for conn in disconnected:
                self.disconnect(conn["websocket"], room_id)
    
    def get_online_users(self, room_id: str) -> List[str]:
        if room_id not in self.active_connections:
            return []
        return [conn["username"] for conn in self.active_connections[room_id]]

manager = ConnectionManager()

def init_db():
    conn = sqlite3.connect('chat.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rooms (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id TEXT NOT NULL,
            username TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CreateRoomRequest(BaseModel):
    name: str

class Room(BaseModel):
    id: str
    name: str
    created_at: str

class Message(BaseModel):
    id: int
    room_id: str
    username: str
    content: str
    timestamp: str

def get_db():
    conn = sqlite3.connect('chat.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.post("/api/chat/rooms", response_model=Room)
async def create_room(request: CreateRoomRequest):
    import uuid
    room_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO rooms (id, name, created_at) VALUES (?, ?, ?)",
            (room_id, request.name, created_at)
        )
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))
    
    conn.close()
    
    return Room(id=room_id, name=request.name, created_at=created_at)

@app.get("/api/chat/rooms", response_model=List[Room])
async def get_rooms():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, created_at FROM rooms ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    
    return [Room(id=row["id"], name=row["name"], created_at=row["created_at"]) for row in rows]

@app.get("/api/chat/rooms/{room_id}/messages", response_model=List[Message])
async def get_messages(room_id: str):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM rooms WHERE id = ?", (room_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Room not found")
    
    cursor.execute(
        "SELECT id, room_id, username, content, timestamp FROM messages WHERE room_id = ? ORDER BY timestamp ASC",
        (room_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    
    return [
        Message(
            id=row["id"],
            room_id=row["room_id"],
            username=row["username"],
            content=row["content"],
            timestamp=row["timestamp"]
        )
        for row in rows
    ]

@app.delete("/api/chat/rooms/{room_id}")
async def delete_room(room_id: str):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM rooms WHERE id = ?", (room_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Room not found")
    
    cursor.execute("DELETE FROM messages WHERE room_id = ?", (room_id,))
    cursor.execute("DELETE FROM rooms WHERE id = ?", (room_id,))
    conn.commit()
    conn.close()
    
    return {"message": "Room deleted successfully"}

@app.websocket("/ws/chat/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, username: str = "Anonymous"):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM rooms WHERE id = ?", (room_id,))
    room = cursor.fetchone()
    conn.close()
    
    if not room:
        await websocket.close(code=1008, reason="Room not found")
        return
    
    await manager.connect(websocket, room_id, username)
    
    join_message = {
        "type": "user_joined",
        "username": username,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "online_users": manager.get_online_users(room_id)
    }
    await manager.broadcast(join_message, room_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "message":
                timestamp = datetime.now(timezone.utc).isoformat()
                
                conn = get_db()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO messages (room_id, username, content, timestamp) VALUES (?, ?, ?, ?)",
                    (room_id, username, data["content"], timestamp)
                )
                conn.commit()
                message_id = cursor.lastrowid
                conn.close()
                
                message = {
                    "type": "message",
                    "id": message_id,
                    "room_id": room_id,
                    "username": username,
                    "content": data["content"],
                    "timestamp": timestamp
                }
                await manager.broadcast(message, room_id)
            
            elif data.get("type") == "typing":
                typing_message = {
                    "type": "typing",
                    "username": username,
                    "is_typing": data.get("is_typing", False)
                }
                await manager.broadcast(typing_message, room_id)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
        leave_message = {
            "type": "user_left",
            "username": username,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "online_users": manager.get_online_users(room_id)
        }
        await manager.broadcast(leave_message, room_id)
    except Exception as e:
        manager.disconnect(websocket, room_id)
        leave_message = {
            "type": "user_left",
            "username": username,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "online_users": manager.get_online_users(room_id)
        }
        await manager.broadcast(leave_message, room_id)

@app.get("/")
async def root():
    return {"message": "Real-time Chat API is running"}
