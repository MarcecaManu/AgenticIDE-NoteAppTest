"""Tests for REST API endpoints."""
import pytest
from fastapi import status


class TestRoomEndpoints:
    """Tests for room management endpoints."""
    
    def test_create_room_success(self, client):
        """Test successful room creation."""
        response = client.post(
            "/api/chat/rooms",
            json={"name": "General Chat"}
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "General Chat"
        assert "id" in data
        assert "created_at" in data
    
    def test_create_room_duplicate_name(self, client):
        """Test creating room with duplicate name fails."""
        # Create first room
        client.post("/api/chat/rooms", json={"name": "Duplicate Room"})
        
        # Try to create duplicate
        response = client.post(
            "/api/chat/rooms",
            json={"name": "Duplicate Room"}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"]
    
    def test_list_rooms_empty(self, client):
        """Test listing rooms when none exist."""
        response = client.get("/api/chat/rooms")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
    
    def test_list_rooms_with_data(self, client):
        """Test listing rooms with existing data."""
        # Create multiple rooms
        client.post("/api/chat/rooms", json={"name": "Room 1"})
        client.post("/api/chat/rooms", json={"name": "Room 2"})
        client.post("/api/chat/rooms", json={"name": "Room 3"})
        
        response = client.get("/api/chat/rooms")
        
        assert response.status_code == status.HTTP_200_OK
        rooms = response.json()
        assert len(rooms) == 3
        assert all("id" in room and "name" in room for room in rooms)
    
    def test_delete_room_success(self, client, sample_room):
        """Test successful room deletion."""
        room_id = sample_room["id"]
        
        response = client.delete(f"/api/chat/rooms/{room_id}")
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify room is deleted
        response = client.get("/api/chat/rooms")
        rooms = response.json()
        assert not any(room["id"] == room_id for room in rooms)
    
    def test_delete_room_not_found(self, client):
        """Test deleting non-existent room."""
        response = client.delete("/api/chat/rooms/9999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestMessageEndpoints:
    """Tests for message endpoints."""
    
    def test_get_messages_empty_room(self, client, sample_room):
        """Test getting messages from empty room."""
        room_id = sample_room["id"]
        
        response = client.get(f"/api/chat/rooms/{room_id}/messages")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
    
    def test_get_messages_nonexistent_room(self, client):
        """Test getting messages from non-existent room."""
        response = client.get("/api/chat/rooms/9999/messages")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestHealthEndpoints:
    """Tests for health and root endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns frontend HTML."""
        response = client.get("/")
        
        assert response.status_code == status.HTTP_200_OK
        # Root now serves HTML frontend
        assert response.headers["content-type"].startswith("text/html")
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "healthy"
