import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.database import Base, get_db

# Use a separate test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

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
    
    response = client.get("/api/notes/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["title"] == "Test Note"

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

def test_delete_note():
    # Create a test note
    create_response = client.post(
        "/api/notes/",
        json={"title": "Test Note", "content": "Test Content"}
    )
    note_id = create_response.json()["id"]
    
    # Delete the note
    delete_response = client.delete(f"/api/notes/{note_id}")
    assert delete_response.status_code == 200
    
    # Verify the note is deleted
    get_response = client.get(f"/api/notes/{note_id}")
    assert get_response.status_code == 404
