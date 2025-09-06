import pytest
from fastapi.testclient import TestClient
import os
import sys

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from backend.main import app

client = TestClient(app)

def test_create_note():
    response = client.post(
        "/api/notes/",
        json={"title": "Test Note", "content": "Test Content"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Note"
    assert data["content"] == "Test Content"
    assert "id" in data
    return data["id"]

def test_read_notes():
    response = client.get("/api/notes/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_update_note():
    # First create a note
    note_id = test_create_note()
    
    # Then update it
    response = client.put(
        f"/api/notes/{note_id}",
        json={"title": "Updated Note", "content": "Updated Content"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Note"
    assert data["content"] == "Updated Content"

def test_delete_note():
    # First create a note
    note_id = test_create_note()
    
    # Then delete it
    response = client.delete(f"/api/notes/{note_id}")
    assert response.status_code == 200
    
    # Verify it's deleted
    response = client.get(f"/api/notes/{note_id}")
    assert response.status_code == 404
