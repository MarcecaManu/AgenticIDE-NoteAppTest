from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import json

from database import get_db, init_db, Room as RoomModel, Message as MessageModel
from schemas import Room, RoomCreate, RoomList, Message, MessageCreate
from connection_manager import manager

app = FastAPI(title="Real-time Chat API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom exception handler for validation errors on room_id paths
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Convert validation errors for room_id paths to 400 Bad Request"""
    errors = exc.errors()
    
    # Check if this is a room_id validation error
    for error in errors:
        if 'room_id' in error.get('loc', []) and 'int_parsing' in str(error.get('type', '')):
            return JSONResponse(
                status_code=400,
                content={"detail": "Invalid room ID"}
            )
    
    # For other validation errors, return 422 as normal
    return JSONResponse(
        status_code=422,
        content={"detail": errors}
    )


@app.on_event("startup")
def startup_event():
    init_db()


# REST API Endpoints

@app.post("/api/chat/rooms", response_model=Room, status_code=201)
def create_room(room: RoomCreate, db: Session = Depends(get_db)):
    """Create a new chat room"""
    # Check if room already exists
    existing_room = db.query(RoomModel).filter(RoomModel.name == room.name).first()
    if existing_room:
        raise HTTPException(status_code=400, detail="Room already exists")
    
    db_room = RoomModel(name=room.name)
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room


@app.get("/api/chat/rooms", response_model=List[RoomList])
def list_rooms(db: Session = Depends(get_db)):
    """List all chat rooms"""
    rooms = db.query(RoomModel).all()
    return rooms


@app.get("/api/chat/rooms/{room_id}/messages", response_model=List[Message])
def get_room_messages(room_id: int, db: Session = Depends(get_db)):
    """Get message history for a room"""
    room = db.query(RoomModel).filter(RoomModel.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    messages = db.query(MessageModel).filter(
        MessageModel.room_id == room_id
    ).order_by(MessageModel.timestamp).all()
    return messages


@app.delete("/api/chat/rooms/{room_id}", status_code=204)
def delete_room(room_id: int, db: Session = Depends(get_db)):
    """Delete a room and its messages"""
    room = db.query(RoomModel).filter(RoomModel.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    db.delete(room)
    db.commit()
    return None


# WebSocket Endpoint

@app.websocket("/ws/chat/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: int, username: str, db: Session = Depends(get_db)):
    """WebSocket endpoint for real-time chat"""
    # Verify room exists
    room = db.query(RoomModel).filter(RoomModel.id == room_id).first()
    if not room:
        await websocket.close(code=1008, reason="Room not found")
        db.close()
        return
    
    await manager.connect(websocket, room_id, username)
    
    # Send join notification
    join_message = {
        "type": "join",
        "username": username,
        "content": f"{username} joined the room",
        "timestamp": datetime.utcnow().isoformat()
    }
    await manager.broadcast_to_room(room_id, join_message)
    
    # Send updated user list
    await manager.send_user_list(room_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type", "message")
            
            if message_type == "message":
                # Save message to database
                content = data.get("content", "")
                if content.strip():
                    db_message = MessageModel(
                        room_id=room_id,
                        username=username,
                        content=content
                    )
                    db.add(db_message)
                    db.commit()
                    db.refresh(db_message)
                    
                    # Broadcast message to all users in the room
                    broadcast_data = {
                        "type": "message",
                        "id": db_message.id,
                        "username": username,
                        "content": content,
                        "timestamp": db_message.timestamp.isoformat()
                    }
                    await manager.broadcast_to_room(room_id, broadcast_data)
            
            elif message_type == "typing":
                # Handle typing indicator
                is_typing = data.get("is_typing", False)
                await manager.set_typing(room_id, username, is_typing)
    
    except WebSocketDisconnect:
        manager.disconnect(room_id, username)
        
        # Send leave notification
        leave_message = {
            "type": "leave",
            "username": username,
            "content": f"{username} left the room",
            "timestamp": datetime.utcnow().isoformat()
        }
        await manager.broadcast_to_room(room_id, leave_message)
        
        # Send updated user list
        await manager.send_user_list(room_id)
    except Exception as e:
        manager.disconnect(room_id, username)
        raise
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "Real-time Chat API", "version": "1.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
