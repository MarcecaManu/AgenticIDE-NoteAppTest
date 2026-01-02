"""
Comprehensive test suite for Real-time Chat System
Tests REST endpoints, WebSocket connections, message broadcasting, and room management
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
import asyncio
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app, manager
from models import Base, ChatRoomModel, MessageModel, get_db_session

# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_chat.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def test_db():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(test_db, monkeypatch):
    """Create a test client with a test database"""
    def override_get_db():
        return TestSessionLocal()
    
    monkeypatch.setattr("main.get_db_session", override_get_db)
    monkeypatch.setattr("models.get_db_session", override_get_db)
    
    with TestClient(app) as c:
        yield c

# Test 1: Create Chat Room (REST API)
def test_create_chat_room(client):
    """Test creating a new chat room via REST API"""
    response = client.post(
        "/api/chat/rooms",
        json={"name": "Test Room", "description": "A test room"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Room"
    assert data["description"] == "A test room"
    assert "id" in data
    assert "created_at" in data

def test_create_duplicate_room(client):
    """Test that duplicate room names are rejected"""
    # Create first room
    client.post("/api/chat/rooms", json={"name": "Unique Room"})
    
    # Try to create duplicate
    response = client.post("/api/chat/rooms", json={"name": "Unique Room"})
    
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()

# Test 2: List Chat Rooms (REST API)
def test_list_chat_rooms(client):
    """Test listing all chat rooms"""
    # Create multiple rooms
    client.post("/api/chat/rooms", json={"name": "Room 1", "description": "First room"})
    client.post("/api/chat/rooms", json={"name": "Room 2", "description": "Second room"})
    client.post("/api/chat/rooms", json={"name": "Room 3"})
    
    # List rooms
    response = client.get("/api/chat/rooms")
    
    assert response.status_code == 200
    rooms = response.json()
    assert len(rooms) == 3
    assert rooms[0]["name"] in ["Room 1", "Room 2", "Room 3"]

# Test 3: Get Message History (REST API)
def test_get_message_history(client):
    """Test retrieving message history for a room"""
    # Create a room
    room_response = client.post(
        "/api/chat/rooms",
        json={"name": "History Room"}
    )
    room_id = room_response.json()["id"]
    
    # Add messages directly to database
    db = TestSessionLocal()
    try:
        for i in range(5):
            message = MessageModel(
                room_id=room_id,
                username=f"User{i}",
                content=f"Message {i}",
                timestamp=datetime.utcnow()
            )
            db.add(message)
        db.commit()
    finally:
        db.close()
    
    # Get message history
    response = client.get(f"/api/chat/rooms/{room_id}/messages")
    
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) == 5
    assert messages[0]["content"] == "Message 0"
    assert messages[4]["content"] == "Message 4"

def test_get_messages_nonexistent_room(client):
    """Test getting messages from a room that doesn't exist"""
    response = client.get("/api/chat/rooms/99999/messages")
    assert response.status_code == 404

# Test 4: Delete Chat Room (REST API)
def test_delete_chat_room(client):
    """Test deleting a chat room and its messages"""
    # Create a room with messages
    room_response = client.post(
        "/api/chat/rooms",
        json={"name": "Delete Me"}
    )
    room_id = room_response.json()["id"]
    
    # Add a message
    db = TestSessionLocal()
    try:
        message = MessageModel(
            room_id=room_id,
            username="TestUser",
            content="Test message",
            timestamp=datetime.utcnow()
        )
        db.add(message)
        db.commit()
    finally:
        db.close()
    
    # Delete the room
    delete_response = client.delete(f"/api/chat/rooms/{room_id}")
    assert delete_response.status_code == 200
    
    # Verify room is deleted
    get_response = client.get(f"/api/chat/rooms/{room_id}/messages")
    assert get_response.status_code == 404
    
    # Verify messages are deleted
    db = TestSessionLocal()
    try:
        messages = db.query(MessageModel).filter(MessageModel.room_id == room_id).all()
        assert len(messages) == 0
    finally:
        db.close()

