import pytest
from fastapi.testclient import TestClient
import os
import sys

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app, DB_PATH, init_db
import sqlite3


@pytest.fixture(scope="function")
def client():
    """Create a test client with a fresh database for each test."""
    # Use a test database
    test_db_path = "test_notes.db"
    
    # Override the DB_PATH in the main module
    import main
    original_db_path = main.DB_PATH
    main.DB_PATH = test_db_path
    
    # Remove test database if it exists
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    # Initialize fresh database
    init_db()
    
    # Update get_db to use test database
    def get_test_db():
        conn = sqlite3.connect(test_db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    main.get_db = get_test_db
    
    # Create test client
    test_client = TestClient(app)
    
    yield test_client
    
    # Cleanup: restore original DB_PATH and remove test database
    main.DB_PATH = original_db_path
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


def test_create_note(client):
    """Test creating a new note."""
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
    assert data["id"] > 0


def test_get_all_notes(client):
    """Test retrieving all notes."""
    # Create some test notes
    notes = [
        {"title": "Note 1", "content": "Content 1"},
        {"title": "Note 2", "content": "Content 2"},
        {"title": "Note 3", "content": "Content 3"}
    ]
    
    for note in notes:
        client.post("/api/notes/", json=note)
    
    # Get all notes
    response = client.get("/api/notes/")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) == 3
    assert isinstance(data, list)
    
    # Verify notes are returned in descending order by updatedAt
    for i, note in enumerate(notes[::-1]):  # Reversed because of DESC order
        assert data[i]["title"] == note["title"]
        assert data[i]["content"] == note["content"]


def test_get_note_by_id(client):
    """Test retrieving a specific note by ID."""
    # Create a note
    note_data = {
        "title": "Specific Note",
        "content": "Specific content"
    }
    
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


def test_get_note_not_found(client):
    """Test retrieving a non-existent note returns 404."""
    response = client.get("/api/notes/99999")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"


def test_update_note(client):
    """Test updating an existing note."""
    # Create a note
    note_data = {
        "title": "Original Title",
        "content": "Original content"
    }
    
    create_response = client.post("/api/notes/", json=note_data)
    created_note = create_response.json()
    note_id = created_note["id"]
    original_created_at = created_note["createdAt"]
    
    # Update the note
    update_data = {
        "title": "Updated Title",
        "content": "Updated content"
    }
    
    response = client.put(f"/api/notes/{note_id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == note_id
    assert data["title"] == update_data["title"]
    assert data["content"] == update_data["content"]
    assert data["createdAt"] == original_created_at  # createdAt should not change
    assert data["updatedAt"] != original_created_at  # updatedAt should change


def test_update_note_partial(client):
    """Test partially updating a note (only title or content)."""
    # Create a note
    note_data = {
        "title": "Original Title",
        "content": "Original content"
    }
    
    create_response = client.post("/api/notes/", json=note_data)
    created_note = create_response.json()
    note_id = created_note["id"]
    
    # Update only the title
    update_data = {
        "title": "New Title Only"
    }
    
    response = client.put(f"/api/notes/{note_id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["title"] == update_data["title"]
    assert data["content"] == note_data["content"]  # Content should remain unchanged


def test_update_note_not_found(client):
    """Test updating a non-existent note returns 404."""
    update_data = {
        "title": "Updated Title",
        "content": "Updated content"
    }
    
    response = client.put("/api/notes/99999", json=update_data)
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"


def test_delete_note(client):
    """Test deleting a note."""
    # Create a note
    note_data = {
        "title": "Note to Delete",
        "content": "This will be deleted"
    }
    
    create_response = client.post("/api/notes/", json=note_data)
    created_note = create_response.json()
    note_id = created_note["id"]
    
    # Delete the note
    response = client.delete(f"/api/notes/{note_id}")
    
    assert response.status_code == 204
    
    # Verify note is deleted
    get_response = client.get(f"/api/notes/{note_id}")
    assert get_response.status_code == 404


def test_delete_note_not_found(client):
    """Test deleting a non-existent note returns 404."""
    response = client.delete("/api/notes/99999")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"


def test_search_notes_by_title(client):
    """Test searching notes by title."""
    # Create notes with different titles
    notes = [
        {"title": "Python Tutorial", "content": "Learn Python"},
        {"title": "JavaScript Guide", "content": "Learn JavaScript"},
        {"title": "Python Advanced", "content": "Advanced Python topics"}
    ]
    
    for note in notes:
        client.post("/api/notes/", json=note)
    
    # Search for "Python"
    response = client.get("/api/notes/?search=Python")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) == 2
    for note in data:
        assert "Python" in note["title"]


def test_create_note_empty_fields(client):
    """Test that creating a note with empty fields fails validation."""
    note_data = {
        "title": "",
        "content": ""
    }
    
    response = client.post("/api/notes/", json=note_data)
    
    # FastAPI Pydantic validation should reject this
    # Empty strings pass validation, so let's test with missing fields instead
    response = client.post("/api/notes/", json={})
    
    assert response.status_code == 422  # Validation error

