import pytest
from fastapi.testclient import TestClient
from backend.main import app, STORAGE_FILE
import os
import json

client = TestClient(app)

# Test storage file path
TEST_STORAGE_FILE = "backend/notes_test.json"

@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Setup and teardown for each test"""
    # Backup original storage file if it exists
    original_storage = None
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
            original_storage = f.read()
    
    # Clear storage for testing
    if os.path.exists(STORAGE_FILE):
        os.remove(STORAGE_FILE)
    
    yield
    
    # Restore original storage
    if original_storage:
        with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
            f.write(original_storage)
    elif os.path.exists(STORAGE_FILE):
        os.remove(STORAGE_FILE)


def test_create_note():
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
    created_note = create_response.json()
    note_id = created_note["id"]
    
    # Get the note by ID
    response = client.get(f"/api/notes/{note_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == note_id
    assert data["title"] == note_data["title"]
    assert data["content"] == note_data["content"]


def test_get_note_by_id_not_found():
    """Test retrieving a non-existent note returns 404"""
    response = client.get("/api/notes/non-existent-id")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"


def test_update_note():
    """Test updating an existing note"""
    # Create a note
    note_data = {"title": "Original Title", "content": "Original Content"}
    create_response = client.post("/api/notes/", json=note_data)
    created_note = create_response.json()
    note_id = created_note["id"]
    original_created_at = created_note["createdAt"]
    
    # Update the note
    update_data = {"title": "Updated Title", "content": "Updated Content"}
    response = client.put(f"/api/notes/{note_id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == note_id
    assert data["title"] == update_data["title"]
    assert data["content"] == update_data["content"]
    assert data["createdAt"] == original_created_at
    assert data["updatedAt"] != original_created_at


def test_update_note_partial():
    """Test partially updating a note (only title)"""
    # Create a note
    note_data = {"title": "Original Title", "content": "Original Content"}
    create_response = client.post("/api/notes/", json=note_data)
    created_note = create_response.json()
    note_id = created_note["id"]
    
    # Update only the title
    update_data = {"title": "Updated Title Only"}
    response = client.put(f"/api/notes/{note_id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["title"] == "Updated Title Only"
    assert data["content"] == "Original Content"  # Content should remain unchanged


def test_update_note_not_found():
    """Test updating a non-existent note returns 404"""
    update_data = {"title": "Updated", "content": "Updated"}
    response = client.put("/api/notes/non-existent-id", json=update_data)
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"


def test_delete_note():
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


def test_delete_note_not_found():
    """Test deleting a non-existent note returns 404"""
    response = client.delete("/api/notes/non-existent-id")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"


def test_persistence():
    """Test that notes persist across requests"""
    # Create a note
    note_data = {"title": "Persistent Note", "content": "Should persist"}
    create_response = client.post("/api/notes/", json=note_data)
    note_id = create_response.json()["id"]
    
    # Verify storage file exists and contains the note
    assert os.path.exists(STORAGE_FILE)
    
    with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
        stored_notes = json.load(f)
    
    assert len(stored_notes) == 1
    assert stored_notes[0]["id"] == note_id
    assert stored_notes[0]["title"] == note_data["title"]