# Test 5: WebSocket Connection and Authentication
def test_websocket_connection(client):
    """Test WebSocket connection and authentication"""
    # Create a room
    room_response = client.post(
        "/api/chat/rooms",
        json={"name": "WebSocket Room"}
    )
    room_id = room_response.json()["id"]
    
    # Connect via WebSocket
    with client.websocket_connect(f"/ws/chat/{room_id}") as websocket:
        # Send authentication
        websocket.send_json({"username": "TestUser"})
        
        # Receive connection confirmation
        data = websocket.receive_json()
        assert data["type"] == "connected"
        assert data["username"] == "TestUser"
        assert data["room_id"] == room_id
        
        # Receive users list
        data = websocket.receive_json()
        assert data["type"] == "users_list"
        assert "TestUser" in data["users"]

def test_websocket_invalid_room(client):
    """Test WebSocket connection to non-existent room"""
    with client.websocket_connect(f"/ws/chat/99999") as websocket:
        # Send authentication
        websocket.send_json({"username": "TestUser"})
        
        # Receive error
        data = websocket.receive_json()
        assert data["type"] == "error"
        assert "not found" in data["content"].lower()

# Test 6: Message Broadcasting
def test_message_broadcasting(client):
    """Test that messages are broadcast to all connected users"""
    # Create a room
    room_response = client.post(
        "/api/chat/rooms",
        json={"name": "Broadcast Room"}
    )
    room_id = room_response.json()["id"]
    
    # Connect two users
    with client.websocket_connect(f"/ws/chat/{room_id}") as ws1, \
         client.websocket_connect(f"/ws/chat/{room_id}") as ws2:
        
        # Authenticate both users
        ws1.send_json({"username": "User1"})
        ws2.send_json({"username": "User2"})
        
        # Clear initial messages (connected, users_list, join notifications)
        for _ in range(3):
            ws1.receive_json()
        for _ in range(4):  # User2 also receives User1's join notification
            ws2.receive_json()
        
        # User1 sends a message
        ws1.send_json({
            "type": "message",
            "content": "Hello from User1"
        })
        
        # Both users should receive the message
        msg1 = ws1.receive_json()
        msg2 = ws2.receive_json()
        
        assert msg1["type"] == "message"
        assert msg1["content"] == "Hello from User1"
        assert msg1["username"] == "User1"
        
        assert msg2["type"] == "message"
        assert msg2["content"] == "Hello from User1"
        assert msg2["username"] == "User1"
        
        # Verify message was saved to database
        db = TestSessionLocal()
        try:
            messages = db.query(MessageModel).filter(
                MessageModel.room_id == room_id,
                MessageModel.username == "User1"
            ).all()
            assert len(messages) == 1
            assert messages[0].content == "Hello from User1"
        finally:
            db.close()

# Test 7: Typing Indicators
def test_typing_indicators(client):
    """Test typing indicator functionality"""
    # Create a room
    room_response = client.post(
        "/api/chat/rooms",
        json={"name": "Typing Room"}
    )
    room_id = room_response.json()["id"]
    
    # Connect two users
    with client.websocket_connect(f"/ws/chat/{room_id}") as ws1, \
         client.websocket_connect(f"/ws/chat/{room_id}") as ws2:
        
        # Authenticate
        ws1.send_json({"username": "User1"})
        ws2.send_json({"username": "User2"})
        
        # Clear initial messages
        for _ in range(3):
            ws1.receive_json()
        for _ in range(4):
            ws2.receive_json()
        
        # User1 starts typing
        ws1.send_json({"type": "typing", "is_typing": True})
        
        # Both users should receive typing notification
        typing1 = ws1.receive_json()
        typing2 = ws2.receive_json()
        
        assert typing1["type"] == "typing"
        assert "User1" in typing1["users"]
        
        assert typing2["type"] == "typing"
        assert "User1" in typing2["users"]
        
        # User1 stops typing
        ws1.send_json({"type": "typing", "is_typing": False})
        
        # Typing list should be updated
        typing1 = ws1.receive_json()
        typing2 = ws2.receive_json()
        
        assert typing1["type"] == "typing"
        assert "User1" not in typing1["users"]
        
        assert typing2["type"] == "typing"
        assert "User1" not in typing2["users"]

