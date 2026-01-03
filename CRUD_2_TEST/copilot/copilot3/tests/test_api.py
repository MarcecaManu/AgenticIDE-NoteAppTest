import pytest
import sys
import os
from fastapi.testclient import TestClient

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app
from database import Database


@pytest.fixture
def client():
    """Create a test client with a fresh database"""
    # Use a test database
    test_db_path = "test_notes.db"
    
    # Remove test database if it exists
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    # Override the database in the app
    from main import db as main_db
    test_db = Database(test_db_path)
    app.dependency_overrides = {}
    
    # Replace the database instance in main module
    import main
    original_db = main.db
    main.db = test_db
    
    client = TestClient(app)
    
    yield client
    
    # Cleanup: restore original db and remove test database
    main.db = original_db
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


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


def test_read_all_notes(client):
    """Test reading all notes"""
    # Create some test notes
    note1 = {"title": "Note 1", "content": "Content 1"}
    note2 = {"title": "Note 2", "content": "Content 2"}
    
    client.post("/api/notes/", json=note1)
    client.post("/api/notes/", json=note2)
    
    # Get all notes
    response = client.get("/api/notes/")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert any(note["title"] == "Note 1" for note in data)
    assert any(note["title"] == "Note 2" for note in data)


def test_read_note_by_id(client):
    """Test reading a specific note by ID"""
    # Create a note
    note_data = {"title": "Specific Note", "content": "Specific Content"}
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


def test_read_note_not_found(client):
    """Test reading a non-existent note returns 404"""
    response = client.get("/api/notes/99999")
    
    assert response.status_code == 404
    assert "detail" in response.json()


def test_update_note(client):
    """Test updating an existing note"""
    # Create a note
    note_data = {"title": "Original Title", "content": "Original Content"}
    create_response = client.post("/api/notes/", json=note_data)
    created_note = create_response.json()
    note_id = created_note["id"]
    original_created_at = created_note["createdAt"]
    
    # Update the note
    updated_data = {"title": "Updated Title", "content": "Updated Content"}
    response = client.put(f"/api/notes/{note_id}", json=updated_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == note_id
    assert data["title"] == updated_data["title"]
    assert data["content"] == updated_data["content"]
    assert data["createdAt"] == original_created_at  # createdAt should not change
    assert data["updatedAt"] != original_created_at  # updatedAt should change


def test_update_note_not_found(client):
    """Test updating a non-existent note returns 404"""
    updated_data = {"title": "Updated Title", "content": "Updated Content"}
    response = client.put("/api/notes/99999", json=updated_data)
    
    assert response.status_code == 404
    assert "detail" in response.json()


def test_delete_note(client):
    """Test deleting a note"""
    # Create a note
    note_data = {"title": "To Be Deleted", "content": "Delete me"}
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
    assert "detail" in response.json()


def test_create_note_with_empty_title(client):
    """Test creating a note with empty title fails validation"""
    note_data = {"title": "", "content": "Content"}
    response = client.post("/api/notes/", json=note_data)
    
    # FastAPI validation should catch this
    assert response.status_code == 422


def test_full_crud_workflow(client):
    """Test a complete CRUD workflow"""
    # 1. Create a note
    create_data = {"title": "Workflow Note", "content": "Initial content"}
    create_response = client.post("/api/notes/", json=create_data)
    assert create_response.status_code == 201
    note = create_response.json()
    note_id = note["id"]
    
    # 2. Read the note
    read_response = client.get(f"/api/notes/{note_id}")
    assert read_response.status_code == 200
    assert read_response.json()["title"] == "Workflow Note"
    
    # 3. Update the note
    update_data = {"title": "Updated Workflow", "content": "Updated content"}
    update_response = client.put(f"/api/notes/{note_id}", json=update_data)
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated Workflow"
    
    # 4. Delete the note
    delete_response = client.delete(f"/api/notes/{note_id}")
    assert delete_response.status_code == 204
    
    # 5. Verify deletion
    final_read = client.get(f"/api/notes/{note_id}")
    assert final_read.status_code == 404
