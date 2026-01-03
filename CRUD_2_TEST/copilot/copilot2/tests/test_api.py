import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app, DATA_FILE

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_data_file():
    """Clean up the data file before and after each test"""
    # Before test
    if DATA_FILE.exists():
        DATA_FILE.unlink()
    
    yield
    
    # After test
    if DATA_FILE.exists():
        DATA_FILE.unlink()


def test_create_note():
    """Test creating a new note"""
    note_data = {
        "title": "Test Note",
        "content": "This is a test note content"
    }
    
    response = client.post("/api/notes/", json=note_data)
    
    assert response.status_code == 201
    data = response.json()
    
    assert data["id"] == 1
    assert data["title"] == note_data["title"]
    assert data["content"] == note_data["content"]
    assert "createdAt" in data
    assert "updatedAt" in data
    assert data["createdAt"] == data["updatedAt"]


def test_get_all_notes():
    """Test retrieving all notes"""
    # Create multiple notes
    note1 = {"title": "Note 1", "content": "Content 1"}
    note2 = {"title": "Note 2", "content": "Content 2"}
    
    client.post("/api/notes/", json=note1)
    client.post("/api/notes/", json=note2)
    
    # Get all notes
    response = client.get("/api/notes/")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) == 2
    assert data[0]["title"] == "Note 1"
    assert data[1]["title"] == "Note 2"


def test_get_note_by_id():
    """Test retrieving a specific note by ID"""
    # Create a note
    note_data = {"title": "Specific Note", "content": "Specific Content"}
    create_response = client.post("/api/notes/", json=note_data)
    note_id = create_response.json()["id"]
    
    # Get the note by ID
    response = client.get(f"/api/notes/{note_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == note_id
    assert data["title"] == note_data["title"]
    assert data["content"] == note_data["content"]


def test_get_nonexistent_note():
    """Test retrieving a note that doesn't exist"""
    response = client.get("/api/notes/999")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"


def test_update_note():
    """Test updating an existing note"""
    # Create a note
    note_data = {"title": "Original Title", "content": "Original Content"}
    create_response = client.post("/api/notes/", json=note_data)
    note_id = create_response.json()["id"]
    original_created_at = create_response.json()["createdAt"]
    
    # Update the note
    update_data = {"title": "Updated Title", "content": "Updated Content"}
    response = client.put(f"/api/notes/{note_id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == note_id
    assert data["title"] == "Updated Title"
    assert data["content"] == "Updated Content"
    assert data["createdAt"] == original_created_at
    assert data["updatedAt"] != data["createdAt"]


def test_update_partial_note():
    """Test partially updating a note (only title)"""
    # Create a note
    note_data = {"title": "Original Title", "content": "Original Content"}
    create_response = client.post("/api/notes/", json=note_data)
    note_id = create_response.json()["id"]
    
    # Update only the title
    update_data = {"title": "New Title"}
    response = client.put(f"/api/notes/{note_id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["title"] == "New Title"
    assert data["content"] == "Original Content"  # Content should remain unchanged


def test_update_nonexistent_note():
    """Test updating a note that doesn't exist"""
    update_data = {"title": "New Title"}
    response = client.put("/api/notes/999", json=update_data)
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"


def test_delete_note():
    """Test deleting a note"""
    # Create a note
    note_data = {"title": "Note to Delete", "content": "This will be deleted"}
    create_response = client.post("/api/notes/", json=note_data)
    note_id = create_response.json()["id"]
    
    # Delete the note
    response = client.delete(f"/api/notes/{note_id}")
    
    assert response.status_code == 204
    
    # Verify the note is deleted
    get_response = client.get(f"/api/notes/{note_id}")
    assert get_response.status_code == 404


def test_delete_nonexistent_note():
    """Test deleting a note that doesn't exist"""
    response = client.delete("/api/notes/999")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"


def test_crud_workflow():
    """Test a complete CRUD workflow"""
    # Create
    note_data = {"title": "Workflow Note", "content": "Testing workflow"}
    create_response = client.post("/api/notes/", json=note_data)
    assert create_response.status_code == 201
    note_id = create_response.json()["id"]
    
    # Read
    read_response = client.get(f"/api/notes/{note_id}")
    assert read_response.status_code == 200
    assert read_response.json()["title"] == "Workflow Note"
    
    # Update
    update_data = {"title": "Updated Workflow"}
    update_response = client.put(f"/api/notes/{note_id}", json=update_data)
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated Workflow"
    
    # Delete
    delete_response = client.delete(f"/api/notes/{note_id}")
    assert delete_response.status_code == 204
    
    # Verify deletion
    verify_response = client.get(f"/api/notes/{note_id}")
    assert verify_response.status_code == 404


def test_multiple_notes_sequential_ids():
    """Test that multiple notes get sequential IDs"""
    notes = [
        {"title": f"Note {i}", "content": f"Content {i}"}
        for i in range(1, 4)
    ]
    
    ids = []
    for note in notes:
        response = client.post("/api/notes/", json=note)
        assert response.status_code == 201
        ids.append(response.json()["id"])
    
    # Check that IDs are sequential
    assert ids == [1, 2, 3]
