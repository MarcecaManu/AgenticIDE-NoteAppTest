import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys
import os
import time

# Import the app using the correct path
sys.path.insert(0, str(Path(__file__).parent.parent))
from main import app
from database import Database

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_test_db():
    # Setup: ensure we have a clean database for each test
    db_path = Path(__file__).parent.parent / "notes.json"
    
    def remove_db_file():
        retries = 3
        while retries > 0:
            try:
                if db_path.exists():
                    os.remove(db_path)
                break
            except PermissionError:
                retries -= 1
                time.sleep(0.1)
    
    # Clean up before test
    remove_db_file()
    
    yield
    
    # Clean up after test
    try:
        db = Database()
        db.close()
    except:
        pass
    remove_db_file()

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
    assert "created_at" in data
    assert "updated_at" in data

def test_read_notes():
    # Create a test note first
    client.post(
        "/api/notes/",
        json={"title": "Test Note", "content": "Test Content"}
    )
    
    # Test getting all notes
    response = client.get("/api/notes/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["title"] == "Test Note"
    
    # Test getting specific note
    note_id = data[0]["id"]
    response = client.get(f"/api/notes/{note_id}")
    assert response.status_code == 200
    assert response.json()["id"] == note_id

def test_update_note():
    # Create a test note
    create_response = client.post(
        "/api/notes/",
        json={"title": "Original Title", "content": "Original Content"}
    )
    note_id = create_response.json()["id"]
    
    # Update the note
    update_response = client.put(
        f"/api/notes/{note_id}",
        json={"title": "Updated Title", "content": "Updated Content"}
    )
    
    assert update_response.status_code == 200
    updated_data = update_response.json()
    assert updated_data["title"] == "Updated Title"
    assert updated_data["content"] == "Updated Content"
    
    # Verify the update
    get_response = client.get(f"/api/notes/{note_id}")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Updated Title"

def test_delete_note():
    # Create a test note
    create_response = client.post(
        "/api/notes/",
        json={"title": "To Be Deleted", "content": "This will be deleted"}
    )
    note_id = create_response.json()["id"]
    
    # Delete the note
    delete_response = client.delete(f"/api/notes/{note_id}")
    assert delete_response.status_code == 200
    
    # Verify the note is deleted
    get_response = client.get(f"/api/notes/{note_id}")
    assert get_response.status_code == 404
