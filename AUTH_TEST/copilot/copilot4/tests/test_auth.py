from fastapi.testclient import TestClient
from backend.main import app
from backend.database import Base, engine
import pytest

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    # Create tables before each test
    Base.metadata.create_all(bind=engine)
    yield
    # Drop tables after each test
    Base.metadata.drop_all(bind=engine)

def test_register():
    response = client.post(
        "/api/auth/register",
        json={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert "id" in data

def test_login():
    # First register a user
    client.post(
        "/api/auth/register",
        json={"username": "testuser", "password": "testpass"}
    )
    
    # Then try to login
    response = client.post(
        "/api/auth/login",
        data={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_logout():
    response = client.post("/api/auth/logout")
    assert response.status_code == 200
    assert response.json() == {"message": "Successfully logged out"}

def test_profile():
    # First register and login
    client.post(
        "/api/auth/register",
        json={"username": "testuser", "password": "testpass"}
    )
    login_response = client.post(
        "/api/auth/login",
        data={"username": "testuser", "password": "testpass"}
    )
    token = login_response.json()["access_token"]
    
    # Then try to access profile
    response = client.get(
        "/api/auth/profile",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
