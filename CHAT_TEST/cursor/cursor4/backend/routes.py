"""
API routes for chat system
"""
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Room, Message
from schemas import (
    RoomCreate, RoomResponse, RoomListResponse,
    MessageResponse, MessageCreate
)
from connection_manager import manager

chat_router = APIRouter()
websocket_router = APIRouter()


@chat_router.post("/rooms", response_model=RoomResponse, status_code=201)
async def create_room(room: RoomCreate, db: Session = Depends(get_db)):
    """Create a new chat room"""
    # Check if room already exists
    existing_room = db.query(Room).filter(Room.name == room.name).first()
    if existing_room:
        raise HTTPException(status_code=400, detail="Room already exists")
    
    db_room = Room(name=room.name)
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room


@chat_router.get("/rooms", response_model=RoomListResponse)
async def get_rooms(db: Session = Depends(get_db)):
    """Get all chat rooms"""
    rooms = db.query(Room).order_by(Room.created_at.desc()).all()
    return {"rooms": rooms, "count": len(rooms)}


@chat_router.get("/rooms/{room_id}/messages", response_model=List[MessageResponse])
async def get_room_messages(room_id: str, db: Session = Depends(get_db)):
    """Get message history for a specific room"""
    # Try to convert room_id to integer
    try:
        room_id_int = int(room_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Check if room exists
    room = db.query(Room).filter(Room.id == room_id_int).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    messages = db.query(Message).filter(
        Message.room_id == room_id_int
    ).order_by(Message.timestamp.asc()).all()
    
    return messages


@chat_router.delete("/rooms/{room_id}", status_code=204)
async def delete_room(room_id: str, db: Session = Depends(get_db)):
    """Delete a chat room and all its messages"""
    # Try to convert room_id to integer
    try:
        room_id_int = int(room_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room = db.query(Room).filter(Room.id == room_id_int).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Disconnect all users from this room
    await manager.disconnect_room(room_id_int)
    
    db.delete(room)
    db.commit()
    return None


@websocket_router.websocket("/ws/chat/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: str,
    username: str,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time chat"""
    # Try to convert room_id to integer
    try:
        room_id_int = int(room_id)
    except ValueError:
        await websocket.close(code=4004, reason="Room not found")
        return
    
    # Verify room exists
    room = db.query(Room).filter(Room.id == room_id_int).first()
    if not room:
        await websocket.close(code=4004, reason="Room not found")
        return
    
    await manager.connect(websocket, room_id_int, username)
    
    # Notify others that user joined
    await manager.broadcast_to_room(
        room_id_int,
        {
            "type": "join",
            "username": username,
            "content": f"{username} joined the room",
            "timestamp": None
        },
        exclude=websocket
    )
    
    # Send online users list
    online_users = manager.get_room_users(room_id_int)
    await websocket.send_json({
        "type": "users_list",
        "users": online_users
    })
    
    try:
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type", "message")
            
            if message_type == "message":
                # Save message to database
                content = data.get("content", "")
                if content.strip():
                    db_message = Message(
                        room_id=room_id_int,
                        username=username,
                        content=content
                    )
                    db.add(db_message)
                    db.commit()
                    db.refresh(db_message)
                    
                    # Broadcast message to all users in room
                    await manager.broadcast_to_room(
                        room_id_int,
                        {
                            "type": "message",
                            "id": db_message.id,
                            "username": username,
                            "content": content,
                            "timestamp": db_message.timestamp.isoformat()
                        }
                    )
            
            elif message_type == "typing":
                # Broadcast typing indicator (don't save to DB)
                await manager.broadcast_to_room(
                    room_id_int,
                    {
                        "type": "typing",
                        "username": username
                    },
                    exclude=websocket
                )
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id_int)
        # Notify others that user left
        await manager.broadcast_to_room(
            room_id_int,
            {
                "type": "leave",
                "username": username,
                "content": f"{username} left the room",
                "timestamp": None
            }
        )

