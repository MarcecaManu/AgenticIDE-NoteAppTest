import pytest
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket
import sys
import os
import sqlite3
import json
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app, init_db, DB_PATH

@pytest.fixture(autouse=True)
def setup_and_teardown():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()
    yield
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

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

def test_get_messages_for_room(client):
    create_response = client.post("/api/chat/rooms", json={"name": "Test Room"})
    room_id = create_response.json()["id"]
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (room_id, username, content, timestamp) VALUES (?, ?, ?, ?)",
        (room_id, "Alice", "Hello!", datetime.utcnow().isoformat())
    )
    cursor.execute(
        "INSERT INTO messages (room_id, username, content, timestamp) VALUES (?, ?, ?, ?)",
        (room_id, "Bob", "Hi there!", datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()
    
    response = client.get(f"/api/chat/rooms/{room_id}/messages")
    
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) == 2
    assert messages[0]["username"] == "Alice"
    assert messages[0]["content"] == "Hello!"
    assert messages[1]["username"] == "Bob"
    assert messages[1]["content"] == "Hi there!"

def test_get_messages_room_not_found(client):
    response = client.get("/api/chat/rooms/nonexistent-room-id/messages")
    assert response.status_code == 404

def test_delete_room(client):
    create_response = client.post("/api/chat/rooms", json={"name": "Test Room"})
    room_id = create_response.json()["id"]
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (room_id, username, content, timestamp) VALUES (?, ?, ?, ?)",
        (room_id, "Alice", "Test message", datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()
    
    delete_response = client.delete(f"/api/chat/rooms/{room_id}")
    assert delete_response.status_code == 200
    
    get_response = client.get(f"/api/chat/rooms/{room_id}/messages")
    assert get_response.status_code == 404
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM messages WHERE room_id = ?", (room_id,))
    count = cursor.fetchone()[0]
    conn.close()
    assert count == 0

def test_delete_room_not_found(client):
    response = client.delete("/api/chat/rooms/nonexistent-room-id")
    assert response.status_code == 404

def test_websocket_connection_and_messaging(client):
    create_response = client.post("/api/chat/rooms", json={"name": "WebSocket Test Room"})
    room_id = create_response.json()["id"]
    
    with client.websocket_connect(f"/ws/chat/{room_id}?username=Alice") as websocket:
        join_message = websocket.receive_json()
        assert join_message["type"] == "user_joined"
        assert join_message["username"] == "Alice"
        assert "Alice" in join_message["online_users"]
        
        websocket.send_json({
            "type": "message",
            "content": "Hello from Alice!"
        })
        
        message_broadcast = websocket.receive_json()
        assert message_broadcast["type"] == "message"
        assert message_broadcast["username"] == "Alice"
        assert message_broadcast["content"] == "Hello from Alice!"
        assert "id" in message_broadcast
        assert "timestamp" in message_broadcast

def test_websocket_multiple_users(client):
    create_response = client.post("/api/chat/rooms", json={"name": "Multi-User Room"})
    room_id = create_response.json()["id"]
    
    with client.websocket_connect(f"/ws/chat/{room_id}?username=Alice") as ws1:
        join_msg1 = ws1.receive_json()
        assert join_msg1["type"] == "user_joined"
        assert join_msg1["username"] == "Alice"
        
        with client.websocket_connect(f"/ws/chat/{room_id}?username=Bob") as ws2:
            join_msg2_ws1 = ws1.receive_json()
            assert join_msg2_ws1["type"] == "user_joined"
            assert join_msg2_ws1["username"] == "Bob"
            assert set(join_msg2_ws1["online_users"]) == {"Alice", "Bob"}
            
            join_msg2_ws2 = ws2.receive_json()
            assert join_msg2_ws2["type"] == "user_joined"
            assert join_msg2_ws2["username"] == "Bob"
            
            ws1.send_json({
                "type": "message",
                "content": "Hello from Alice!"
            })
            
            msg_ws1 = ws1.receive_json()
            assert msg_ws1["type"] == "message"
            assert msg_ws1["content"] == "Hello from Alice!"
            
            msg_ws2 = ws2.receive_json()
            assert msg_ws2["type"] == "message"
            assert msg_ws2["content"] == "Hello from Alice!"

def test_websocket_typing_indicator(client):
    create_response = client.post("/api/chat/rooms", json={"name": "Typing Test Room"})
    room_id = create_response.json()["id"]
    
    with client.websocket_connect(f"/ws/chat/{room_id}?username=Alice") as ws1:
        ws1.receive_json()
        
        with client.websocket_connect(f"/ws/chat/{room_id}?username=Bob") as ws2:
            ws1.receive_json()
            ws2.receive_json()
            
            ws1.send_json({
                "type": "typing",
                "is_typing": True
            })
            
            typing_msg = ws2.receive_json()
            assert typing_msg["type"] == "typing"
            assert typing_msg["username"] == "Alice"
            assert typing_msg["is_typing"] == True

def test_websocket_user_disconnect(client):
    create_response = client.post("/api/chat/rooms", json={"name": "Disconnect Test Room"})
    room_id = create_response.json()["id"]
    
    with client.websocket_connect(f"/ws/chat/{room_id}?username=Alice") as ws1:
        ws1.receive_json()
        
        with client.websocket_connect(f"/ws/chat/{room_id}?username=Bob") as ws2:
            ws1.receive_json()
            ws2.receive_json()
        
        leave_msg = ws1.receive_json()
        assert leave_msg["type"] == "user_left"
        assert leave_msg["username"] == "Bob"
        assert "Alice" in leave_msg["online_users"]
        assert "Bob" not in leave_msg["online_users"]

def test_websocket_room_not_found(client):
    with pytest.raises(Exception):
        with client.websocket_connect("/ws/chat/nonexistent-room?username=Alice") as websocket:
            pass

def test_message_persistence(client):
    create_response = client.post("/api/chat/rooms", json={"name": "Persistence Test Room"})
    room_id = create_response.json()["id"]
    
    with client.websocket_connect(f"/ws/chat/{room_id}?username=Alice") as websocket:
        websocket.receive_json()
        
        websocket.send_json({
            "type": "message",
            "content": "Persistent message"
        })
        
        websocket.receive_json()
    
    response = client.get(f"/api/chat/rooms/{room_id}/messages")
    messages = response.json()
    
    assert len(messages) == 1
    assert messages[0]["username"] == "Alice"
    assert messages[0]["content"] == "Persistent message"

def test_no_duplicate_connections_same_user(client):
    create_response = client.post("/api/chat/rooms", json={"name": "Duplicate Prevention Room"})
    room_id = create_response.json()["id"]
    
    with client.websocket_connect(f"/ws/chat/{room_id}?username=Alice") as ws1:
        join_msg1 = ws1.receive_json()
        assert join_msg1["type"] == "user_joined"
        assert join_msg1["username"] == "Alice"
        assert join_msg1["online_users"] == ["Alice"]
        
        with client.websocket_connect(f"/ws/chat/{room_id}?username=Alice") as ws2:
            join_msg2 = ws2.receive_json()
            assert join_msg2["type"] == "user_joined"
            assert join_msg2["username"] == "Alice"
            assert join_msg2["online_users"] == ["Alice"]
            
            ws2.send_json({
                "type": "message",
                "content": "Test message from second connection"
            })
            
            msg = ws2.receive_json()
            assert msg["type"] == "message"
            assert msg["content"] == "Test message from second connection"
            
            try:
                ws1.receive_json(timeout=1)
                assert False, "First connection should be closed"
            except:
                pass
