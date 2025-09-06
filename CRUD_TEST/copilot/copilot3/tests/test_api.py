import sys
import os
import pytest
from fastapi.testclient import TestClient

# Add the parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.main import app
from backend.app.database.database import Base, engine

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_create_note():
    note_data = {"title": "Test Note", "content": "Test Content"}
    response = client.post("/api/notes/", json=note_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == note_data["title"]
    assert data["content"] == note_data["content"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

def test_get_notes():
    # First create a note
    note_data = {"title": "Test Note", "content": "Test Content"}
    client.post("/api/notes/", json=note_data)
    
    # Get all notes
    response = client.get("/api/notes/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert isinstance(data, list)
    assert all(isinstance(note, dict) for note in data)

def test_update_note():
    # First create a note
    note_data = {"title": "Original Title", "content": "Original Content"}
    response = client.post("/api/notes/", json=note_data)
    note_id = response.json()["id"]
    
    # Update the note
    updated_data = {"title": "Updated Title", "content": "Updated Content"}
    response = client.put(f"/api/notes/{note_id}", json=updated_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == updated_data["title"]
    assert data["content"] == updated_data["content"]

def test_delete_note():
    # First create a note
    note_data = {"title": "Test Note", "content": "Test Content"}
    response = client.post("/api/notes/", json=note_data)
    note_id = response.json()["id"]
    
    # Delete the note
    response = client.delete(f"/api/notes/{note_id}")
    assert response.status_code == 200
    
    # Verify the note is deleted
    response = client.get(f"/api/notes/{note_id}")
    assert response.status_code == 404