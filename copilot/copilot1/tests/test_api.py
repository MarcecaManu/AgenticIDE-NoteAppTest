import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import os
import sys

# Add the parent directory to Python path to make the backend package importable
sys.path.append(str(Path(__file__).parent.parent))

from backend.app.main import app
from backend.app import models

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch):
    # Use a test database in the same directory as the test file
    test_db = Path(__file__).parent / "test_notes.db"
    
    # Patch the database path in models.py
    def mock_get_db():
        conn = models.sqlite3.connect(test_db)
        conn.row_factory = models.dict_factory
        return conn
    
    monkeypatch.setattr(models, "get_db", mock_get_db)
    
    # Clean up any existing test database
    if test_db.exists():
        os.remove(test_db)
    
    # Initialize the test database
    conn = models.sqlite3.connect(test_db)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    
    yield
    
    # Clean up after tests
    if test_db.exists():
        os.remove(test_db)

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

def test_get_note():
    # First create a note
    create_response = client.post(
        "/api/notes/",
        json={"title": "Test Note", "content": "Test Content"}
    )
    note_id = create_response.json()["id"]

    # Then get the note
    response = client.get(f"/api/notes/{note_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Note"
    assert data["content"] == "Test Content"
    assert data["id"] == note_id

def test_update_note():
    # First create a note
    create_response = client.post(
        "/api/notes/",
        json={"title": "Test Note", "content": "Test Content"}
    )
    note_id = create_response.json()["id"]

    # Then update the note
    update_response = client.put(
        f"/api/notes/{note_id}",
        json={"title": "Updated Note", "content": "Updated Content"}
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["title"] == "Updated Note"
    assert data["content"] == "Updated Content"
    assert data["id"] == note_id

def test_delete_note():
    # First create a note
    create_response = client.post(
        "/api/notes/",
        json={"title": "Test Note", "content": "Test Content"}
    )
    note_id = create_response.json()["id"]

    # Then delete the note
    delete_response = client.delete(f"/api/notes/{note_id}")
    assert delete_response.status_code == 200

    # Verify the note is deleted
    get_response = client.get(f"/api/notes/{note_id}")
    assert get_response.status_code == 404