import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app
from database import Base, get_db

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def client():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create test client
    with TestClient(app) as test_client:
        yield test_client
    
    # Drop tables after test
    Base.metadata.drop_all(bind=engine)


def test_root_endpoint(client):
    """Test the root endpoint returns correct message"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Real-time Chat API"


def test_create_room(client):
    """Test creating a new chat room"""
    response = client.post(
        "/api/chat/rooms",
        json={"name": "Test Room"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Room"
    assert "id" in data
    assert "created_at" in data


def test_create_duplicate_room(client):
    """Test that creating a duplicate room returns an error"""
    # Create first room
    client.post("/api/chat/rooms", json={"name": "Test Room"})
    
    # Try to create duplicate
    response = client.post("/api/chat/rooms", json={"name": "Test Room"})
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_list_rooms(client):
    """Test listing all chat rooms"""
    # Create multiple rooms
    client.post("/api/chat/rooms", json={"name": "Room 1"})
    client.post("/api/chat/rooms", json={"name": "Room 2"})
    client.post("/api/chat/rooms", json={"name": "Room 3"})
    
    # List rooms
    response = client.get("/api/chat/rooms")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["name"] == "Room 1"
    assert data[1]["name"] == "Room 2"
    assert data[2]["name"] == "Room 3"


def test_get_room_messages_empty(client):
    """Test getting messages from an empty room"""
    # Create room
    room_response = client.post("/api/chat/rooms", json={"name": "Test Room"})
    room_id = room_response.json()["id"]
    
    # Get messages
    response = client.get(f"/api/chat/rooms/{room_id}/messages")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


def test_get_room_messages_nonexistent(client):
    """Test getting messages from a non-existent room"""
    response = client.get("/api/chat/rooms/999/messages")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_delete_room(client):
    """Test deleting a room"""
    # Create room
    room_response = client.post("/api/chat/rooms", json={"name": "Test Room"})
    room_id = room_response.json()["id"]
    
    # Delete room
    response = client.delete(f"/api/chat/rooms/{room_id}")
    assert response.status_code == 204
    
    # Verify room is deleted
    get_response = client.get(f"/api/chat/rooms/{room_id}/messages")
    assert get_response.status_code == 404


def test_delete_nonexistent_room(client):
    """Test deleting a non-existent room"""
    response = client.delete("/api/chat/rooms/999")
    assert response.status_code == 404


def test_websocket_connection(client):
    """Test WebSocket connection to a chat room"""
    # Create room
    room_response = client.post("/api/chat/rooms", json={"name": "Test Room"})
    room_id = room_response.json()["id"]
    
    # Connect to WebSocket
    with client.websocket_connect(f"/ws/chat/{room_id}?username=TestUser") as websocket:
        # Should receive join message
        data = websocket.receive_json()
        assert data["type"] == "join"
        assert data["username"] == "TestUser"
        
        # Should receive user list
        data = websocket.receive_json()
        assert data["type"] == "user_list"
        assert "TestUser" in data["users"]


def test_websocket_nonexistent_room(client):
    """Test WebSocket connection to a non-existent room"""
    with pytest.raises(Exception):
        with client.websocket_connect("/ws/chat/999?username=TestUser") as websocket:
            pass


def test_websocket_message_broadcasting(client):
    """Test that messages are broadcast to all users in a room"""
    # Create room
    room_response = client.post("/api/chat/rooms", json={"name": "Test Room"})
    room_id = room_response.json()["id"]
    
    # Connect two users
    with client.websocket_connect(f"/ws/chat/{room_id}?username=User1") as ws1:
        with client.websocket_connect(f"/ws/chat/{room_id}?username=User2") as ws2:
            # Clear initial messages (join notifications and user lists)
            ws1.receive_json()  # User1 join
            ws1.receive_json()  # User list with User1
            ws1.receive_json()  # User2 join
            ws1.receive_json()  # User list with User1, User2
            
            ws2.receive_json()  # User2 join
            ws2.receive_json()  # User list with User1, User2
            
            # Send message from User1
            ws1.send_json({
                "type": "message",
                "content": "Hello from User1"
            })
            
            # Both users should receive the message
            msg1 = ws1.receive_json()
            assert msg1["type"] == "message"
            assert msg1["username"] == "User1"
            assert msg1["content"] == "Hello from User1"
            
            msg2 = ws2.receive_json()
            assert msg2["type"] == "message"
            assert msg2["username"] == "User1"
            assert msg2["content"] == "Hello from User1"


def test_websocket_typing_indicator(client):
    """Test typing indicator functionality"""
    # Create room
    room_response = client.post("/api/chat/rooms", json={"name": "Test Room"})
    room_id = room_response.json()["id"]
    
    # Connect two users
    with client.websocket_connect(f"/ws/chat/{room_id}?username=User1") as ws1:
        with client.websocket_connect(f"/ws/chat/{room_id}?username=User2") as ws2:
            # Clear initial messages
            ws1.receive_json()  # User1 join
            ws1.receive_json()  # User list
            ws1.receive_json()  # User2 join
            ws1.receive_json()  # User list
            
            ws2.receive_json()  # User2 join
            ws2.receive_json()  # User list
            
            # User1 starts typing
            ws1.send_json({
                "type": "typing",
                "is_typing": True
            })
            
            # Both users should receive typing notification
            typing1 = ws1.receive_json()
            assert typing1["type"] == "typing"
            assert "User1" in typing1["users"]
            
            typing2 = ws2.receive_json()
            assert typing2["type"] == "typing"
            assert "User1" in typing2["users"]
            
            # User1 stops typing
            ws1.send_json({
                "type": "typing",
                "is_typing": False
            })
            
            # Both users should receive updated typing notification
            typing1 = ws1.receive_json()
            assert typing1["type"] == "typing"
            assert "User1" not in typing1["users"]
            
            typing2 = ws2.receive_json()
            assert typing2["type"] == "typing"
            assert "User1" not in typing2["users"]


def test_websocket_leave_notification(client):
    """Test that users receive leave notifications"""
    # Create room
    room_response = client.post("/api/chat/rooms", json={"name": "Test Room"})
    room_id = room_response.json()["id"]
    
    # Connect two users
    with client.websocket_connect(f"/ws/chat/{room_id}?username=User1") as ws1:
        ws2 = client.websocket_connect(f"/ws/chat/{room_id}?username=User2")
        ws2.__enter__()
        
        # Clear initial messages
        ws1.receive_json()  # User1 join
        ws1.receive_json()  # User list
        ws1.receive_json()  # User2 join
        ws1.receive_json()  # User list
        
        ws2.receive_json()  # User2 join
        ws2.receive_json()  # User list
        
        # User2 disconnects
        ws2.__exit__(None, None, None)
        
        # User1 should receive leave notification
        leave_msg = ws1.receive_json()
        assert leave_msg["type"] == "leave"
        assert leave_msg["username"] == "User2"
        
        # User1 should receive updated user list
        user_list = ws1.receive_json()
        assert user_list["type"] == "user_list"
        assert "User2" not in user_list["users"]
        assert "User1" in user_list["users"]


def test_message_persistence(client):
    """Test that messages are persisted in the database"""
    # Create room
    room_response = client.post("/api/chat/rooms", json={"name": "Test Room"})
    room_id = room_response.json()["id"]
    
    # Send messages via WebSocket
    with client.websocket_connect(f"/ws/chat/{room_id}?username=TestUser") as websocket:
        # Clear initial messages
        websocket.receive_json()  # join
        websocket.receive_json()  # user list
        
        # Send multiple messages
        for i in range(3):
            websocket.send_json({
                "type": "message",
                "content": f"Message {i + 1}"
            })
            websocket.receive_json()  # receive broadcast
    
    # Retrieve messages via REST API
    response = client.get(f"/api/chat/rooms/{room_id}/messages")
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) == 3
    assert messages[0]["content"] == "Message 1"
    assert messages[1]["content"] == "Message 2"
    assert messages[2]["content"] == "Message 3"
    assert all(msg["username"] == "TestUser" for msg in messages)


def test_delete_room_deletes_messages(client):
    """Test that deleting a room also deletes its messages"""
    # Create room
    room_response = client.post("/api/chat/rooms", json={"name": "Test Room"})
    room_id = room_response.json()["id"]
    
    # Send messages
    with client.websocket_connect(f"/ws/chat/{room_id}?username=TestUser") as websocket:
        websocket.receive_json()  # join
        websocket.receive_json()  # user list
        
        websocket.send_json({
            "type": "message",
            "content": "Test message"
        })
        websocket.receive_json()  # receive broadcast
    
    # Verify message exists
    response = client.get(f"/api/chat/rooms/{room_id}/messages")
    assert len(response.json()) == 1
    
    # Delete room
    client.delete(f"/api/chat/rooms/{room_id}")
    
    # Verify room and messages are deleted
    response = client.get(f"/api/chat/rooms/{room_id}/messages")
    assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
