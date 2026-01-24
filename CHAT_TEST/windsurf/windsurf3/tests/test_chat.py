import pytest
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket
import sys
import os
import sqlite3
import json
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from main import app, init_db, get_db

@pytest.fixture(autouse=True)
def setup_test_db():
    if os.path.exists('chat.db'):
        os.remove('chat.db')
    init_db()
    yield
    if os.path.exists('chat.db'):
        os.remove('chat.db')

@pytest.fixture
def client():
    return TestClient(app)

def test_create_room(client):
    response = client.post(
        "/api/chat/rooms",
        json={"name": "Test Room"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Room"
    assert "id" in data
    assert "created_at" in data

def test_get_rooms(client):
    client.post("/api/chat/rooms", json={"name": "Room 1"})
    client.post("/api/chat/rooms", json={"name": "Room 2"})
    
    response = client.get("/api/chat/rooms")
    assert response.status_code == 200
    rooms = response.json()
    assert len(rooms) == 2
    assert rooms[0]["name"] in ["Room 1", "Room 2"]
    assert rooms[1]["name"] in ["Room 1", "Room 2"]

def test_get_messages_empty_room(client):
    room_response = client.post("/api/chat/rooms", json={"name": "Empty Room"})
    room_id = room_response.json()["id"]
    
    response = client.get(f"/api/chat/rooms/{room_id}/messages")
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) == 0

def test_get_messages_nonexistent_room(client):
    response = client.get("/api/chat/rooms/nonexistent-id/messages")
    assert response.status_code == 404
    assert response.json()["detail"] == "Room not found"

def test_delete_room(client):
    room_response = client.post("/api/chat/rooms", json={"name": "Room to Delete"})
    room_id = room_response.json()["id"]
    
    delete_response = client.delete(f"/api/chat/rooms/{room_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Room deleted successfully"
    
    get_response = client.get("/api/chat/rooms")
    rooms = get_response.json()
    assert len(rooms) == 0

def test_delete_nonexistent_room(client):
    response = client.delete("/api/chat/rooms/nonexistent-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Room not found"

def test_websocket_connection_and_message(client):
    room_response = client.post("/api/chat/rooms", json={"name": "WebSocket Test Room"})
    room_id = room_response.json()["id"]
    
    with client.websocket_connect(f"/ws/chat/{room_id}?username=TestUser") as websocket:
        join_message = websocket.receive_json()
        assert join_message["type"] == "user_joined"
        assert join_message["username"] == "TestUser"
        assert "TestUser" in join_message["online_users"]
        
        websocket.send_json({
            "type": "message",
            "content": "Hello, World!"
        })
        
        message = websocket.receive_json()
        assert message["type"] == "message"
        assert message["username"] == "TestUser"
        assert message["content"] == "Hello, World!"
        assert message["room_id"] == room_id
        assert "id" in message
        assert "timestamp" in message

def test_websocket_message_persistence(client):
    room_response = client.post("/api/chat/rooms", json={"name": "Persistence Test Room"})
    room_id = room_response.json()["id"]
    
    with client.websocket_connect(f"/ws/chat/{room_id}?username=User1") as websocket:
        websocket.receive_json()
        
        websocket.send_json({
            "type": "message",
            "content": "Persistent message"
        })
        websocket.receive_json()
    
    messages_response = client.get(f"/api/chat/rooms/{room_id}/messages")
    messages = messages_response.json()
    assert len(messages) == 1
    assert messages[0]["content"] == "Persistent message"
    assert messages[0]["username"] == "User1"

def test_websocket_multiple_users(client):
    room_response = client.post("/api/chat/rooms", json={"name": "Multi-User Room"})
    room_id = room_response.json()["id"]
    
    with client.websocket_connect(f"/ws/chat/{room_id}?username=User1") as ws1:
        join1 = ws1.receive_json()
        assert join1["type"] == "user_joined"
        assert join1["username"] == "User1"
        
        with client.websocket_connect(f"/ws/chat/{room_id}?username=User2") as ws2:
            join2_to_user2 = ws2.receive_json()
            assert join2_to_user2["type"] == "user_joined"
            assert join2_to_user2["username"] == "User2"
            
            join2_to_user1 = ws1.receive_json()
            assert join2_to_user1["type"] == "user_joined"
            assert join2_to_user1["username"] == "User2"
            assert "User1" in join2_to_user1["online_users"]
            assert "User2" in join2_to_user1["online_users"]
            
            ws1.send_json({
                "type": "message",
                "content": "Hello from User1"
            })
            
            msg_to_user1 = ws1.receive_json()
            assert msg_to_user1["content"] == "Hello from User1"
            
            msg_to_user2 = ws2.receive_json()
            assert msg_to_user2["content"] == "Hello from User1"
            assert msg_to_user2["username"] == "User1"

def test_websocket_typing_indicator(client):
    room_response = client.post("/api/chat/rooms", json={"name": "Typing Test Room"})
    room_id = room_response.json()["id"]
    
    with client.websocket_connect(f"/ws/chat/{room_id}?username=User1") as ws1:
        ws1.receive_json()
        
        with client.websocket_connect(f"/ws/chat/{room_id}?username=User2") as ws2:
            ws2.receive_json()
            ws1.receive_json()
            
            ws1.send_json({
                "type": "typing",
                "is_typing": True
            })
            
            typing_msg = ws2.receive_json()
            assert typing_msg["type"] == "typing"
            assert typing_msg["username"] == "User1"
            assert typing_msg["is_typing"] == True

def test_websocket_user_disconnect(client):
    room_response = client.post("/api/chat/rooms", json={"name": "Disconnect Test Room"})
    room_id = room_response.json()["id"]
    
    with client.websocket_connect(f"/ws/chat/{room_id}?username=User1") as ws1:
        ws1.receive_json()
        
        ws2 = client.websocket_connect(f"/ws/chat/{room_id}?username=User2")
        with ws2:
            ws2.receive_json()
            ws1.receive_json()
        
        leave_message = ws1.receive_json()
        assert leave_message["type"] == "user_left"
        assert leave_message["username"] == "User2"
        assert "User2" not in leave_message["online_users"]
        assert "User1" in leave_message["online_users"]

def test_websocket_nonexistent_room(client):
    with pytest.raises(Exception):
        with client.websocket_connect("/ws/chat/nonexistent-room?username=TestUser") as websocket:
            pass

def test_delete_room_with_messages(client):
    room_response = client.post("/api/chat/rooms", json={"name": "Room with Messages"})
    room_id = room_response.json()["id"]
    
    with client.websocket_connect(f"/ws/chat/{room_id}?username=TestUser") as websocket:
        websocket.receive_json()
        
        websocket.send_json({
            "type": "message",
            "content": "Test message"
        })
        websocket.receive_json()
    
    messages_before = client.get(f"/api/chat/rooms/{room_id}/messages").json()
    assert len(messages_before) == 1
    
    delete_response = client.delete(f"/api/chat/rooms/{room_id}")
    assert delete_response.status_code == 200
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM messages WHERE room_id = ?", (room_id,))
    count = cursor.fetchone()[0]
    conn.close()
    assert count == 0

def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
