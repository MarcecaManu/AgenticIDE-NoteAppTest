import pytest
from fastapi.testclient import TestClient
import os
import sys

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.main import app, db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_teardown():
    # Setup: ensure we're using a test database
    test_db_path = "data/test_notes.json"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Clear the database before each test
    db.truncate()
    
    yield
    
    # Teardown: clean up test database
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    db.truncate()

def test_create_note():
    # Test creating a new note
    response = client.post(
        "/api/notes/",
        json={"title": "Test Note", "content": "This is a test note"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Note"
    assert data["content"] == "This is a test note"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

def test_get_notes():
    # Create test notes
    client.post(
        "/api/notes/",
        json={"title": "Test Note 1", "content": "Content 1"}
    )
    client.post(
        "/api/notes/",
        json={"title": "Test Note 2", "content": "Content 2"}
    )

    # Test getting all notes
    response = client.get("/api/notes/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Test Note 1"
    assert data[1]["title"] == "Test Note 2"

def test_get_note_by_id():
    # Create a test note
    create_response = client.post(
        "/api/notes/",
        json={"title": "Test Note", "content": "This is a test note"}
    )
    note_id = create_response.json()["id"]

    # Test getting the note by ID
    response = client.get(f"/api/notes/{note_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == note_id
    assert data["title"] == "Test Note"
    assert data["content"] == "This is a test note"

def test_update_note():
    # Create a test note
    create_response = client.post(
        "/api/notes/",
        json={"title": "Original Title", "content": "Original content"}
    )
    note_id = create_response.json()["id"]

    # Test updating the note
    response = client.put(
        f"/api/notes/{note_id}",
        json={"title": "Updated Title", "content": "Updated content"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == note_id
    assert data["title"] == "Updated Title"
    assert data["content"] == "Updated content"

    # Verify the update persisted
    get_response = client.get(f"/api/notes/{note_id}")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["title"] == "Updated Title"
    assert get_data["content"] == "Updated content"

def test_delete_note():
    # Create a test note
    create_response = client.post(
        "/api/notes/",
        json={"title": "Test Note", "content": "This is a test note"}
    )
    note_id = create_response.json()["id"]

    # Test deleting the note
    response = client.delete(f"/api/notes/{note_id}")
    assert response.status_code == 200

    # Verify the note was deleted
    get_response = client.get(f"/api/notes/{note_id}")
    assert get_response.status_code == 404

def test_search_notes():
    # Create test notes
    client.post(
        "/api/notes/",
        json={"title": "Python Tutorial", "content": "Learn Python"}
    )
    client.post(
        "/api/notes/",
        json={"title": "JavaScript Guide", "content": "Learn JavaScript"}
    )

    # Test searching notes
    response = client.get("/api/notes/?search=Python")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Python Tutorial" 