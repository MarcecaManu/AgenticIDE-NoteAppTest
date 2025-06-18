import pytest
from datetime import datetime

def test_create_note(test_client):
    response = test_client.post(
        "/api/notes/",
        json={"title": "Test Note", "content": "Test Content"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Note"
    assert data["content"] == "Test Content"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

def test_get_notes(test_client):
    # Create a test note first
    test_client.post(
        "/api/notes/",
        json={"title": "Test Note", "content": "Test Content"}
    )
    
    response = test_client.get("/api/notes/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["title"] == "Test Note"
    assert data[0]["content"] == "Test Content"

def test_update_note(test_client):
    # Create a test note first
    create_response = test_client.post(
        "/api/notes/",
        json={"title": "Original Title", "content": "Original Content"}
    )
    note_id = create_response.json()["id"]
    
    # Update the note
    update_response = test_client.put(
        f"/api/notes/{note_id}",
        json={"title": "Updated Title", "content": "Updated Content"}
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["title"] == "Updated Title"
    assert data["content"] == "Updated Content"

def test_delete_note(test_client):
    # Create a test note first
    create_response = test_client.post(
        "/api/notes/",
        json={"title": "Test Note", "content": "Test Content"}
    )
    note_id = create_response.json()["id"]
    
    # Delete the note
    delete_response = test_client.delete(f"/api/notes/{note_id}")
    assert delete_response.status_code == 200
    
    # Verify the note is deleted
    get_response = test_client.get(f"/api/notes/{note_id}")
    assert get_response.status_code == 404
