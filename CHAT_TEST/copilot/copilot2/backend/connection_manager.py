"""WebSocket connection manager for real-time chat."""
from typing import Dict, List, Set
from fastapi import WebSocket
import json
from datetime import datetime


class ConnectionManager:
    """Manages WebSocket connections for chat rooms."""
    
    def __init__(self):
        # room_id -> list of websocket connections
        self.active_connections: Dict[int, List[WebSocket]] = {}
        # room_id -> set of usernames
        self.room_users: Dict[int, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, room_id: int, username: str):
        """Connect a new WebSocket client to a room."""
        await websocket.accept()
        
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
            self.room_users[room_id] = set()
        
        self.active_connections[room_id].append(websocket)
        self.room_users[room_id].add(username)
        
        # Notify all users in the room about the new user
        await self.broadcast_system_message(
            room_id, 
            f"{username} joined the room",
            "join",
            username
        )
        
        # Send updated user list
        await self.broadcast_user_list(room_id)
    
    def disconnect(self, websocket: WebSocket, room_id: int, username: str):
        """Disconnect a WebSocket client from a room."""
        if room_id in self.active_connections:
            if websocket in self.active_connections[room_id]:
                self.active_connections[room_id].remove(websocket)
            
            if username in self.room_users[room_id]:
                self.room_users[room_id].remove(username)
            
            # Clean up empty rooms
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
                del self.room_users[room_id]
    
    async def broadcast_message(self, room_id: int, message: dict):
        """Broadcast a message to all connections in a room."""
        if room_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[room_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.append(connection)
            
            # Remove disconnected clients
            for connection in disconnected:
                if connection in self.active_connections[room_id]:
                    self.active_connections[room_id].remove(connection)
    
    async def broadcast_system_message(self, room_id: int, content: str, message_type: str, username: str = "System"):
        """Broadcast a system message (join, leave, etc.)."""
        message = {
            "id": None,
            "room_id": room_id,
            "username": username,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "message_type": message_type
        }
        await self.broadcast_message(room_id, message)
    
    async def broadcast_user_list(self, room_id: int):
        """Broadcast the current list of users in a room."""
        if room_id in self.room_users:
            user_list = list(self.room_users[room_id])
            message = {
                "message_type": "user_list",
                "users": user_list,
                "room_id": room_id
            }
            await self.broadcast_message(room_id, message)
    
    async def broadcast_typing(self, room_id: int, username: str, is_typing: bool):
        """Broadcast typing indicator."""
        message = {
            "message_type": "typing",
            "username": username,
            "is_typing": is_typing,
            "room_id": room_id
        }
        await self.broadcast_message(room_id, message)
    
    def get_room_users(self, room_id: int) -> List[str]:
        """Get list of users in a room."""
        return list(self.room_users.get(room_id, set()))
