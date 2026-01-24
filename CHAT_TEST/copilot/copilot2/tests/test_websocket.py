"""Tests for WebSocket functionality."""
import pytest
import json
from fastapi.testclient import TestClient


class TestWebSocketConnection:
    """Tests for WebSocket connection management."""
    
    def test_websocket_connection_success(self, client, sample_room):
        """Test successful WebSocket connection."""
        room_id = sample_room["id"]
        
        with client.websocket_connect(f"/ws/chat/{room_id}?username=TestUser") as websocket:
            # Should receive join notification
            data = websocket.receive_json()
            assert data["message_type"] == "join"
            assert "TestUser joined" in data["content"]
            
            # Should receive user list
            data = websocket.receive_json()
            assert data["message_type"] == "user_list"
            assert "TestUser" in data["users"]
    
    def test_websocket_connection_nonexistent_room(self, client):
        """Test WebSocket connection to non-existent room."""
        with pytest.raises(Exception):
            with client.websocket_connect("/ws/chat/9999?username=TestUser") as websocket:
                pass
    
    def test_websocket_multiple_users(self, client, sample_room):
        """Test multiple users connecting to same room."""
        room_id = sample_room["id"]
        
        with client.websocket_connect(f"/ws/chat/{room_id}?username=User1") as ws1:
            # Clear initial messages
            ws1.receive_json()  # join notification
            ws1.receive_json()  # user list
            
            with client.websocket_connect(f"/ws/chat/{room_id}?username=User2") as ws2:
                # User1 should receive User2's join notification
                data = ws1.receive_json()
                assert data["message_type"] == "join"
                assert "User2 joined" in data["content"]
                
                # User1 should receive updated user list
                data = ws1.receive_json()
                assert data["message_type"] == "user_list"
                assert "User1" in data["users"]
                assert "User2" in data["users"]


class TestWebSocketMessaging:
    """Tests for WebSocket message broadcasting."""
    
    def test_send_and_receive_message(self, client, sample_room):
        """Test sending and receiving messages."""
        room_id = sample_room["id"]
        
        with client.websocket_connect(f"/ws/chat/{room_id}?username=Sender") as websocket:
            # Clear initial messages
            websocket.receive_json()  # join
            websocket.receive_json()  # user list
            
            # Send a message
            message = {
                "message_type": "message",
                "content": "Hello, World!"
            }
            websocket.send_json(message)
            
            # Receive the broadcast message
            data = websocket.receive_json()
            assert data["message_type"] == "message"
            assert data["username"] == "Sender"
            assert data["content"] == "Hello, World!"
            assert "id" in data
            assert "timestamp" in data
    
    def test_message_broadcasting_to_multiple_users(self, client, sample_room):
        """Test messages are broadcast to all users in room."""
        room_id = sample_room["id"]
        
        with client.websocket_connect(f"/ws/chat/{room_id}?username=User1") as ws1, \
             client.websocket_connect(f"/ws/chat/{room_id}?username=User2") as ws2:
            
            # Clear initial messages
            ws1.receive_json()  # User1 join
            ws1.receive_json()  # User list
            ws1.receive_json()  # User2 join notification
            ws1.receive_json()  # Updated user list
            
            ws2.receive_json()  # User2 join
            ws2.receive_json()  # User list
            
            # User1 sends a message
            message = {
                "message_type": "message",
                "content": "Hello from User1"
            }
            ws1.send_json(message)
            
            # Both users should receive the message
            data1 = ws1.receive_json()
            data2 = ws2.receive_json()
            
            assert data1["content"] == "Hello from User1"
            assert data2["content"] == "Hello from User1"
            assert data1["username"] == "User1"
            assert data2["username"] == "User1"
    
    def test_messages_persist_in_database(self, client, sample_room):
        """Test that messages are saved to database."""
        room_id = sample_room["id"]
        
        # Send messages via WebSocket
        with client.websocket_connect(f"/ws/chat/{room_id}?username=Tester") as websocket:
            websocket.receive_json()  # join
            websocket.receive_json()  # user list
            
            for i in range(3):
                message = {
                    "message_type": "message",
                    "content": f"Test message {i+1}"
                }
                websocket.send_json(message)
                websocket.receive_json()  # receive broadcast
        
        # Retrieve messages via REST API
        response = client.get(f"/api/chat/rooms/{room_id}/messages")
        messages = response.json()
        
        assert len(messages) == 3
        assert messages[0]["content"] == "Test message 1"
        assert messages[1]["content"] == "Test message 2"
        assert messages[2]["content"] == "Test message 3"
        assert all(msg["username"] == "Tester" for msg in messages)


class TestWebSocketTypingIndicator:
    """Tests for typing indicator functionality."""
    
    def test_typing_indicator(self, client, sample_room):
        """Test typing indicator broadcasting."""
        room_id = sample_room["id"]
        
        with client.websocket_connect(f"/ws/chat/{room_id}?username=User1") as ws1, \
             client.websocket_connect(f"/ws/chat/{room_id}?username=User2") as ws2:
            
            # Clear initial messages
            for _ in range(4):
                ws1.receive_json()
            for _ in range(2):
                ws2.receive_json()
            
            # User1 starts typing
            typing_msg = {
                "message_type": "typing",
                "is_typing": True
            }
            ws1.send_json(typing_msg)
            
            # User2 should receive typing indicator
            data = ws2.receive_json()
            assert data["message_type"] == "typing"
            assert data["username"] == "User1"
            assert data["is_typing"] is True
            
            # User1 stops typing
            typing_msg["is_typing"] = False
            ws1.send_json(typing_msg)
            
            # User2 should receive stop typing indicator
            data = ws2.receive_json()
            assert data["message_type"] == "typing"
            assert data["username"] == "User1"
            assert data["is_typing"] is False


class TestWebSocketDisconnection:
    """Tests for connection handling and disconnection."""
    
    def test_user_leave_notification(self, client, sample_room):
        """Test that other users are notified when someone leaves."""
        room_id = sample_room["id"]
        
        with client.websocket_connect(f"/ws/chat/{room_id}?username=User1") as ws1:
            ws1.receive_json()  # join
            ws1.receive_json()  # user list
            
            # User2 connects and disconnects
            with client.websocket_connect(f"/ws/chat/{room_id}?username=User2") as ws2:
                ws1.receive_json()  # User2 join
                ws1.receive_json()  # user list
                ws2.receive_json()  # User2's own join
                ws2.receive_json()  # user list
            
            # User1 should receive leave notification
            data = ws1.receive_json()
            assert data["message_type"] == "leave"
            assert "User2 left" in data["content"]
            
            # User1 should receive updated user list
            data = ws1.receive_json()
            assert data["message_type"] == "user_list"
            assert "User1" in data["users"]
            assert "User2" not in data["users"]
