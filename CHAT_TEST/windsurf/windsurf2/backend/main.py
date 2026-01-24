from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime, timezone
import sqlite3
import json
import asyncio
from contextlib import asynccontextmanager

DB_PATH = "chat.db"

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[Dict]] = {}
    
    async def connect(self, websocket: WebSocket, room_id: str, username: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        
        existing_conn = None
        for conn in self.active_connections[room_id]:
            if conn["username"] == username:
                existing_conn = conn
                break
        
        if existing_conn:
            try:
                await existing_conn["websocket"].close()
            except:
                pass
            self.active_connections[room_id].remove(existing_conn)
        
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
    
    async def broadcast(self, room_id: str, message: dict):
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
        usernames = [conn["username"] for conn in self.active_connections[room_id]]
        return list(dict.fromkeys(usernames))

manager = ConnectionManager()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id TEXT NOT NULL,
            username TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (room_id) REFERENCES rooms (id) ON DELETE CASCADE
        )
    """)
    
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

class CreateRoomResponse(BaseModel):
    id: str
    name: str
    created_at: str

class RoomResponse(BaseModel):
    id: str
    name: str
    created_at: str

class MessageResponse(BaseModel):
    id: int
    room_id: str
    username: str
    content: str
    timestamp: str

@app.post("/api/chat/rooms", response_model=CreateRoomResponse)
async def create_room(request: CreateRoomRequest):
    import uuid
    room_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    
    conn = sqlite3.connect(DB_PATH)
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
    
    return CreateRoomResponse(
        id=room_id,
        name=request.name,
        created_at=created_at
    )

@app.get("/api/chat/rooms", response_model=List[RoomResponse])
async def get_rooms():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, created_at FROM rooms ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    
    return [
        RoomResponse(id=row[0], name=row[1], created_at=row[2])
        for row in rows
    ]

@app.get("/api/chat/rooms/{room_id}/messages", response_model=List[MessageResponse])
async def get_messages(room_id: str):
    conn = sqlite3.connect(DB_PATH)
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
        MessageResponse(
            id=row[0],
            room_id=row[1],
            username=row[2],
            content=row[3],
            timestamp=row[4]
        )
        for row in rows
    ]

@app.delete("/api/chat/rooms/{room_id}")
async def delete_room(room_id: str):
    conn = sqlite3.connect(DB_PATH)
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
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    username = websocket.query_params.get("username", "Anonymous")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM rooms WHERE id = ?", (room_id,))
    if not cursor.fetchone():
        conn.close()
        await websocket.close(code=1008, reason="Room not found")
        return
    conn.close()
    
    await manager.connect(websocket, room_id, username)
    
    await manager.broadcast(room_id, {
        "type": "user_joined",
        "username": username,
        "online_users": manager.get_online_users(room_id),
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "message":
                content = data.get("content", "")
                timestamp = datetime.now(timezone.utc).isoformat()
                
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO messages (room_id, username, content, timestamp) VALUES (?, ?, ?, ?)",
                    (room_id, username, content, timestamp)
                )
                conn.commit()
                message_id = cursor.lastrowid
                conn.close()
                
                await manager.broadcast(room_id, {
                    "type": "message",
                    "id": message_id,
                    "room_id": room_id,
                    "username": username,
                    "content": content,
                    "timestamp": timestamp
                })
            
            elif data.get("type") == "typing":
                await manager.broadcast(room_id, {
                    "type": "typing",
                    "username": username,
                    "is_typing": data.get("is_typing", False)
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
        await manager.broadcast(room_id, {
            "type": "user_left",
            "username": username,
            "online_users": manager.get_online_users(room_id),
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    except Exception as e:
        manager.disconnect(websocket, room_id)
        await manager.broadcast(room_id, {
            "type": "user_left",
            "username": username,
            "online_users": manager.get_online_users(room_id),
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

@app.get("/")
async def root():
    return {"message": "Real-time Chat API is running"}
