import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database import Base
from backend.main import app, get_db
from backend import models  # Import models to ensure tables are created

# Test database setup
TEST_DB_URL = "sqlite:///./test.db"
engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables for testing
def setup_module(module):
    Base.metadata.create_all(bind=engine)

def teardown_module(module):
    Base.metadata.drop_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def cleanup_tables():
    # Setup - optionally create any test data here
    yield
    # Cleanup - clear all tables after each test
    db = next(override_get_db())
    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())
    db.commit()

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

def test_create_note(client):
    # Test creating a new note
    response = client.post(
        "/api/notes/",
        json={"title": "Test Note", "content": "Test Content"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Note"
    assert data["content"] == "Test Content"
    assert "id" in data
    assert "createdAt" in data
    assert "updatedAt" in data

def test_read_notes(client):
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

    # Test getting note by ID
    note_id = data[0]["id"]
    response = client.get(f"/api/notes/{note_id}")
    assert response.status_code == 200
    assert response.json()["id"] == note_id

def test_update_note(client):
    # Create a test note
    response = client.post(
        "/api/notes/",
        json={"title": "Original Title", "content": "Original Content"}
    )
    note_id = response.json()["id"]
    
    # Test updating the note
    response = client.put(
        f"/api/notes/{note_id}",
        json={"title": "Updated Title", "content": "Updated Content"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["content"] == "Updated Content"

def test_delete_note(client):
    # Create a test note
    response = client.post(
        "/api/notes/",
        json={"title": "Test Note", "content": "Test Content"}
    )
    note_id = response.json()["id"]
    
    # Test deleting the note
    response = client.delete(f"/api/notes/{note_id}")
    assert response.status_code == 200
    
    # Verify the note is deleted
    response = client.get(f"/api/notes/{note_id}")
    assert response.status_code == 404
