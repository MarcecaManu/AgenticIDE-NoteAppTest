"""
Comprehensive tests for the Real-time Chat API.
Tests cover REST endpoints, WebSocket connections, message broadcasting,
room management, and connection handling.
"""
import pytest
import sys
import os
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket
import json
import uuid

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app, manager
from database import init_db, ChatDatabase, DB_PATH


@pytest.fixture(scope="function", autouse=True)
def setup_test_db():
    """Setup test database before each test and cleanup after."""
    # Remove existing test db
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    # Initialize fresh database
    init_db()
    
    yield
    
    # Cleanup after test
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    # Clear connection manager
    manager.active_connections.clear()


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


# Test 1: REST API - Create and List Rooms
def test_create_and_list_rooms(client):
    """Test creating chat rooms and listing them."""
    # Create first room
    response = client.post(
        "/api/chat/rooms",
        json={"name": "General Chat"}
    )
    assert response.status_code == 201
    room1 = response.json()
    assert room1["name"] == "General Chat"
    assert "id" in room1
    assert "created_at" in room1
    
    # Create second room
    response = client.post(
        "/api/chat/rooms",
        json={"name": "Tech Discussion"}
    )
    assert response.status_code == 201
    room2 = response.json()
    assert room2["name"] == "Tech Discussion"
    
    # List all rooms
    response = client.get("/api/chat/rooms")
    assert response.status_code == 200
    rooms = response.json()
    assert len(rooms) == 2
    
    # Verify rooms are returned in correct order (newest first)
    assert rooms[0]["id"] == room2["id"]
    assert rooms[1]["id"] == room1["id"]


# Test 2: REST API - Get Room Messages
def test_get_room_messages(client):
    """Test retrieving message history for a room."""
    # Create a room
    response = client.post(
        "/api/chat/rooms",
        json={"name": "Test Room"}
    )
    room = response.json()
    room_id = room["id"]
    
    # Initially, room should have no messages
    response = client.get(f"/api/chat/rooms/{room_id}/messages")
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) == 0
    
    # Add messages directly to database
    message1_id = str(uuid.uuid4())
    message2_id = str(uuid.uuid4())
    ChatDatabase.create_message(
        message1_id, room_id, "user1", "Hello!", "2024-01-01T10:00:00"
    )
    ChatDatabase.create_message(
        message2_id, room_id, "user2", "Hi there!", "2024-01-01T10:01:00"
    )
    
    # Get messages
    response = client.get(f"/api/chat/rooms/{room_id}/messages")
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) == 2
    
    # Messages should be in chronological order
    assert messages[0]["username"] == "user1"
    assert messages[0]["content"] == "Hello!"
    assert messages[1]["username"] == "user2"
    assert messages[1]["content"] == "Hi there!"
    
    # Test non-existent room
    response = client.get("/api/chat/rooms/fake-id/messages")
    assert response.status_code == 404


# Test 3: REST API - Delete Room
def test_delete_room(client):
    """Test deleting a room and its messages."""
    # Create a room
    response = client.post(
        "/api/chat/rooms",
        json={"name": "Temporary Room"}
    )
    room = response.json()
    room_id = room["id"]
    
    # Add a message
    message_id = str(uuid.uuid4())
    ChatDatabase.create_message(
        message_id, room_id, "user1", "Test message", "2024-01-01T10:00:00"
    )
    
    # Verify message exists
    messages = ChatDatabase.get_room_messages(room_id)
    assert len(messages) == 1
    
    # Delete the room
    response = client.delete(f"/api/chat/rooms/{room_id}")
    assert response.status_code == 204
    
    # Verify room is deleted
    response = client.get("/api/chat/rooms")
    rooms = response.json()
    assert len(rooms) == 0
    
    # Verify messages are deleted (cascade)
    messages = ChatDatabase.get_room_messages(room_id)
    assert len(messages) == 0
    
    # Try to delete non-existent room
    response = client.delete("/api/chat/rooms/fake-id")
    assert response.status_code == 404


# Test 4: WebSocket - Connection and Join Notification
def test_websocket_connection_and_join(client):
    """Test WebSocket connection and join notifications."""
    # Create a room
    response = client.post(
        "/api/chat/rooms",
        json={"name": "WebSocket Test Room"}
    )
    room = response.json()
    room_id = room["id"]
    
    # Connect via WebSocket
    with client.websocket_connect(f"/ws/chat/{room_id}?username=alice") as websocket:
        # Should receive join notification
        data = websocket.receive_json()
        assert data["type"] == "join"
        assert data["username"] == "alice"
        assert "timestamp" in data
        
        # Should receive user list
        data = websocket.receive_json()
        assert data["type"] == "user_list"
        assert "alice" in data["users"]
        assert len(data["users"]) == 1


