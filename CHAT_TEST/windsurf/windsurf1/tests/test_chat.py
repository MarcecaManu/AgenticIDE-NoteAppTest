import pytest
import asyncio
import json
import os
import shutil
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app, DATA_DIR, ROOMS_FILE, MESSAGES_FILE, manager

@pytest.fixture(autouse=True)
def cleanup_data():
    if os.path.exists(DATA_DIR):
        shutil.rmtree(DATA_DIR)
    os.makedirs(DATA_DIR, exist_ok=True)
    
    manager.active_connections.clear()
    manager.typing_users.clear()
    
    yield
    
    if os.path.exists(DATA_DIR):
        shutil.rmtree(DATA_DIR)

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
    assert rooms[0]["name"] == "Room 1"
    assert rooms[1]["name"] == "Room 2"

def test_get_room_messages(client):
    create_response = client.post("/api/chat/rooms", json={"name": "Test Room"})
    room_id = create_response.json()["id"]
    
    response = client.get(f"/api/chat/rooms/{room_id}/messages")
    
    assert response.status_code == 200
    messages = response.json()
    assert isinstance(messages, list)
    assert len(messages) == 0

def test_get_room_messages_not_found(client):
    response = client.get("/api/chat/rooms/nonexistent-room-id/messages")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Room not found"

def test_delete_room(client):
    create_response = client.post("/api/chat/rooms", json={"name": "Test Room"})
    room_id = create_response.json()["id"]
    
    delete_response = client.delete(f"/api/chat/rooms/{room_id}")
    
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Room deleted successfully"
    
    get_response = client.get("/api/chat/rooms")
    rooms = get_response.json()
    assert len(rooms) == 0

def test_delete_room_not_found(client):
    response = client.delete("/api/chat/rooms/nonexistent-room-id")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Room not found"

def test_websocket_connection_and_messaging(client):
    create_response = client.post("/api/chat/rooms", json={"name": "Test Room"})
    room_id = create_response.json()["id"]
    
    with client.websocket_connect(f"/ws/chat/{room_id}?username=TestUser") as websocket:
        join_message = websocket.receive_json()
        assert join_message["type"] == "system"
        assert "TestUser joined the room" in join_message["content"]
        
        user_list_message = websocket.receive_json()
        assert user_list_message["type"] == "user_list"
        assert "TestUser" in user_list_message["users"]
        
        websocket.send_json({
            "type": "message",
            "content": "Hello, World!"
        })
        
        message_response = websocket.receive_json()
        assert message_response["type"] == "message"
        assert message_response["message"]["username"] == "TestUser"
        assert message_response["message"]["content"] == "Hello, World!"
        assert message_response["message"]["room_id"] == room_id

def test_websocket_multiple_users(client):
    create_response = client.post("/api/chat/rooms", json={"name": "Test Room"})
    room_id = create_response.json()["id"]
    
    with client.websocket_connect(f"/ws/chat/{room_id}?username=User1") as ws1:
        ws1.receive_json()
        ws1.receive_json()
        
        with client.websocket_connect(f"/ws/chat/{room_id}?username=User2") as ws2:
            user1_sees_join = ws1.receive_json()
            assert user1_sees_join["type"] == "system"
            assert "User2 joined the room" in user1_sees_join["content"]
            
            user1_sees_list = ws1.receive_json()
            assert user1_sees_list["type"] == "user_list"
            assert len(user1_sees_list["users"]) == 2
            
            user2_sees_join = ws2.receive_json()
            assert user2_sees_join["type"] == "system"
            
            user2_sees_list = ws2.receive_json()
            assert user2_sees_list["type"] == "user_list"
            assert len(user2_sees_list["users"]) == 2
            
            ws2.send_json({
                "type": "message",
                "content": "Message from User2"
            })
            
            user1_receives = ws1.receive_json()
            assert user1_receives["type"] == "message"
            assert user1_receives["message"]["username"] == "User2"
            assert user1_receives["message"]["content"] == "Message from User2"
            
            user2_receives = ws2.receive_json()
            assert user2_receives["type"] == "message"
            assert user2_receives["message"]["username"] == "User2"

def test_websocket_typing_indicator(client):
    create_response = client.post("/api/chat/rooms", json={"name": "Test Room"})
    room_id = create_response.json()["id"]
    
    with client.websocket_connect(f"/ws/chat/{room_id}?username=User1") as ws1:
        ws1.receive_json()
        ws1.receive_json()
        
        with client.websocket_connect(f"/ws/chat/{room_id}?username=User2") as ws2:
            ws1.receive_json()
            ws1.receive_json()
            ws2.receive_json()
            ws2.receive_json()
            
            ws2.send_json({
                "type": "typing",
                "is_typing": True
            })
            
            typing_message = ws1.receive_json()
            assert typing_message["type"] == "typing"
            assert "User2" in typing_message["users"]
            
            ws2.send_json({
                "type": "typing",
                "is_typing": False
            })
            
            stop_typing_message = ws1.receive_json()
            assert stop_typing_message["type"] == "typing"
            assert "User2" not in stop_typing_message["users"]

def test_websocket_room_not_found(client):
    with pytest.raises(Exception):
        with client.websocket_connect("/ws/chat/nonexistent-room?username=TestUser") as websocket:
            pass

def test_message_persistence(client):
    create_response = client.post("/api/chat/rooms", json={"name": "Test Room"})
    room_id = create_response.json()["id"]
    
    with client.websocket_connect(f"/ws/chat/{room_id}?username=TestUser") as websocket:
        websocket.receive_json()
        websocket.receive_json()
        
        websocket.send_json({
            "type": "message",
            "content": "Persistent message"
        })
        
        websocket.receive_json()
    
    response = client.get(f"/api/chat/rooms/{room_id}/messages")
    messages = response.json()
    
    assert len(messages) == 1
    assert messages[0]["username"] == "TestUser"
    assert messages[0]["content"] == "Persistent message"
    assert messages[0]["room_id"] == room_id

def test_delete_room_removes_messages(client):
    create_response = client.post("/api/chat/rooms", json={"name": "Test Room"})
    room_id = create_response.json()["id"]
    
    with client.websocket_connect(f"/ws/chat/{room_id}?username=TestUser") as websocket:
        websocket.receive_json()
        websocket.receive_json()
        
        websocket.send_json({
            "type": "message",
            "content": "Test message"
        })
        
        websocket.receive_json()
    
    messages_before = client.get(f"/api/chat/rooms/{room_id}/messages").json()
    assert len(messages_before) == 1
    
    client.delete(f"/api/chat/rooms/{room_id}")
    
    assert os.path.exists(MESSAGES_FILE)
    with open(MESSAGES_FILE, 'r') as f:
        all_messages = json.load(f)
    
    room_messages = [msg for msg in all_messages if msg["room_id"] == room_id]
    assert len(room_messages) == 0
