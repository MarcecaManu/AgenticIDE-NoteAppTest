import pytest
from fastapi.testclient import TestClient
from backend.main import app, get_notes_table
from tinydb import TinyDB
from tinydb.storages import MemoryStorage

@pytest.fixture(autouse=True)
def test_db():
    # Create an in-memory database for testing
    db = TinyDB(storage=MemoryStorage)
    
    # Override the get_notes_table dependency
    def override_get_notes():
        return db.table('notes')
    
    app.dependency_overrides[get_notes_table] = override_get_notes
    
    yield db
    
    # Cleanup
    app.dependency_overrides.clear()
    db.close()

@pytest.fixture
def test_client(test_db):
    return TestClient(app)

def test_create_note(test_client):
    response = test_client.post(
        "/api/notes",
        json={"title": "Test Note", "content": "Test Content"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Note"
    assert data["content"] == "Test Content"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

def test_get_notes(test_client):
    # Create a test note first
    test_client.post(
        "/api/notes",
        json={"title": "Test Note", "content": "Test Content"}
    )
    
    response = test_client.get("/api/notes")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["title"] == "Test Note"

def test_update_note(test_client):
    # Create a test note first
    create_response = test_client.post(
        "/api/notes",
        json={"title": "Original Title", "content": "Original Content"}
    )
    note_id = create_response.json()["id"]
    
    # Update the note
    update_response = test_client.put(
        f"/api/notes/{note_id}",
        json={"title": "Updated Title", "content": "Updated Content"}
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["title"] == "Updated Title"
    assert data["content"] == "Updated Content"
    assert data["id"] == note_id

def test_delete_note(test_client):
    # Create a test note first
    create_response = test_client.post(
        "/api/notes",
        json={"title": "Test Note", "content": "Test Content"}
    )
    note_id = create_response.json()["id"]
    
    # Delete the note
    delete_response = test_client.delete(f"/api/notes/{note_id}")
    assert delete_response.status_code == 200
    
    # Verify note is deleted
    get_response = test_client.get(f"/api/notes/{note_id}")
    assert get_response.status_code == 404
