import pytest
import httpx
import asyncio
import sys
import os
import json
from pathlib import Path

# Add backend directory to Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from fastapi.testclient import TestClient
from main import app
from database import db

class TestAuthAPI:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and teardown for each test"""
        # Clean up database before each test
        if os.path.exists("users.json"):
            os.remove("users.json")
        db.users = []
        db.next_id = 1
        
        # Clear token blacklist
        from auth import token_blacklist
        token_blacklist.clear()
        
        yield
        
        # Clean up after test
        if os.path.exists("users.json"):
            os.remove("users.json")

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    def test_register_new_user(self, client):
        """Test user registration with valid data"""
        user_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testuser"
        assert "id" in data
        assert data["id"] == 1

    def test_register_duplicate_user(self, client):
        """Test registration with existing username"""
        user_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        
        # Register first user
        response1 = client.post("/api/auth/register", json=user_data)
        assert response1.status_code == 201
        
        # Try to register same username again
        response2 = client.post("/api/auth/register", json=user_data)
        assert response2.status_code == 400
        data = response2.json()
        assert "already registered" in data["detail"].lower()

    def test_login_valid_credentials(self, client):
        """Test login with valid credentials"""
        # First register a user
        user_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        client.post("/api/auth/register", json=user_data)
        
        # Now login
        login_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        # Register a user first
        user_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        client.post("/api/auth/register", json=user_data)
        
        # Try login with wrong password
        login_data = {
            "username": "testuser",
            "password": "wrongpassword"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert "incorrect" in data["detail"].lower()

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        login_data = {
            "username": "nonexistent",
            "password": "somepassword"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert "incorrect" in data["detail"].lower()

    def test_get_profile_with_valid_token(self, client):
        """Test getting user profile with valid token"""
        # Register and login to get token
        user_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        client.post("/api/auth/register", json=user_data)
        
        login_response = client.post("/api/auth/login", json=user_data)
        token = login_response.json()["access_token"]
        
        # Get profile
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/auth/profile", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["id"] == 1

    def test_get_profile_without_token(self, client):
        """Test getting profile without authentication token"""
        response = client.get("/api/auth/profile")
        
        assert response.status_code == 403  # FastAPI returns 403 for missing auth

    def test_get_profile_with_invalid_token(self, client):
        """Test getting profile with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/auth/profile", headers=headers)
        
        assert response.status_code == 401
        data = response.json()
        assert "could not validate credentials" in data["detail"].lower()

    def test_logout_with_valid_token(self, client):
        """Test logout with valid token"""
        # Register and login to get token
        user_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        client.post("/api/auth/register", json=user_data)
        
        login_response = client.post("/api/auth/login", json=user_data)
        token = login_response.json()["access_token"]
        
        # Logout
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/api/auth/logout", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "logged out" in data["message"].lower()

    def test_logout_without_token(self, client):
        """Test logout without authentication token"""
        response = client.post("/api/auth/logout")
        
        assert response.status_code == 403  # FastAPI returns 403 for missing auth

    def test_token_blacklist_after_logout(self, client):
        """Test that token is blacklisted after logout"""
        # Register and login to get token
        user_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        client.post("/api/auth/register", json=user_data)
        
        login_response = client.post("/api/auth/login", json=user_data)
        token = login_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Verify token works before logout
        profile_response = client.get("/api/auth/profile", headers=headers)
        assert profile_response.status_code == 200
        
        # Logout
        logout_response = client.post("/api/auth/logout", headers=headers)
        assert logout_response.status_code == 200
        
        # Try to use token after logout - should fail
        profile_response_after = client.get("/api/auth/profile", headers=headers)
        assert profile_response_after.status_code == 401

    def test_password_hashing(self, client):
        """Test that passwords are properly hashed and not stored in plain text"""
        user_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        
        # Register user
        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code == 201
        
        # Check that password is hashed in database
        user = db.get_user_by_username("testuser")
        assert user is not None
        assert user.hashed_password != "testpassword123"  # Should be hashed
        assert user.hashed_password.startswith("$2b$")  # bcrypt hash format

    def test_data_persistence(self, client):
        """Test that user data persists to file"""
        user_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        
        # Register user
        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code == 201
        
        # Check that users.json file was created
        assert os.path.exists("users.json")
        
        # Check file contents
        with open("users.json", 'r') as f:
            data = json.load(f)
            assert "users" in data
            assert len(data["users"]) == 1
            assert data["users"][0]["username"] == "testuser"
            assert data["users"][0]["id"] == 1

if __name__ == "__main__":
    pytest.main([__file__, "-v"])