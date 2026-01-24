import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app, DB_PATH
import sqlite3

@pytest.fixture(autouse=True)
def setup_and_teardown():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            createdAt TEXT NOT NULL,
            updatedAt TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    
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
    assert data["id"] == 1

def test_get_all_notes(client):
    client.post("/api/notes/", json={"title": "Note 1", "content": "Content 1"})
    client.post("/api/notes/", json={"title": "Note 2", "content": "Content 2"})
    client.post("/api/notes/", json={"title": "Note 3", "content": "Content 3"})
    
    response = client.get("/api/notes/")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["title"] == "Note 3"
    assert data[1]["title"] == "Note 2"
    assert data[2]["title"] == "Note 1"

def test_get_note_by_id(client):
    create_response = client.post(
        "/api/notes/",
        json={"title": "Specific Note", "content": "Specific Content"}
    )
    note_id = create_response.json()["id"]
    
    response = client.get(f"/api/notes/{note_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == note_id
    assert data["title"] == "Specific Note"
    assert data["content"] == "Specific Content"

def test_get_note_by_id_not_found(client):
    response = client.get("/api/notes/999")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"

def test_update_note(client):
    create_response = client.post(
        "/api/notes/",
        json={"title": "Original Title", "content": "Original Content"}
    )
    note_id = create_response.json()["id"]
    
    response = client.put(
        f"/api/notes/{note_id}",
        json={"title": "Updated Title", "content": "Updated Content"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == note_id
    assert data["title"] == "Updated Title"
    assert data["content"] == "Updated Content"
    assert data["createdAt"] != data["updatedAt"]

def test_update_note_partial(client):
    create_response = client.post(
        "/api/notes/",
        json={"title": "Original Title", "content": "Original Content"}
    )
    note_id = create_response.json()["id"]
    
    response = client.put(
        f"/api/notes/{note_id}",
        json={"title": "Updated Title Only"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title Only"
    assert data["content"] == "Original Content"

def test_update_note_not_found(client):
    response = client.put(
        "/api/notes/999",
        json={"title": "Updated Title", "content": "Updated Content"}
    )
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"

def test_delete_note(client):
    create_response = client.post(
        "/api/notes/",
        json={"title": "Note to Delete", "content": "This will be deleted"}
    )
    note_id = create_response.json()["id"]
    
    response = client.delete(f"/api/notes/{note_id}")
    
    assert response.status_code == 204
    
    get_response = client.get(f"/api/notes/{note_id}")
    assert get_response.status_code == 404

def test_delete_note_not_found(client):
    response = client.delete("/api/notes/999")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"

def test_create_note_empty_fields(client):
    response = client.post(
        "/api/notes/",
        json={"title": "", "content": ""}
    )
    
    assert response.status_code == 201

def test_get_all_notes_empty(client):
    response = client.get("/api/notes/")
    
    assert response.status_code == 200
    assert response.json() == []

def test_full_crud_workflow(client):
    create_response = client.post(
        "/api/notes/",
        json={"title": "Workflow Note", "content": "Initial content"}
    )
    assert create_response.status_code == 201
    note_id = create_response.json()["id"]
    
    get_response = client.get(f"/api/notes/{note_id}")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Workflow Note"
    
    update_response = client.put(
        f"/api/notes/{note_id}",
        json={"title": "Updated Workflow", "content": "Updated content"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated Workflow"
    
    delete_response = client.delete(f"/api/notes/{note_id}")
    assert delete_response.status_code == 204
    
    final_get_response = client.get(f"/api/notes/{note_id}")
    assert final_get_response.status_code == 404
