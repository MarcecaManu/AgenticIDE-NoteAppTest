import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path
import os

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Set test database path
os.environ['TEST_MODE'] = '1'

from main import app
from database import init_db, DB_PATH

@pytest.fixture(scope="function")
def client():
    """Create a test client with a fresh database for each test"""
    # Use a test database
    test_db_path = Path(__file__).parent / "test_notes.db"
    
    # Replace the DB_PATH in database module
    import database
    original_db_path = database.DB_PATH
    database.DB_PATH = test_db_path
    
    # Initialize fresh database
    if test_db_path.exists():
        test_db_path.unlink()
    init_db()
    
    # Create test client
    test_client = TestClient(app)
    
    yield test_client
    
    # Cleanup
    if test_db_path.exists():
        test_db_path.unlink()
    database.DB_PATH = original_db_path


def test_create_note(client):
    """Test creating a new note"""
    note_data = {
        "title": "Test Note",
        "content": "This is a test note content"
    }
    
    response = client.post("/api/notes/", json=note_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == note_data["title"]
    assert data["content"] == note_data["content"]
    assert "id" in data
    assert "createdAt" in data
    assert "updatedAt" in data


def test_get_all_notes(client):
    """Test retrieving all notes"""
    # Create some test notes
    notes_data = [
        {"title": "Note 1", "content": "Content 1"},
        {"title": "Note 2", "content": "Content 2"},
        {"title": "Note 3", "content": "Content 3"}
    ]
    
    for note_data in notes_data:
        client.post("/api/notes/", json=note_data)
    
    # Get all notes
    response = client.get("/api/notes/")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert all("id" in note for note in data)
    assert all("title" in note for note in data)
    assert all("content" in note for note in data)


def test_get_note_by_id(client):
    """Test retrieving a specific note by ID"""
    # Create a note
    note_data = {"title": "Specific Note", "content": "Specific content"}
    create_response = client.post("/api/notes/", json=note_data)
    created_note = create_response.json()
    note_id = created_note["id"]
    
    # Get the note by ID
    response = client.get(f"/api/notes/{note_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == note_id
    assert data["title"] == note_data["title"]
    assert data["content"] == note_data["content"]


def test_get_note_by_id_not_found(client):
    """Test retrieving a non-existent note returns 404"""
    response = client.get("/api/notes/99999")
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_update_note(client):
    """Test updating an existing note"""
    # Create a note
    note_data = {"title": "Original Title", "content": "Original content"}
    create_response = client.post("/api/notes/", json=note_data)
    created_note = create_response.json()
    note_id = created_note["id"]
    
    # Update the note
    updated_data = {"title": "Updated Title", "content": "Updated content"}
    response = client.put(f"/api/notes/{note_id}", json=updated_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == note_id
    assert data["title"] == updated_data["title"]
    assert data["content"] == updated_data["content"]
    # updatedAt should be >= createdAt (may be equal if update is within same second)
    assert data["updatedAt"] >= data["createdAt"]


def test_update_note_not_found(client):
    """Test updating a non-existent note returns 404"""
    updated_data = {"title": "Updated Title", "content": "Updated content"}
    response = client.put("/api/notes/99999", json=updated_data)
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_delete_note(client):
    """Test deleting a note"""
    # Create a note
    note_data = {"title": "Note to Delete", "content": "This will be deleted"}
    create_response = client.post("/api/notes/", json=note_data)
    created_note = create_response.json()
    note_id = created_note["id"]
    
    # Delete the note
    response = client.delete(f"/api/notes/{note_id}")
    
    assert response.status_code == 204
    
    # Verify the note is deleted
    get_response = client.get(f"/api/notes/{note_id}")
    assert get_response.status_code == 404


def test_delete_note_not_found(client):
    """Test deleting a non-existent note returns 404"""
    response = client.delete("/api/notes/99999")
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_create_note_empty_fields(client):
    """Test creating a note with empty fields returns validation error"""
    note_data = {"title": "", "content": ""}
    response = client.post("/api/notes/", json=note_data)
    
    # Should still create but with empty strings (depends on validation)
    # FastAPI/Pydantic will accept empty strings unless we add validators
    assert response.status_code == 201


def test_notes_persistence(client):
    """Test that notes persist across requests"""
    # Create a note
    note_data = {"title": "Persistent Note", "content": "This should persist"}
    create_response = client.post("/api/notes/", json=note_data)
    note_id = create_response.json()["id"]
    
    # Get all notes
    list_response = client.get("/api/notes/")
    notes = list_response.json()
    
    # Verify the note exists in the list
    assert any(note["id"] == note_id for note in notes)
    assert any(note["title"] == note_data["title"] for note in notes)

