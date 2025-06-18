import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import os
import json
import sys
from pathlib import Path
import shutil

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

# Override the database file path for tests
import backend.database
TEST_DB_FILE = 'test_notes.json'
backend.database.db = backend.database.TinyDB(TEST_DB_FILE)

from backend.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_teardown():
    # Setup: ensure we start with a clean test database
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except PermissionError:
            pass
    
    # Create a fresh database for each test
    backend.database.db = backend.database.TinyDB(TEST_DB_FILE)
    backend.database.notes_table = backend.database.db.table('notes')
    
    yield
    
    # Teardown: clean up test database
    if os.path.exists(TEST_DB_FILE):
        try:
            backend.database.db.close()
            os.remove(TEST_DB_FILE)
        except PermissionError:
            pass

def test_create_note():
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
    # Create a test note first
    client.post(
        "/api/notes/",
        json={"title": "Test Note 1", "content": "Content 1"}
    )
    client.post(
        "/api/notes/",
        json={"title": "Test Note 2", "content": "Content 2"}
    )
    
    response = client.get("/api/notes/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Test Note 1"
    assert data[1]["title"] == "Test Note 2"

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
    data = update_response.json()
    assert data["title"] == "Updated Title"
    assert data["content"] == "Updated Content"
    assert data["id"] == note_id
    
    # Verify the update
    get_response = client.get(f"/api/notes/{note_id}")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Updated Title"

def test_delete_note():
    # Create a test note
    create_response = client.post(
        "/api/notes/",
        json={"title": "To Be Deleted", "content": "This note will be deleted"}
    )
    note_id = create_response.json()["id"]
    
    # Delete the note
    delete_response = client.delete(f"/api/notes/{note_id}")
    assert delete_response.status_code == 200
    
    # Verify the note is deleted
    get_response = client.get(f"/api/notes/{note_id}")
    assert get_response.status_code == 404 