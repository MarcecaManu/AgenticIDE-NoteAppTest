import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import json
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app, DATA_FILE

client = TestClient(app)

@pytest.fixture(autouse=True)
def cleanup():
    """Clean up test data before and after each test"""
    # Setup: Clear data file before test
    if DATA_FILE.exists():
        DATA_FILE.unlink()
    
    yield
    
    # Teardown: Clear data file after test
    if DATA_FILE.exists():
        DATA_FILE.unlink()


class TestCreateNote:
    """Tests for creating notes"""
    
    def test_create_note_success(self):
        """Test successfully creating a note"""
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
        assert data["id"] == 1
        assert "createdAt" in data
        assert "updatedAt" in data
        assert data["createdAt"] == data["updatedAt"]
    
    def test_create_multiple_notes(self):
        """Test creating multiple notes with incrementing IDs"""
        note1 = {"title": "Note 1", "content": "Content 1"}
        note2 = {"title": "Note 2", "content": "Content 2"}
        
        response1 = client.post("/api/notes/", json=note1)
        response2 = client.post("/api/notes/", json=note2)
        
        assert response1.status_code == 201
        assert response2.status_code == 201
        assert response1.json()["id"] == 1
        assert response2.json()["id"] == 2


class TestReadNotes:
    """Tests for reading notes"""
    
    def test_read_all_notes_empty(self):
        """Test reading all notes when database is empty"""
        response = client.get("/api/notes/")
        
        assert response.status_code == 200
        assert response.json() == []
    
    def test_read_all_notes_with_data(self):
        """Test reading all notes with existing data"""
        # Create test notes
        notes = [
            {"title": "Note 1", "content": "Content 1"},
            {"title": "Note 2", "content": "Content 2"},
            {"title": "Note 3", "content": "Content 3"}
        ]
        
        for note in notes:
            client.post("/api/notes/", json=note)
        
        response = client.get("/api/notes/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all("id" in note for note in data)
        assert all("title" in note for note in data)
        assert all("content" in note for note in data)
    
    def test_read_note_by_id_success(self):
        """Test reading a specific note by ID"""
        # Create a note
        note_data = {"title": "Test Note", "content": "Test Content"}
        create_response = client.post("/api/notes/", json=note_data)
        created_note = create_response.json()
        note_id = created_note["id"]
        
        # Read the note by ID
        response = client.get(f"/api/notes/{note_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == note_id
        assert data["title"] == note_data["title"]
        assert data["content"] == note_data["content"]
    
    def test_read_note_by_id_not_found(self):
        """Test reading a note with non-existent ID"""
        response = client.get("/api/notes/999")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Note not found"


class TestUpdateNote:
    """Tests for updating notes"""
    
    def test_update_note_success(self):
        """Test successfully updating a note"""
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
        assert data["title"] == update_data["title"]
        assert data["content"] == update_data["content"]
        assert data["createdAt"] == original_created_at
        assert data["updatedAt"] != data["createdAt"]
    
    def test_update_note_partial(self):
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
        assert data["content"] == "Original Content"  # Content unchanged
    
    def test_update_note_not_found(self):
        """Test updating a non-existent note"""
        update_data = {"title": "New Title", "content": "New Content"}
        response = client.put("/api/notes/999", json=update_data)
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Note not found"


class TestDeleteNote:
    """Tests for deleting notes"""
    
    def test_delete_note_success(self):
        """Test successfully deleting a note"""
        # Create a note
        note_data = {"title": "To Delete", "content": "This will be deleted"}
        create_response = client.post("/api/notes/", json=note_data)
        note_id = create_response.json()["id"]
        
        # Delete the note
        response = client.delete(f"/api/notes/{note_id}")
        
        assert response.status_code == 204
        
        # Verify note is deleted
        get_response = client.get(f"/api/notes/{note_id}")
        assert get_response.status_code == 404
    
    def test_delete_note_not_found(self):
        """Test deleting a non-existent note"""
        response = client.delete("/api/notes/999")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Note not found"
    
    def test_delete_note_persists(self):
        """Test that deletion persists in storage"""
        # Create two notes
        client.post("/api/notes/", json={"title": "Note 1", "content": "Content 1"})
        create_response = client.post("/api/notes/", json={"title": "Note 2", "content": "Content 2"})
        note_id = create_response.json()["id"]
        
        # Delete one note
        client.delete(f"/api/notes/{note_id}")
        
        # Check all notes
        response = client.get("/api/notes/")
        assert response.status_code == 200
        remaining_notes = response.json()
        assert len(remaining_notes) == 1
        assert remaining_notes[0]["title"] == "Note 1"


class TestPersistence:
    """Tests for data persistence"""
    
    def test_data_persists_to_file(self):
        """Test that data is actually written to the JSON file"""
        note_data = {"title": "Persistent Note", "content": "This should be saved"}
        response = client.post("/api/notes/", json=note_data)
        
        assert response.status_code == 201
        
        # Verify file exists and contains data
        assert DATA_FILE.exists()
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            saved_notes = json.load(f)
        
        assert len(saved_notes) == 1
        assert saved_notes[0]["title"] == note_data["title"]
        assert saved_notes[0]["content"] == note_data["content"]
