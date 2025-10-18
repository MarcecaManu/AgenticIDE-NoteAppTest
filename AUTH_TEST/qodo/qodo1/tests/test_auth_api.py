import pytest
import json
import os
import sys
from fastapi.testclient import TestClient

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app
from database import FileDatabase

# Test database file
TEST_DB_FILE = "test_users.json"

@pytest.fixture(scope="function")
def client():
    """Create a test client with a clean database for each test"""
    # Use a test database in the tests directory
    test_db_path = os.path.join(os.path.dirname(__file__), TEST_DB_FILE)
    
    # Use a test database
    from database import db
    db.db_file = test_db_path
    db.users = []
    db.next_id = 1
    
    # Clear token blacklist for each test
    from auth import token_blacklist
    token_blacklist.clear()
    
    # Clean up any existing test database
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    client = TestClient(app)
    yield client
    
    # Clean up after test
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

@pytest.fixture
def test_user():
    """Test user data"""
    return {
        "username": "testuser",
        "password": "testpass123"
    }

class TestAuthAPI:
    
    def test_register_new_user(self, client, test_user):
        """Test user registration with valid data"""
        response = client.post("/api/auth/register", json=test_user)
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == test_user["username"]
        assert "id" in data
        assert data["id"] == 1

    def test_register_duplicate_user(self, client, test_user):
        """Test registration with duplicate username"""
        # Register user first time
        client.post("/api/auth/register", json=test_user)
        
        # Try to register same user again
        response = client.post("/api/auth/register", json=test_user)
        
        assert response.status_code == 400
        data = response.json()
        assert "already registered" in data["detail"].lower()

    def test_register_invalid_username(self, client):
        """Test registration with invalid username"""
        invalid_user = {"username": "ab", "password": "testpass123"}
        response = client.post("/api/auth/register", json=invalid_user)
        
        assert response.status_code == 400
        data = response.json()
        assert "at least 3 characters" in data["detail"]

    def test_register_invalid_password(self, client):
        """Test registration with invalid password"""
        invalid_user = {"username": "testuser", "password": "123"}
        response = client.post("/api/auth/register", json=invalid_user)
        
        assert response.status_code == 400
        data = response.json()
        assert "at least 6 characters" in data["detail"]

    def test_login_valid_credentials(self, client, test_user):
        """Test login with valid credentials"""
        # Register user first
        client.post("/api/auth/register", json=test_user)
        
        # Login
        response = client.post("/api/auth/login", json=test_user)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    def test_login_invalid_username(self, client, test_user):
        """Test login with non-existent username"""
        response = client.post("/api/auth/login", json={
            "username": "nonexistent",
            "password": "password123"
        })
        
        assert response.status_code == 401
        data = response.json()
        assert "incorrect username or password" in data["detail"].lower()

    def test_login_invalid_password(self, client, test_user):
        """Test login with wrong password"""
        # Register user first
        client.post("/api/auth/register", json=test_user)
        
        # Try login with wrong password
        response = client.post("/api/auth/login", json={
            "username": test_user["username"],
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        data = response.json()
        assert "incorrect username or password" in data["detail"].lower()

    def test_get_profile_with_valid_token(self, client, test_user):
        """Test getting user profile with valid token"""
        # Register and login
        client.post("/api/auth/register", json=test_user)
        login_response = client.post("/api/auth/login", json=test_user)
        token = login_response.json()["access_token"]
        
        # Get profile
        response = client.get("/api/auth/profile", headers={
            "Authorization": f"Bearer {token}"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user["username"]
        assert "id" in data

    def test_get_profile_without_token(self, client):
        """Test getting profile without authentication token"""
        response = client.get("/api/auth/profile")
        
        assert response.status_code == 403  # FastAPI returns 403 for missing auth

    def test_get_profile_with_invalid_token(self, client):
        """Test getting profile with invalid token"""
        response = client.get("/api/auth/profile", headers={
            "Authorization": "Bearer invalid_token"
        })
        
        assert response.status_code == 401
        data = response.json()
        assert "could not validate credentials" in data["detail"].lower()

    def test_logout_with_valid_token(self, client, test_user):
        """Test logout with valid token"""
        # Register and login
        client.post("/api/auth/register", json=test_user)
        login_response = client.post("/api/auth/login", json=test_user)
        token = login_response.json()["access_token"]
        
        # Logout
        response = client.post("/api/auth/logout", headers={
            "Authorization": f"Bearer {token}"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "successfully logged out" in data["message"].lower()

    def test_logout_without_token(self, client):
        """Test logout without token"""
        response = client.post("/api/auth/logout")
        
        assert response.status_code == 403  # FastAPI returns 403 for missing auth

    def test_profile_access_after_logout(self, client, test_user):
        """Test that profile cannot be accessed after logout"""
        # Register and login
        client.post("/api/auth/register", json=test_user)
        login_response = client.post("/api/auth/login", json=test_user)
        token = login_response.json()["access_token"]
        
        # Logout
        client.post("/api/auth/logout", headers={
            "Authorization": f"Bearer {token}"
        })
        
        # Try to access profile with the same token
        response = client.get("/api/auth/profile", headers={
            "Authorization": f"Bearer {token}"
        })
        
        assert response.status_code == 401
        data = response.json()
        assert "could not validate credentials" in data["detail"].lower()

    def test_user_data_persistence(self, client, test_user):
        """Test that user data persists across requests"""
        # Register user
        register_response = client.post("/api/auth/register", json=test_user)
        assert register_response.status_code == 201
        user_id = register_response.json()["id"]
        
        # Login and get profile
        login_response = client.post("/api/auth/login", json=test_user)
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        profile_response = client.get("/api/auth/profile", headers={
            "Authorization": f"Bearer {token}"
        })
        
        # Debug: print the response if it fails
        assert profile_response.status_code == 200, f"Profile request failed: {profile_response.status_code} - {profile_response.text}"
        
        profile_data = profile_response.json()
        assert "username" in profile_data, f"Username not in profile response: {profile_data}"
        assert "id" in profile_data, f"ID not in profile response: {profile_data}"
        assert profile_data["username"] == test_user["username"]
        assert profile_data["id"] == user_id
        
        # Verify data file was created
        test_db_path = os.path.join(os.path.dirname(__file__), TEST_DB_FILE)
        assert os.path.exists(test_db_path)
        
        # Verify data in file
        with open(test_db_path, 'r') as f:
            db_data = json.load(f)
            assert len(db_data["users"]) == 1
            assert db_data["users"][0]["username"] == test_user["username"]
            assert db_data["users"][0]["id"] == user_id