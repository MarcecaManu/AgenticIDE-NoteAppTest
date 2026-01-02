from fastapi import WebSocket
from typing import Dict, List, Set
import json
from datetime import datetime


class ConnectionManager:
    def __init__(self):
        # room_id -> {username -> websocket}
        self.active_connections: Dict[int, Dict[str, WebSocket]] = {}
        # track typing status: room_id -> {username}
        self.typing_users: Dict[int, Set[str]] = {}

    async def connect(self, websocket: WebSocket, room_id: int, username: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = {}
        self.active_connections[room_id][username] = websocket

    def disconnect(self, room_id: int, username: str):
        if room_id in self.active_connections:
            if username in self.active_connections[room_id]:
                del self.active_connections[room_id][username]
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
        
        # Remove from typing users
        if room_id in self.typing_users:
            self.typing_users[room_id].discard(username)
            if not self.typing_users[room_id]:
                del self.typing_users[room_id]

    async def broadcast_to_room(self, room_id: int, message: dict):
        if room_id in self.active_connections:
            disconnected = []
            for username, connection in self.active_connections[room_id].items():
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.append(username)
            
            # Clean up disconnected users
            for username in disconnected:
                self.disconnect(room_id, username)

    async def send_user_list(self, room_id: int):
        if room_id in self.active_connections:
            users = list(self.active_connections[room_id].keys())
            message = {
                "type": "user_list",
                "users": users,
                "timestamp": datetime.utcnow().isoformat()
            }
            await self.broadcast_to_room(room_id, message)

    def get_room_users(self, room_id: int) -> List[str]:
        if room_id in self.active_connections:
            return list(self.active_connections[room_id].keys())
        return []

    async def set_typing(self, room_id: int, username: str, is_typing: bool):
        if room_id not in self.typing_users:
            self.typing_users[room_id] = set()
        
        if is_typing:
            self.typing_users[room_id].add(username)
        else:
            self.typing_users[room_id].discard(username)
        
        # Broadcast typing status
        typing_list = list(self.typing_users[room_id])
        message = {
            "type": "typing",
            "users": typing_list,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast_to_room(room_id, message)


manager = ConnectionManager()
