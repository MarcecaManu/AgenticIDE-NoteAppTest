"""
WebSocket connection manager for handling real-time chat.
"""
from fastapi import WebSocket
from typing import Dict, Set, List
import json
import asyncio


class ConnectionManager:
    """Manages WebSocket connections for chat rooms."""
    
    def __init__(self):
        # room_id -> set of (websocket, username) tuples
        self.active_connections: Dict[str, Set[tuple]] = {}
        # room_id -> set of usernames currently typing
        self.typing_users: Dict[str, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, room_id: str, username: str):
        """Accept a new WebSocket connection and add to room."""
        await websocket.accept()
        
        if room_id not in self.active_connections:
            self.active_connections[room_id] = set()
            self.typing_users[room_id] = set()
        
        self.active_connections[room_id].add((websocket, username))
        
        # Notify others in the room
        await self.broadcast_to_room(
            room_id,
            {
                "type": "join",
                "data": {
                    "username": username,
                    "message": f"{username} joined the room"
                }
            },
            exclude_ws=websocket
        )
        
        # Send current user list to the new user
        await self.send_user_list(room_id, websocket)
    
    def disconnect(self, websocket: WebSocket, room_id: str, username: str):
        """Remove a WebSocket connection from a room."""
        if room_id in self.active_connections:
            self.active_connections[room_id].discard((websocket, username))
            
            # Remove from typing users
            if username in self.typing_users.get(room_id, set()):
                self.typing_users[room_id].discard(username)
            
            # Clean up empty rooms
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
                if room_id in self.typing_users:
                    del self.typing_users[room_id]
    
    async def broadcast_to_room(self, room_id: str, message: dict, exclude_ws: WebSocket = None):
        """Broadcast a message to all connections in a room."""
        if room_id not in self.active_connections:
            return
        
        message_json = json.dumps(message)
        disconnected = []
        
        for websocket, username in self.active_connections[room_id]:
            if websocket == exclude_ws:
                continue
            
            try:
                await websocket.send_text(message_json)
            except Exception:
                disconnected.append((websocket, username))
        
        # Clean up disconnected websockets
        for ws, user in disconnected:
            self.disconnect(ws, room_id, user)
    
    async def send_user_list(self, room_id: str, websocket: WebSocket = None):
        """Send the list of active users in a room."""
        if room_id not in self.active_connections:
            return
        
        usernames = [username for _, username in self.active_connections[room_id]]
        message = {
            "type": "user_list",
            "data": {
                "users": usernames
            }
        }
        
        if websocket:
            # Send to specific websocket
            await websocket.send_json(message)
        else:
            # Broadcast to all in room
            await self.broadcast_to_room(room_id, message)
    
    async def handle_typing(self, room_id: str, username: str, is_typing: bool):
        """Handle typing indicator updates."""
        if room_id not in self.typing_users:
            self.typing_users[room_id] = set()
        
        if is_typing:
            self.typing_users[room_id].add(username)
        else:
            self.typing_users[room_id].discard(username)
        
        # Broadcast typing status
        await self.broadcast_to_room(
            room_id,
            {
                "type": "typing",
                "data": {
                    "username": username,
                    "is_typing": is_typing
                }
            }
        )
    
    def get_room_users(self, room_id: str) -> List[str]:
        """Get list of usernames in a room."""
        if room_id not in self.active_connections:
            return []
        return [username for _, username in self.active_connections[room_id]]

