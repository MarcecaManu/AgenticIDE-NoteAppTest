"""
WebSocket connection manager for handling real-time connections
"""
from fastapi import WebSocket
from typing import Dict, List, Set
import json


class ConnectionManager:
    """Manages WebSocket connections for chat rooms"""
    
    def __init__(self):
        # Store active connections: {room_id: [(websocket, username), ...]}
        self.active_connections: Dict[int, List[tuple[WebSocket, str]]] = {}
    
    async def connect(self, websocket: WebSocket, room_id: int, username: str):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        
        self.active_connections[room_id].append((websocket, username))
    
    def disconnect(self, websocket: WebSocket, room_id: int):
        """Remove a WebSocket connection"""
        if room_id in self.active_connections:
            self.active_connections[room_id] = [
                (ws, user) for ws, user in self.active_connections[room_id]
                if ws != websocket
            ]
            # Clean up empty rooms
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
    
    async def disconnect_room(self, room_id: int):
        """Disconnect all users from a specific room"""
        if room_id in self.active_connections:
            for websocket, _ in self.active_connections[room_id]:
                try:
                    await websocket.close(code=1000, reason="Room deleted")
                except:
                    pass
            del self.active_connections[room_id]
    
    def get_room_users(self, room_id: int) -> List[str]:
        """Get list of usernames in a room"""
        if room_id not in self.active_connections:
            return []
        return [username for _, username in self.active_connections[room_id]]
    
    async def broadcast_to_room(
        self,
        room_id: int,
        message: dict,
        exclude: WebSocket = None
    ):
        """Send a message to all connections in a room"""
        if room_id not in self.active_connections:
            return
        
        # Remove failed connections
        failed_connections = []
        
        for websocket, _ in self.active_connections[room_id]:
            if exclude and websocket == exclude:
                continue
            
            try:
                await websocket.send_json(message)
            except Exception:
                failed_connections.append(websocket)
        
        # Clean up failed connections
        for websocket in failed_connections:
            self.disconnect(websocket, room_id)


# Global connection manager instance
manager = ConnectionManager()