# Test 8: Connection Handling - User Join/Leave
def test_user_join_leave_notifications(client):
    """Test that users receive notifications when others join/leave"""
    # Create a room
    room_response = client.post(
        "/api/chat/rooms",
        json={"name": "Join/Leave Room"}
    )
    room_id = room_response.json()["id"]
    
    # Connect first user
    with client.websocket_connect(f"/ws/chat/{room_id}") as ws1:
        ws1.send_json({"username": "User1"})
        
        # Clear initial messages
        for _ in range(2):
            ws1.receive_json()
        
        # Connect second user
        with client.websocket_connect(f"/ws/chat/{room_id}") as ws2:
            ws2.send_json({"username": "User2"})
            
            # User1 should receive join notification
            join_msg = ws1.receive_json()
            assert join_msg["type"] == "system"
            assert "User2" in join_msg["content"]
            assert "joined" in join_msg["content"].lower()
            
            # User1 should receive updated users list
            users_msg = ws1.receive_json()
            assert users_msg["type"] == "users_list"
            assert "User1" in users_msg["users"]
            assert "User2" in users_msg["users"]
            assert users_msg["count"] == 2
        
        # After ws2 closes, User1 should receive leave notification
        leave_msg = ws1.receive_json()
        assert leave_msg["type"] == "system"
        assert "User2" in leave_msg["content"]
        assert "left" in leave_msg["content"].lower()
        
        # User1 should receive updated users list
        users_msg = ws1.receive_json()
        assert users_msg["type"] == "users_list"
        assert "User1" in users_msg["users"]
        assert "User2" not in users_msg["users"]
        assert users_msg["count"] == 1

# Test 9: Room Deletion with Active Connections
def test_room_deletion_with_active_connections(client):
    """Test that active users are notified when their room is deleted"""
    # Create a room
    room_response = client.post(
        "/api/chat/rooms",
        json={"name": "To Be Deleted"}
    )
    room_id = room_response.json()["id"]
    
    # Connect a user
    with client.websocket_connect(f"/ws/chat/{room_id}") as ws:
        ws.send_json({"username": "User1"})
        
        # Clear initial messages
        for _ in range(2):
            ws.receive_json()
        
        # Delete the room
        delete_response = client.delete(f"/api/chat/rooms/{room_id}")
        assert delete_response.status_code == 200
        
        # User should receive room_deleted notification
        data = ws.receive_json()
        assert data["type"] == "room_deleted"
        assert "deleted" in data["message"].lower()

# Test 10: Multiple Messages in Sequence
def test_multiple_messages_sequence(client):
    """Test sending multiple messages in quick succession"""
    # Create a room
    room_response = client.post(
        "/api/chat/rooms",
        json={"name": "Multi Message Room"}
    )
    room_id = room_response.json()["id"]
    
    with client.websocket_connect(f"/ws/chat/{room_id}") as ws:
        ws.send_json({"username": "User1"})
        
        # Clear initial messages
        for _ in range(2):
            ws.receive_json()
        
        # Send multiple messages
        messages_to_send = ["Message 1", "Message 2", "Message 3", "Message 4", "Message 5"]
        
        for msg in messages_to_send:
            ws.send_json({"type": "message", "content": msg})
        
        # Receive all messages
        received_messages = []
        for _ in range(5):
            data = ws.receive_json()
            assert data["type"] == "message"
            received_messages.append(data["content"])
        
        assert received_messages == messages_to_send
        
        # Verify all messages were saved
        db = TestSessionLocal()
        try:
            db_messages = db.query(MessageModel).filter(
                MessageModel.room_id == room_id
            ).order_by(MessageModel.timestamp).all()
            assert len(db_messages) == 5
            for i, msg in enumerate(db_messages):
                assert msg.content == messages_to_send[i]
        finally:
            db.close()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

