"""
Comprehensive test suite for Real-time Chat System
Tests REST endpoints, WebSocket connections, message broadcasting, and room management
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json

import sys
sys.path.insert(0, '../backend')

from main import app
from database import Base, get_db
from models import Room, Message

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_chat.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def test_db():
    """Create test database tables before each test and drop after"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(test_db):
    """Create test client"""
    return TestClient(app)


# Test 1: REST API - Create Room
def test_create_room(client):
    """Test creating a new chat room via REST API"""
    response = client.post(
        "/api/chat/rooms",
        json={"name": "Test Room"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Room"
    assert "id" in data
    assert "created_at" in data


# Test 2: REST API - Create Duplicate Room (Error Handling)
def test_create_duplicate_room(client):
    """Test that creating a duplicate room returns an error"""
    client.post("/api/chat/rooms", json={"name": "Test Room"})
    
    # Try creating same room again
    response = client.post("/api/chat/rooms", json={"name": "Test Room"})
    
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


# Test 3: REST API - List Rooms
def test_list_rooms(client):
    """Test listing all chat rooms"""
    # Create some rooms
    client.post("/api/chat/rooms", json={"name": "Room 1"})
    client.post("/api/chat/rooms", json={"name": "Room 2"})
    client.post("/api/chat/rooms", json={"name": "Room 3"})
    
    response = client.get("/api/chat/rooms")
    
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 3
    assert len(data["rooms"]) == 3
    room_names = [room["name"] for room in data["rooms"]]
    assert "Room 1" in room_names
    assert "Room 2" in room_names
    assert "Room 3" in room_names


# Test 4: REST API - Get Room Messages
def test_get_room_messages(client):
    """Test retrieving message history for a room"""
    # Create a room
    room_response = client.post("/api/chat/rooms", json={"name": "Test Room"})
    room_id = room_response.json()["id"]
    
    # Initially, room should have no messages
    response = client.get(f"/api/chat/rooms/{room_id}/messages")
    assert response.status_code == 200
    assert len(response.json()) == 0
    
    # Add messages via database (simulating WebSocket messages)
    db = next(override_get_db())
    msg1 = Message(room_id=room_id, username="User1", content="Hello")
    msg2 = Message(room_id=room_id, username="User2", content="Hi there")
    db.add(msg1)
    db.add(msg2)
    db.commit()
    
    # Get messages again
    response = client.get(f"/api/chat/rooms/{room_id}/messages")
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) == 2
    assert messages[0]["content"] == "Hello"
    assert messages[1]["content"] == "Hi there"


# Test 5: REST API - Delete Room
def test_delete_room(client):
    """Test deleting a chat room and its messages"""
    # Create a room
    room_response = client.post("/api/chat/rooms", json={"name": "Test Room"})
    room_id = room_response.json()["id"]
    
    # Add a message
    db = next(override_get_db())
    msg = Message(room_id=room_id, username="User1", content="Test message")
    db.add(msg)
    db.commit()
    
    # Delete the room
    response = client.delete(f"/api/chat/rooms/{room_id}")
    assert response.status_code == 204
    
    # Verify room is deleted
    response = client.get(f"/api/chat/rooms/{room_id}/messages")
    assert response.status_code == 404


# Test 6: REST API - Delete Non-existent Room
def test_delete_nonexistent_room(client):
    """Test deleting a room that doesn't exist"""
    response = client.delete("/api/chat/rooms/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


# Test 7: WebSocket - Connection and Join
def test_websocket_connection(client):
    """Test WebSocket connection and join notification"""
    # Create a room
    room_response = client.post("/api/chat/rooms", json={"name": "Test Room"})
    room_id = room_response.json()["id"]
    
    # Connect to WebSocket
    with client.websocket_connect(f"/ws/chat/{room_id}?username=TestUser") as websocket:
        # Should receive users list
        data = websocket.receive_json()
        assert data["type"] == "users_list"
        assert "TestUser" in data["users"]


# Test 8: WebSocket - Message Broadcasting
def test_websocket_message_broadcasting(client):
    """Test that messages are broadcast to all connected users"""
    # Create a room
    room_response = client.post("/api/chat/rooms", json={"name": "Test Room"})
    room_id = room_response.json()["id"]
    
    # Connect two users
    with client.websocket_connect(f"/ws/chat/{room_id}?username=User1") as ws1:
        with client.websocket_connect(f"/ws/chat/{room_id}?username=User2") as ws2:
            # Clear initial messages (users list)
            ws1.receive_json()  # User1's users list
            ws2.receive_json()  # User2's users list
            
            # User2 should receive User2 join notification
            join_msg = ws1.receive_json()
            assert join_msg["type"] == "join"
            assert "User2" in join_msg["content"]
            
            # User1 sends a message
            ws1.send_json({
                "type": "message",
                "content": "Hello from User1"
            })
            
            # Both users should receive the message
            msg1 = ws1.receive_json()
            msg2 = ws2.receive_json()
            
            assert msg1["type"] == "message"
            assert msg1["username"] == "User1"
            assert msg1["content"] == "Hello from User1"
            
            assert msg2["type"] == "message"
            assert msg2["username"] == "User1"
            assert msg2["content"] == "Hello from User1"


# Test 9: WebSocket - Typing Indicator
def test_websocket_typing_indicator(client):
    """Test typing indicator broadcasting"""
    # Create a room
    room_response = client.post("/api/chat/rooms", json={"name": "Test Room"})
    room_id = room_response.json()["id"]
    
    # Connect two users
    with client.websocket_connect(f"/ws/chat/{room_id}?username=User1") as ws1:
        with client.websocket_connect(f"/ws/chat/{room_id}?username=User2") as ws2:
            # Clear initial messages
            ws1.receive_json()  # User1's users list
            ws2.receive_json()  # User2's users list
            ws1.receive_json()  # User1 receives User2 join
            
            # User1 sends typing indicator
            ws1.send_json({"type": "typing"})
            
            # User2 should receive typing indicator
            typing_msg = ws2.receive_json()
            assert typing_msg["type"] == "typing"
            assert typing_msg["username"] == "User1"


# Test 10: WebSocket - Connection to Non-existent Room
def test_websocket_invalid_room(client):
    """Test that connecting to non-existent room fails gracefully"""
    with pytest.raises(Exception):
        # This should close with error code
        with client.websocket_connect("/ws/chat/999?username=TestUser") as websocket:
            pass


# Test 11: WebSocket - Leave Notification
def test_websocket_leave_notification(client):
    """Test that users are notified when someone leaves"""
    # Create a room
    room_response = client.post("/api/chat/rooms", json={"name": "Test Room"})
    room_id = room_response.json()["id"]
    
    # Connect two users
    with client.websocket_connect(f"/ws/chat/{room_id}?username=User1") as ws1:
        ws2 = client.websocket_connect(f"/ws/chat/{room_id}?username=User2")
        ws2.__enter__()
        
        # Clear initial messages
        ws1.receive_json()
        ws2.receive_json()
        ws1.receive_json()  # Join notification
        
        # User2 disconnects
        ws2.close()
        
        # User1 should receive leave notification
        leave_msg = ws1.receive_json()
        assert leave_msg["type"] == "leave"
        assert "User2" in leave_msg["content"]


# Test 12: Data Persistence
def test_message_persistence(client):
    """Test that messages are persisted to database"""
    # Create a room
    room_response = client.post("/api/chat/rooms", json={"name": "Test Room"})
    room_id = room_response.json()["id"]
    
    # Send messages via WebSocket
    with client.websocket_connect(f"/ws/chat/{room_id}?username=User1") as websocket:
        websocket.receive_json()  # Clear users list
        
        websocket.send_json({
            "type": "message",
            "content": "Persistent message"
        })
        
        websocket.receive_json()  # Receive echo
    
    # Verify message was saved
    db = next(override_get_db())
    messages = db.query(Message).filter(Message.room_id == room_id).all()
    assert len(messages) == 1
    assert messages[0].content == "Persistent message"
    assert messages[0].username == "User1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

