"""
Tests for REST API endpoints.
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.asyncio
async def test_create_room(client):
    """Test creating a new chat room."""
    response = client.post(
        "/api/chat/rooms",
        json={"name": "Test Room"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["name"] == "Test Room"
    assert "created_at" in data


@pytest.mark.asyncio
async def test_get_all_rooms(client):
    """Test retrieving all chat rooms."""
    # Create two rooms
    client.post("/api/chat/rooms", json={"name": "Room 1"})
    client.post("/api/chat/rooms", json={"name": "Room 2"})
    
    # Get all rooms
    response = client.get("/api/chat/rooms")
    
    assert response.status_code == 200
    rooms = response.json()
    assert len(rooms) == 2
    assert rooms[0]["name"] in ["Room 1", "Room 2"]
    assert rooms[1]["name"] in ["Room 1", "Room 2"]


@pytest.mark.asyncio
async def test_get_room_messages_empty(client):
    """Test retrieving messages from an empty room."""
    # Create a room
    create_response = client.post(
        "/api/chat/rooms",
        json={"name": "Empty Room"}
    )
    room_id = create_response.json()["id"]
    
    # Get messages
    response = client.get(f"/api/chat/rooms/{room_id}/messages")
    
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) == 0


@pytest.mark.asyncio
async def test_get_messages_nonexistent_room(client):
    """Test retrieving messages from a non-existent room."""
    response = client.get("/api/chat/rooms/nonexistent-id/messages")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Room not found"


@pytest.mark.asyncio
async def test_delete_room(client):
    """Test deleting a chat room."""
    # Create a room
    create_response = client.post(
        "/api/chat/rooms",
        json={"name": "Room to Delete"}
    )
    room_id = create_response.json()["id"]
    
    # Delete the room
    response = client.delete(f"/api/chat/rooms/{room_id}")
    
    assert response.status_code == 204
    
    # Verify room is deleted
    get_response = client.get(f"/api/chat/rooms/{room_id}/messages")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_nonexistent_room(client):
    """Test deleting a non-existent room."""
    response = client.delete("/api/chat/rooms/nonexistent-id")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Room not found"


@pytest.mark.asyncio
async def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

