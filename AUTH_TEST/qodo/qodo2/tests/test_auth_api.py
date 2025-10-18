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
from auth import token_blacklist

class TestAuthAPI:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and teardown for each test"""
        # Clear database and token blacklist before each test
        db.users = []
        db.next_id = 1
        token_blacklist.clear()
        
        # Remove test database file if it exists
        if os.path.exists(db.db_file):
            os.remove(db.db_file)
        
        yield
        
        # Cleanup after test
        if os.path.exists(db.db_file):
            os.remove(db.db_file)

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    def test_register_new_user(self, client):
        """Test user registration with valid data"""
        user_data = {
            "username": "testuser",
            "password": "testpass123"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testuser"
        assert data["id"] == 1
        assert "password" not in data  # Password should not be in response

    def test_register_duplicate_user(self, client):
        """Test registration with existing username"""
        user_data = {
            "username": "testuser",
            "password": "testpass123"
        }
        
        # Register first user
        response1 = client.post("/api/auth/register", json=user_data)
        assert response1.status_code == 201
        
        # Try to register same username again
        response2 = client.post("/api/auth/register", json=user_data)
        assert response2.status_code == 400
        assert "already registered" in response2.json()["detail"]

    def test_register_invalid_data(self, client):
        """Test registration with invalid data"""
        # Test short username
        response1 = client.post("/api/auth/register", json={
            "username": "ab",
            "password": "testpass123"
        })
        assert response1.status_code == 400
        assert "at least 3 characters" in response1.json()["detail"]
        
        # Test short password
        response2 = client.post("/api/auth/register", json={
            "username": "testuser",
            "password": "12345"
        })
        assert response2.status_code == 400
        assert "at least 6 characters" in response2.json()["detail"]

    def test_login_valid_credentials(self, client):
        """Test login with valid credentials"""
        # First register a user
        register_data = {
            "username": "testuser",
            "password": "testpass123"
        }
        client.post("/api/auth/register", json=register_data)
        
        # Now login
        login_data = {
            "username": "testuser",
            "password": "testpass123"
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
        register_data = {
            "username": "testuser",
            "password": "testpass123"
        }
        client.post("/api/auth/register", json=register_data)
        
        # Try login with wrong password
        login_data = {
            "username": "testuser",
            "password": "wrongpassword"
        }
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        login_data = {
            "username": "nonexistent",
            "password": "testpass123"
        }
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_get_profile_with_valid_token(self, client):
        """Test getting user profile with valid token"""
        # Register and login to get token
        register_data = {
            "username": "testuser",
            "password": "testpass123"
        }
        client.post("/api/auth/register", json=register_data)
        
        login_response = client.post("/api/auth/login", json=register_data)
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
        assert "Could not validate credentials" in response.json()["detail"]

    def test_logout_with_valid_token(self, client):
        """Test logout with valid token"""
        # Register and login to get token
        register_data = {
            "username": "testuser",
            "password": "testpass123"
        }
        client.post("/api/auth/register", json=register_data)
        
        login_response = client.post("/api/auth/login", json=register_data)
        token = login_response.json()["access_token"]
        
        # Logout
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/api/auth/logout", headers=headers)
        
        assert response.status_code == 200
        assert "Successfully logged out" in response.json()["message"]
        
        # Verify token is blacklisted by trying to access profile
        profile_response = client.get("/api/auth/profile", headers=headers)
        assert profile_response.status_code == 401

    def test_logout_without_token(self, client):
        """Test logout without authentication token"""
        response = client.post("/api/auth/logout")
        
        assert response.status_code == 403  # FastAPI returns 403 for missing auth

    def test_logout_with_invalid_token(self, client):
        """Test logout with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.post("/api/auth/logout", headers=headers)
        
        assert response.status_code == 401

    def test_complete_user_flow(self, client):
        """Test complete user flow: register -> login -> profile -> logout"""
        # 1. Register
        register_data = {
            "username": "flowuser",
            "password": "flowpass123"
        }
        register_response = client.post("/api/auth/register", json=register_data)
        assert register_response.status_code == 201
        
        # 2. Login
        login_response = client.post("/api/auth/login", json=register_data)
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # 3. Get Profile
        headers = {"Authorization": f"Bearer {token}"}
        profile_response = client.get("/api/auth/profile", headers=headers)
        assert profile_response.status_code == 200
        assert profile_response.json()["username"] == "flowuser"
        
        # 4. Logout
        logout_response = client.post("/api/auth/logout", headers=headers)
        assert logout_response.status_code == 200
        
        # 5. Verify token is invalidated
        profile_after_logout = client.get("/api/auth/profile", headers=headers)
        assert profile_after_logout.status_code == 401

    def test_data_persistence(self, client):
        """Test that user data persists across requests"""
        # Register a user
        register_data = {
            "username": "persistuser",
            "password": "persistpass123"
        }
        client.post("/api/auth/register", json=register_data)
        
        # Verify user exists by logging in
        login_response = client.post("/api/auth/login", json=register_data)
        assert login_response.status_code == 200
        
        # Check that database file was created
        assert os.path.exists(db.db_file)
        
        # Verify data in file
        with open(db.db_file, 'r') as f:
            data = json.load(f)
            assert len(data['users']) == 1
            assert data['users'][0]['username'] == 'persistuser'
            assert data['users'][0]['id'] == 1
            # Password should be hashed, not plain text
            assert data['users'][0]['hashed_password'] != 'persistpass123'
            assert len(data['users'][0]['hashed_password']) > 20  # Bcrypt hashes are long

if __name__ == "__main__":
    pytest.main([__file__, "-v"])