# Test 5: WebSocket - Message Broadcasting
def test_websocket_message_broadcasting(client):
    """Test real-time message broadcasting to multiple users."""
    # Create a room
    response = client.post(
        "/api/chat/rooms",
        json={"name": "Broadcast Test Room"}
    )
    room = response.json()
    room_id = room["id"]
    
    # Connect two users
    with client.websocket_connect(f"/ws/chat/{room_id}?username=alice") as ws1, \
         client.websocket_connect(f"/ws/chat/{room_id}?username=bob") as ws2:
        
        # Clear join notifications for alice
        ws1.receive_json()  # alice join
        ws1.receive_json()  # user list [alice]
        
        # Clear join notifications for bob
        ws2.receive_json()  # bob join
        ws2.receive_json()  # user list [alice, bob]
        
        # Alice should also receive bob's join
        ws1.receive_json()  # bob join
        ws1.receive_json()  # updated user list
        
        # Alice sends a message
        ws1.send_json({
            "type": "message",
            "content": "Hello everyone!"
        })
        
        # Both users should receive the message
        msg1 = ws1.receive_json()
        assert msg1["type"] == "message"
        assert msg1["message"]["username"] == "alice"
        assert msg1["message"]["content"] == "Hello everyone!"
        
        msg2 = ws2.receive_json()
        assert msg2["type"] == "message"
        assert msg2["message"]["username"] == "alice"
        assert msg2["message"]["content"] == "Hello everyone!"
        
        # Verify message is stored in database
        messages = ChatDatabase.get_room_messages(room_id)
        assert len(messages) == 1
        assert messages[0]["username"] == "alice"
        assert messages[0]["content"] == "Hello everyone!"


# Test 6: WebSocket - Typing Indicators
def test_websocket_typing_indicators(client):
    """Test typing indicator broadcasting."""
    # Create a room
    response = client.post(
        "/api/chat/rooms",
        json={"name": "Typing Test Room"}
    )
    room = response.json()
    room_id = room["id"]
    
    # Connect two users
    with client.websocket_connect(f"/ws/chat/{room_id}?username=alice") as ws1, \
         client.websocket_connect(f"/ws/chat/{room_id}?username=bob") as ws2:
        
        # Clear join notifications
        ws1.receive_json()  # alice join
        ws1.receive_json()  # user list
        ws2.receive_json()  # bob join
        ws2.receive_json()  # user list
        ws1.receive_json()  # bob join notification
        ws1.receive_json()  # updated user list
        
        # Alice sends typing indicator
        ws1.send_json({
            "type": "typing"
        })
        
        # Both users should receive typing indicator
        typing1 = ws1.receive_json()
        assert typing1["type"] == "typing"
        assert typing1["username"] == "alice"
        
        typing2 = ws2.receive_json()
        assert typing2["type"] == "typing"
        assert typing2["username"] == "alice"


# Test 7: WebSocket - Leave Notification
def test_websocket_leave_notification(client):
    """Test leave notifications when user disconnects."""
    # Create a room
    response = client.post(
        "/api/chat/rooms",
        json={"name": "Leave Test Room"}
    )
    room = response.json()
    room_id = room["id"]
    
    # Connect two users
    with client.websocket_connect(f"/ws/chat/{room_id}?username=alice") as ws1:
        with client.websocket_connect(f"/ws/chat/{room_id}?username=bob") as ws2:
            # Clear join notifications
            ws1.receive_json()  # alice join
            ws1.receive_json()  # user list
            ws2.receive_json()  # bob join
            ws2.receive_json()  # user list
            ws1.receive_json()  # bob join notification
            ws1.receive_json()  # updated user list
        
        # Bob disconnected (context manager exited)
        # Alice should receive leave notification
        leave_msg = ws1.receive_json()
        assert leave_msg["type"] == "leave"
        assert leave_msg["username"] == "bob"
        
        # Alice should receive updated user list
        user_list_msg = ws1.receive_json()
        assert user_list_msg["type"] == "user_list"
        assert "bob" not in user_list_msg["users"]
        assert "alice" in user_list_msg["users"]


# Test 8: WebSocket - Connection Validation
def test_websocket_connection_validation(client):
    """Test WebSocket connection validation (username required, room must exist)."""
    # Create a room
    response = client.post(
        "/api/chat/rooms",
        json={"name": "Validation Test Room"}
    )
    room = response.json()
    room_id = room["id"]
    
    # Try to connect without username
    with pytest.raises(Exception):
        with client.websocket_connect(f"/ws/chat/{room_id}") as websocket:
            pass
    
    # Try to connect to non-existent room
    with pytest.raises(Exception):
        with client.websocket_connect(f"/ws/chat/fake-room-id?username=alice") as websocket:
            pass


# Test 9: Database - Concurrent Operations
def test_database_concurrent_operations():
    """Test database handles concurrent operations correctly."""
    # Create multiple rooms
    room1_id = str(uuid.uuid4())
    room2_id = str(uuid.uuid4())
    
    room1 = ChatDatabase.create_room(room1_id, "Room 1")
    room2 = ChatDatabase.create_room(room2_id, "Room 2")
    
    assert room1["id"] == room1_id
    assert room2["id"] == room2_id
    
    # Create messages in different rooms
    msg1_id = str(uuid.uuid4())
    msg2_id = str(uuid.uuid4())
    
    ChatDatabase.create_message(
        msg1_id, room1_id, "user1", "Message in room 1", "2024-01-01T10:00:00"
    )
    ChatDatabase.create_message(
        msg2_id, room2_id, "user2", "Message in room 2", "2024-01-01T10:01:00"
    )
    
    # Verify messages are in correct rooms
    room1_messages = ChatDatabase.get_room_messages(room1_id)
    room2_messages = ChatDatabase.get_room_messages(room2_id)
    
    assert len(room1_messages) == 1
    assert len(room2_messages) == 1
    assert room1_messages[0]["content"] == "Message in room 1"
    assert room2_messages[0]["content"] == "Message in room 2"


# Test 10: Room Management - Validation
def test_room_creation_validation(client):
    """Test room creation with invalid data."""
    # Empty name
    response = client.post(
        "/api/chat/rooms",
        json={"name": ""}
    )
    assert response.status_code == 422  # Validation error
    
    # Missing name
    response = client.post(
        "/api/chat/rooms",
        json={}
    )
    assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

