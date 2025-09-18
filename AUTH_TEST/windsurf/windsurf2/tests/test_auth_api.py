import pytest
import os
import sqlite3
from fastapi.testclient import TestClient
from datetime import datetime, timezone
import sys
import tempfile

# Add the backend directory to the path so we can import the app
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app, DATABASE_PATH, init_db

class TestAuthAPI:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        # Create a temporary database for testing
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        
        # Override the database path
        import main
        main.DATABASE_PATH = self.test_db.name
        
        # Initialize the test database
        init_db()
        
        # Create test client
        self.client = TestClient(app)
        
        yield
        
        # Cleanup: remove test database
        if os.path.exists(self.test_db.name):
            os.unlink(self.test_db.name)

    def test_register_new_user(self):
        """Test user registration with valid data"""
        user_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        
        response = self.client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "user_id" in data
        assert data["message"] == "User registered successfully"
        assert isinstance(data["user_id"], int)

    def test_register_duplicate_user(self):
        """Test registration with existing username"""
        user_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        
        # Register user first time
        response1 = self.client.post("/api/auth/register", json=user_data)
        assert response1.status_code == 200
        
        # Try to register same user again
        response2 = self.client.post("/api/auth/register", json=user_data)
        assert response2.status_code == 400
        data = response2.json()
        assert data["detail"] == "Username already registered"

    def test_login_valid_credentials(self):
        """Test login with valid credentials"""
        # First register a user
        user_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        self.client.post("/api/auth/register", json=user_data)
        
        # Now login
        login_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        
        response = self.client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        # Register a user first
        user_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        self.client.post("/api/auth/register", json=user_data)
        
        # Try login with wrong password
        login_data = {
            "username": "testuser",
            "password": "wrongpassword"
        }
        
        response = self.client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Incorrect username or password"

    def test_login_nonexistent_user(self):
        """Test login with non-existent user"""
        login_data = {
            "username": "nonexistent",
            "password": "somepassword"
        }
        
        response = self.client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Incorrect username or password"

    def test_get_profile_valid_token(self):
        """Test getting profile with valid token"""
        # Register and login to get token
        user_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        self.client.post("/api/auth/register", json=user_data)
        
        login_response = self.client.post("/api/auth/login", json=user_data)
        token = login_response.json()["access_token"]
        
        # Get profile
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get("/api/auth/profile", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "username" in data
        assert "created_at" in data
        assert data["username"] == "testuser"
        assert isinstance(data["id"], int)
        assert isinstance(data["created_at"], str)

    def test_get_profile_invalid_token(self):
        """Test getting profile with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = self.client.get("/api/auth/profile", headers=headers)
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Could not validate credentials"

    def test_get_profile_no_token(self):
        """Test getting profile without token"""
        response = self.client.get("/api/auth/profile")
        
        assert response.status_code == 403
        data = response.json()
        assert data["detail"] == "Not authenticated"

    def test_logout_valid_token(self):
        """Test logout with valid token"""
        # Register and login to get token
        user_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        self.client.post("/api/auth/register", json=user_data)
        
        login_response = self.client.post("/api/auth/login", json=user_data)
        token = login_response.json()["access_token"]
        
        # Logout
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.post("/api/auth/logout", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Successfully logged out"

    def test_logout_and_token_blacklist(self):
        """Test that token is blacklisted after logout"""
        # Register and login to get token
        user_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        self.client.post("/api/auth/register", json=user_data)
        
        login_response = self.client.post("/api/auth/login", json=user_data)
        token = login_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Verify token works before logout
        profile_response = self.client.get("/api/auth/profile", headers=headers)
        assert profile_response.status_code == 200
        
        # Logout
        logout_response = self.client.post("/api/auth/logout", headers=headers)
        assert logout_response.status_code == 200
        
        # Try to use token after logout - should fail
        profile_response_after = self.client.get("/api/auth/profile", headers=headers)
        assert profile_response_after.status_code == 401

    def test_logout_invalid_token(self):
        """Test logout with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = self.client.post("/api/auth/logout", headers=headers)
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Could not validate credentials"

    def test_password_hashing(self):
        """Test that passwords are properly hashed in database"""
        user_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        
        self.client.post("/api/auth/register", json=user_data)
        
        # Check database directly
        conn = sqlite3.connect(self.test_db.name)
        cursor = conn.cursor()
        cursor.execute("SELECT hashed_password FROM users WHERE username = ?", ("testuser",))
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
        hashed_password = result[0]
        # Password should be hashed (not stored in plain text)
        assert hashed_password != "testpassword123"
        # Bcrypt hashes start with $2b$
        assert hashed_password.startswith("$2b$")

    def test_jwt_token_structure(self):
        """Test JWT token structure and expiration"""
        # Register and login
        user_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        self.client.post("/api/auth/register", json=user_data)
        
        login_response = self.client.post("/api/auth/login", json=user_data)
        token = login_response.json()["access_token"]
        
        # JWT tokens have 3 parts separated by dots
        token_parts = token.split('.')
        assert len(token_parts) == 3
        
        # Decode token to check structure (without verification for testing)
        import base64
        import json
        
        # Add padding if needed
        payload = token_parts[1]
        payload += '=' * (4 - len(payload) % 4)
        
        decoded_payload = json.loads(base64.b64decode(payload))
        assert "sub" in decoded_payload  # subject (username)
        assert "exp" in decoded_payload  # expiration
        assert decoded_payload["sub"] == "testuser"

if __name__ == "__main__":
    pytest.main([__file__])
