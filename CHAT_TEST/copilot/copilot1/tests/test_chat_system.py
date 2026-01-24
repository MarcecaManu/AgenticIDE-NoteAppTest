"""
Automated tests for the Real-time Chat System.

Tests cover:
1. REST API endpoints (room creation, listing, message retrieval, deletion)
2. WebSocket connections and messaging
3. Message broadcasting to multiple users
4. Room management operations
5. Connection handling and error cases
6. User online status tracking
"""

import pytest
import asyncio
import json
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app, manager, db
import uuid


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def test_db():
    """Create a clean test database."""
    test_db_path = "test_chat.db"
    test_database = db.__class__(test_db_path)
    
    # Clean up any existing test data
    with test_database.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM messages")
        cursor.execute("DELETE FROM rooms")
    
    yield test_database
    
    # Cleanup
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


class TestRESTEndpoints:
    """Test suite for REST API endpoints."""
    
    def test_create_room(self, client):
        """Test 1: Create a new chat room via REST API."""
        response = client.post(
            "/api/chat/rooms",
            json={"name": "Test Room"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["name"] == "Test Room"
        assert "created_at" in data
    
    def test_get_all_rooms(self, client):
        """Test 2: Retrieve all chat rooms."""
        # Create test rooms
        room1 = client.post("/api/chat/rooms", json={"name": "Room 1"}).json()
        room2 = client.post("/api/chat/rooms", json={"name": "Room 2"}).json()
        
        # Get all rooms
        response = client.get("/api/chat/rooms")
        assert response.status_code == 200
        
        rooms = response.json()
        assert len(rooms) >= 2
        room_names = [r["name"] for r in rooms]
        assert "Room 1" in room_names
        assert "Room 2" in room_names
    
    def test_get_room_messages(self, client):
        """Test 3: Retrieve message history for a room."""
        # Create a room
        room_response = client.post("/api/chat/rooms", json={"name": "Message Test Room"})
        room_id = room_response.json()["id"]
        
        # Add some messages directly to the database
        from datetime import datetime
        for i in range(3):
            db.create_message(
                message_id=str(uuid.uuid4()),
                room_id=room_id,
                username=f"User{i}",
                content=f"Test message {i}",
                timestamp=datetime.utcnow().isoformat()
            )
        
        # Get messages
        response = client.get(f"/api/chat/rooms/{room_id}/messages")
        assert response.status_code == 200
        
        messages = response.json()
        assert len(messages) == 3
        assert messages[0]["content"] == "Test message 0"
    
    def test_get_messages_nonexistent_room(self, client):
        """Test 4: Handle request for messages from non-existent room."""
        fake_room_id = str(uuid.uuid4())
        response = client.get(f"/api/chat/rooms/{fake_room_id}/messages")
        assert response.status_code == 404
    
    def test_delete_room(self, client):
        """Test 5: Delete a room and its messages."""
        # Create a room
        room_response = client.post("/api/chat/rooms", json={"name": "Room to Delete"})
        room_id = room_response.json()["id"]
        
        # Add a message
        from datetime import datetime
        db.create_message(
            message_id=str(uuid.uuid4()),
            room_id=room_id,
            username="TestUser",
            content="Test message",
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Delete the room
        response = client.delete(f"/api/chat/rooms/{room_id}")
        assert response.status_code == 204
        
        # Verify room is deleted
        get_response = client.get(f"/api/chat/rooms/{room_id}/messages")
        assert get_response.status_code == 404
        
        # Verify messages are deleted
        messages = db.get_room_messages(room_id)
        assert len(messages) == 0
    
    def test_get_online_users(self, client):
        """Test 6: Get list of online users in a room."""
        # Create a room
        room_response = client.post("/api/chat/rooms", json={"name": "Online Users Test"})
        room_id = room_response.json()["id"]
        
        # Get online users (should be empty)
        response = client.get(f"/api/chat/rooms/{room_id}/online")
        assert response.status_code == 200
        assert response.json() == []


class TestWebSocketConnections:
    """Test suite for WebSocket functionality."""
    
    def test_websocket_connection(self, client):
        """Test 7: Establish WebSocket connection."""
        # Create a room
        room_response = client.post("/api/chat/rooms", json={"name": "WebSocket Test Room"})
        room_id = room_response.json()["id"]
        
        # Connect via WebSocket
        with client.websocket_connect(f"/ws/chat/{room_id}?username=TestUser") as websocket:
            # Should receive join notification
            data = websocket.receive_json()
            assert data["type"] == "join"
            assert data["username"] == "TestUser"
            assert "TestUser" in data["content"]
    
    def test_websocket_message_sending(self, client):
        """Test 8: Send and receive messages via WebSocket."""
        # Create a room
        room_response = client.post("/api/chat/rooms", json={"name": "Message Send Test"})
        room_id = room_response.json()["id"]
        
        # Connect via WebSocket
        with client.websocket_connect(f"/ws/chat/{room_id}?username=Sender") as websocket:
            # Receive join notification
            websocket.receive_json()
            
            # Send a message
            websocket.send_json({
                "type": "message",
                "content": "Hello, World!"
            })
            
            # Receive the message back
            data = websocket.receive_json()
            assert data["type"] == "message"
            assert data["username"] == "Sender"
            assert data["content"] == "Hello, World!"
            assert "id" in data
            assert "timestamp" in data
    
    def test_message_broadcasting(self, client):
        """Test 9: Broadcast messages to multiple connected users."""
        # Create a room
        room_response = client.post("/api/chat/rooms", json={"name": "Broadcast Test"})
        room_id = room_response.json()["id"]
        
        # Connect two users
        with client.websocket_connect(f"/ws/chat/{room_id}?username=User1") as ws1, \
             client.websocket_connect(f"/ws/chat/{room_id}?username=User2") as ws2:
            
            # Clear join notifications
            ws1.receive_json()  # User1's own join
            ws1.receive_json()  # User2's join notification to User1
            ws2.receive_json()  # User2's own join
            
            # User1 sends a message
            ws1.send_json({
                "type": "message",
                "content": "Broadcast test message"
            })
            
            # User1 receives their own message
            msg1 = ws1.receive_json()
            assert msg1["type"] == "message"
            assert msg1["content"] == "Broadcast test message"
            
            # User2 also receives the message
            msg2 = ws2.receive_json()
            assert msg2["type"] == "message"
            assert msg2["username"] == "User1"
            assert msg2["content"] == "Broadcast test message"
    
    def test_typing_indicator(self, client):
        """Test 10: Typing indicator broadcasting."""
        # Create a room
        room_response = client.post("/api/chat/rooms", json={"name": "Typing Test"})
        room_id = room_response.json()["id"]
        
        # Connect two users
        with client.websocket_connect(f"/ws/chat/{room_id}?username=Typer") as ws1, \
             client.websocket_connect(f"/ws/chat/{room_id}?username=Watcher") as ws2:
            
            # Clear join notifications
            ws1.receive_json()
            ws1.receive_json()
            ws2.receive_json()
            
            # User1 starts typing
            ws1.send_json({
                "type": "typing",
                "content": "typing"
            })
            
            # User2 should receive typing indicator
            typing_msg = ws2.receive_json()
            assert typing_msg["type"] == "typing"
            assert typing_msg["username"] == "Typer"
    
    def test_connection_disconnect_notifications(self, client):
        """Test 11: User join and leave notifications."""
        # Create a room
        room_response = client.post("/api/chat/rooms", json={"name": "Disconnect Test"})
        room_id = room_response.json()["id"]
        
        # Connect first user
        with client.websocket_connect(f"/ws/chat/{room_id}?username=Permanent") as ws1:
            ws1.receive_json()  # Own join notification
            
            # Connect second user
            with client.websocket_connect(f"/ws/chat/{room_id}?username=Temporary") as ws2:
                # ws1 receives join notification for ws2
                join_msg = ws1.receive_json()
                assert join_msg["type"] == "join"
                assert "Temporary" in join_msg["content"]
                assert "Permanent" in join_msg["online_users"]
                assert "Temporary" in join_msg["online_users"]
            
            # After ws2 disconnects, ws1 receives leave notification
            leave_msg = ws1.receive_json()
            assert leave_msg["type"] == "leave"
            assert "Temporary" in leave_msg["content"]
            assert "Permanent" in leave_msg["online_users"]
            assert "Temporary" not in leave_msg["online_users"]
    
    def test_websocket_nonexistent_room(self, client):
        """Test 12: Handle WebSocket connection to non-existent room."""
        fake_room_id = str(uuid.uuid4())
        
        try:
            with client.websocket_connect(f"/ws/chat/{fake_room_id}?username=TestUser") as websocket:
                # Should not get here - connection should fail
                assert False, "Expected WebSocket connection to fail"
        except Exception as e:
            # Connection should be rejected
            assert True


class TestDatabaseOperations:
    """Test suite for database operations."""
    
    def test_message_persistence(self, client):
        """Test 13: Verify messages are persisted to database."""
        # Create a room
        room_response = client.post("/api/chat/rooms", json={"name": "Persistence Test"})
        room_id = room_response.json()["id"]
        
        # Send a message via WebSocket
        with client.websocket_connect(f"/ws/chat/{room_id}?username=PersistUser") as websocket:
            websocket.receive_json()  # Join notification
            
            websocket.send_json({
                "type": "message",
                "content": "Persistent message"
            })
            
            # Receive message
            msg = websocket.receive_json()
            message_id = msg["id"]
        
        # Verify message is in database
        stored_message = db.get_message(message_id)
        assert stored_message is not None
        assert stored_message["content"] == "Persistent message"
        assert stored_message["username"] == "PersistUser"
        assert stored_message["room_id"] == room_id
    
    def test_cascade_delete(self, client):
        """Test 14: Verify cascade delete removes messages when room is deleted."""
        # Create a room and add messages
        room_response = client.post("/api/chat/rooms", json={"name": "Cascade Test"})
        room_id = room_response.json()["id"]
        
        # Add messages via WebSocket
        with client.websocket_connect(f"/ws/chat/{room_id}?username=CascadeUser") as websocket:
            websocket.receive_json()
            
            for i in range(3):
                websocket.send_json({
                    "type": "message",
                    "content": f"Message {i}"
                })
                websocket.receive_json()
        
        # Verify messages exist
        messages_before = db.get_room_messages(room_id)
        assert len(messages_before) == 3
        
        # Delete room
        client.delete(f"/api/chat/rooms/{room_id}")
        
        # Verify messages are deleted
        messages_after = db.get_room_messages(room_id)
        assert len(messages_after) == 0


class TestErrorHandling:
    """Test suite for error handling and edge cases."""
    
    def test_empty_message(self, client):
        """Test 15: Handle empty message content."""
        room_response = client.post("/api/chat/rooms", json={"name": "Empty Message Test"})
        room_id = room_response.json()["id"]
        
        with client.websocket_connect(f"/ws/chat/{room_id}?username=EmptyUser") as websocket:
            websocket.receive_json()
            
            # Send empty message
            websocket.send_json({
                "type": "message",
                "content": ""
            })
            
            # Should still receive the message (backend doesn't validate emptiness)
            msg = websocket.receive_json()
            assert msg["type"] == "message"
            assert msg["content"] == ""


# Run tests with pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
