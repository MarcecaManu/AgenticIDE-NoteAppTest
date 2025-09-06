import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app
from database import notes_table

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_database():
    """Clear the database before each test"""
    notes_table.truncate()
    yield

def test_create_note():
    note_data = {
        "title": "Test Note",
        "content": "This is a test note"
    }
    response = client.post("/api/notes/", json=note_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["title"] == note_data["title"]
    assert data["content"] == note_data["content"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

def test_get_all_notes():
    # Create two test notes
    notes = [
        {"title": "Note 1", "content": "Content 1"},
        {"title": "Note 2", "content": "Content 2"}
    ]
    
    for note in notes:
        client.post("/api/notes/", json=note)
    
    response = client.get("/api/notes/")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    assert all(isinstance(note["id"], int) for note in data)
    assert all(note["title"] in ["Note 1", "Note 2"] for note in data)

def test_update_note():
    # Create a test note
    create_response = client.post("/api/notes/", json={
        "title": "Original Title",
        "content": "Original Content"
    })
    note_id = create_response.json()["id"]
    
    # Update the note
    update_data = {
        "title": "Updated Title",
        "content": "Updated Content"
    }
    response = client.put(f"/api/notes/{note_id}", json=update_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["content"] == update_data["content"]
    assert data["id"] == note_id

def test_delete_note():
    # Create a test note
    create_response = client.post("/api/notes/", json={
        "title": "Note to Delete",
        "content": "This note will be deleted"
    })
    note_id = create_response.json()["id"]
    
    # Delete the note
    response = client.delete(f"/api/notes/{note_id}")
    assert response.status_code == 200
    
    # Verify the note is deleted
    get_response = client.get(f"/api/notes/{note_id}")
    assert get_response.status_code == 404 