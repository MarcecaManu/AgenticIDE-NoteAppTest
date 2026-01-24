"""
Tests for WebSocket functionality.
"""
import pytest
import json
import asyncio
from fastapi.testclient import TestClient


@pytest.mark.asyncio
async def test_websocket_connect_to_nonexistent_room(client):
    """Test WebSocket connection to a non-existent room."""
    with pytest.raises(Exception):
        with client.websocket_connect("/ws/chat/nonexistent-id?username=TestUser"):
            pass


@pytest.mark.asyncio
async def test_websocket_connect_and_disconnect(client):
    """Test basic WebSocket connection and disconnection."""
    # Create a room
    response = client.post("/api/chat/rooms", json={"name": "WebSocket Test Room"})
    room_id = response.json()["id"]
    
    # Connect to WebSocket
    with client.websocket_connect(f"/ws/chat/{room_id}?username=TestUser") as websocket:
        # Receive user list message
        data = websocket.receive_json()
        assert data["type"] == "user_list"
        assert "TestUser" in data["data"]["users"]


@pytest.mark.asyncio
async def test_websocket_send_message(client):
    """Test sending a message through WebSocket."""
    # Create a room
    response = client.post("/api/chat/rooms", json={"name": "Message Test Room"})
    room_id = response.json()["id"]
    
    # Connect to WebSocket
    with client.websocket_connect(f"/ws/chat/{room_id}?username=TestUser") as websocket:
        # Skip initial user list message
        websocket.receive_json()
        
        # Send a message
        websocket.send_json({
            "type": "message",
            "content": "Hello, World!"
        })
        
        # Receive the broadcasted message
        data = websocket.receive_json()
        assert data["type"] == "message"
        assert data["data"]["username"] == "TestUser"
        assert data["data"]["content"] == "Hello, World!"
        assert "id" in data["data"]
        assert "timestamp" in data["data"]


@pytest.mark.asyncio
async def test_websocket_message_broadcasting(client):
    """Test message broadcasting to multiple users."""
    # Create a room
    response = client.post("/api/chat/rooms", json={"name": "Broadcast Test Room"})
    room_id = response.json()["id"]
    
    # Connect two users
    with client.websocket_connect(f"/ws/chat/{room_id}?username=User1") as ws1:
        with client.websocket_connect(f"/ws/chat/{room_id}?username=User2") as ws2:
            # Clear initial messages
            ws1.receive_json()  # User1's user list
            ws2.receive_json()  # User2's user list
            
            # User1 should receive join notification for User2
            join_msg = ws1.receive_json()
            assert join_msg["type"] == "join"
            assert "User2" in join_msg["data"]["message"]
            
            # User1 sends a message
            ws1.send_json({
                "type": "message",
                "content": "Hello from User1"
            })
            
            # Both users should receive the message
            msg1 = ws1.receive_json()
            msg2 = ws2.receive_json()
            
            assert msg1["type"] == "message"
            assert msg2["type"] == "message"
            assert msg1["data"]["content"] == "Hello from User1"
            assert msg2["data"]["content"] == "Hello from User1"


@pytest.mark.asyncio
async def test_websocket_typing_indicator(client):
    """Test typing indicator functionality."""
    # Create a room
    response = client.post("/api/chat/rooms", json={"name": "Typing Test Room"})
    room_id = response.json()["id"]
    
    # Connect two users
    with client.websocket_connect(f"/ws/chat/{room_id}?username=User1") as ws1:
        with client.websocket_connect(f"/ws/chat/{room_id}?username=User2") as ws2:
            # Clear initial messages
            ws1.receive_json()  # User1's user list
            ws2.receive_json()  # User2's user list
            ws1.receive_json()  # User1's join notification for User2
            
            # User1 starts typing
            ws1.send_json({
                "type": "typing",
                "is_typing": True
            })
            
            # User2 should receive typing indicator
            typing_msg = ws2.receive_json()
            assert typing_msg["type"] == "typing"
            assert typing_msg["data"]["username"] == "User1"
            assert typing_msg["data"]["is_typing"] is True


@pytest.mark.asyncio
async def test_websocket_join_leave_notifications(client):
    """Test join and leave notifications."""
    # Create a room
    response = client.post("/api/chat/rooms", json={"name": "Join/Leave Test Room"})
    room_id = response.json()["id"]
    
    with client.websocket_connect(f"/ws/chat/{room_id}?username=User1") as ws1:
        ws1.receive_json()  # Clear user list
        
        # User2 joins
        with client.websocket_connect(f"/ws/chat/{room_id}?username=User2") as ws2:
            ws2.receive_json()  # Clear user list for User2
            
            # User1 should receive join notification
            join_msg = ws1.receive_json()
            assert join_msg["type"] == "join"
            assert "User2" in join_msg["data"]["message"]
        
        # User1 should receive leave notification after User2 disconnects
        leave_msg = ws1.receive_json()
        assert leave_msg["type"] == "leave"
        assert "User2" in leave_msg["data"]["message"]


@pytest.mark.asyncio
async def test_message_persistence(client):
    """Test that messages are persisted in the database."""
    # Create a room
    response = client.post("/api/chat/rooms", json={"name": "Persistence Test Room"})
    room_id = response.json()["id"]
    
    # Send messages through WebSocket
    with client.websocket_connect(f"/ws/chat/{room_id}?username=TestUser") as websocket:
        websocket.receive_json()  # Clear user list
        
        # Send two messages
        websocket.send_json({"type": "message", "content": "Message 1"})
        websocket.receive_json()  # Receive broadcast
        
        websocket.send_json({"type": "message", "content": "Message 2"})
        websocket.receive_json()  # Receive broadcast
    
    # Retrieve messages via REST API
    messages_response = client.get(f"/api/chat/rooms/{room_id}/messages")
    messages = messages_response.json()
    
    assert len(messages) == 2
    assert messages[0]["content"] == "Message 1"
    assert messages[1]["content"] == "Message 2"
    assert all(msg["username"] == "TestUser" for msg in messages)

