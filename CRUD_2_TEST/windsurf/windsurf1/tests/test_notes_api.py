import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app, DB_PATH, init_db
import sqlite3

@pytest.fixture(autouse=True)
def setup_test_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()
    yield
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

@pytest.fixture
def client():
    return TestClient(app)

def test_create_note(client):
    response = client.post(
        "/api/notes/",
        json={"title": "Test Note", "content": "This is a test note"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Note"
    assert data["content"] == "This is a test note"
    assert "id" in data
    assert "createdAt" in data
    assert "updatedAt" in data

def test_get_all_notes(client):
    client.post("/api/notes/", json={"title": "Note 1", "content": "Content 1"})
    client.post("/api/notes/", json={"title": "Note 2", "content": "Content 2"})
    
    response = client.get("/api/notes/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] in ["Note 1", "Note 2"]
    assert data[1]["title"] in ["Note 1", "Note 2"]

def test_get_note_by_id(client):
    create_response = client.post(
        "/api/notes/",
        json={"title": "Specific Note", "content": "Specific content"}
    )
    note_id = create_response.json()["id"]
    
    response = client.get(f"/api/notes/{note_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == note_id
    assert data["title"] == "Specific Note"
    assert data["content"] == "Specific content"

def test_get_note_not_found(client):
    response = client.get("/api/notes/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"

def test_update_note(client):
    create_response = client.post(
        "/api/notes/",
        json={"title": "Original Title", "content": "Original content"}
    )
    note_id = create_response.json()["id"]
    
    response = client.put(
        f"/api/notes/{note_id}",
        json={"title": "Updated Title", "content": "Updated content"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == note_id
    assert data["title"] == "Updated Title"
    assert data["content"] == "Updated content"
    assert data["updatedAt"] != data["createdAt"]

def test_update_note_partial(client):
    create_response = client.post(
        "/api/notes/",
        json={"title": "Original Title", "content": "Original content"}
    )
    note_id = create_response.json()["id"]
    
    response = client.put(
        f"/api/notes/{note_id}",
        json={"title": "New Title Only"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Title Only"
    assert data["content"] == "Original content"

def test_update_note_not_found(client):
    response = client.put(
        "/api/notes/9999",
        json={"title": "Updated", "content": "Updated"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"

def test_delete_note(client):
    create_response = client.post(
        "/api/notes/",
        json={"title": "To Delete", "content": "Will be deleted"}
    )
    note_id = create_response.json()["id"]
    
    response = client.delete(f"/api/notes/{note_id}")
    assert response.status_code == 204
    
    get_response = client.get(f"/api/notes/{note_id}")
    assert get_response.status_code == 404

def test_delete_note_not_found(client):
    response = client.delete("/api/notes/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"

def test_create_note_empty_fields(client):
    response = client.post(
        "/api/notes/",
        json={"title": "", "content": ""}
    )
    assert response.status_code == 201

def test_notes_persistence(client):
    client.post("/api/notes/", json={"title": "Persistent Note", "content": "Should persist"})
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM notes")
    count = cursor.fetchone()[0]
    conn.close()
    
    assert count == 1
