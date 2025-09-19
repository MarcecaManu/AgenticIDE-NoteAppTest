import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import database
from main import app
from database import get_db, Base

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def test_engine():
    """Create a test database engine."""
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
    return engine

@pytest.fixture
def test_db(test_engine):
    """Set up a test database and client."""
    # Create tables in test database
    database.init_db(test_engine)
    
    # Create a new session factory
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    # Override dependencies
    app.dependency_overrides[get_db] = override_get_db
    
    # Create test client
    test_client = TestClient(app)
    
    # Return test client
    yield test_client
    
    # Clean up
    Base.metadata.drop_all(bind=test_engine)
    app.dependency_overrides.clear()

def test_register(test_db):
    client = test_db
    response = client.post(
        "/api/auth/register",
        json={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"

def test_login(test_db):
    client = test_db
    # First register a user
    client.post(
        "/api/auth/register",
        json={"username": "testuser2", "password": "testpass2"}
    )

    # Then try to login
    response = client.post(
        "/api/auth/login",
        data={"username": "testuser2", "password": "testpass2"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_get_profile(test_db):
    client = test_db
    # Register and login first
    client.post(
        "/api/auth/register",
        json={"username": "testuser3", "password": "testpass3"}
    )
    login_response = client.post(
        "/api/auth/login",
        data={"username": "testuser3", "password": "testpass3"}
    )
    token = login_response.json()["access_token"]

    # Get profile
    response = client.get(
        "/api/auth/profile",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser3"

def test_logout(test_db):
    client = test_db
    # Register and login first
    client.post(
        "/api/auth/register",
        json={"username": "testuser4", "password": "testpass4"}
    )
    login_response = client.post(
        "/api/auth/login",
        data={"username": "testuser4", "password": "testpass4"}
    )
    token = login_response.json()["access_token"]

    # Logout
    response = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Successfully logged out"

    # Try to access profile after logout (should fail)
    response = client.get(
        "/api/auth/profile",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401
