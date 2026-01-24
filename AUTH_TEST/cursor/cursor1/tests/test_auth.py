import pytest
from fastapi.testclient import TestClient
import sys
import os
import sqlite3

# Add parent directory to path to import backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.main import app, DB_PATH, init_db

# Test client
client = TestClient(app)

# Test database path
TEST_DB_PATH = "backend/test_users.db"

@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch):
    """Setup test database before each test and cleanup after"""
    # Use test database
    monkeypatch.setattr("backend.main.DB_PATH", TEST_DB_PATH)
    
    # Remove test database if exists
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    
    # Initialize test database
    init_db()
    
    yield
    
    # Cleanup: remove test database after test
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

class TestRegistration:
    """Test user registration endpoint"""
    
    def test_register_valid_user(self):
        """Test registering a new user with valid credentials"""
        response = client.post(
            "/api/auth/register",
            json={"username": "testuser", "password": "password123"}
        )
        assert response.status_code == 201
        assert response.json()["message"] == "User registered successfully"
    
    def test_register_duplicate_username(self):
        """Test registering with an already existing username"""
        # Register first user
        client.post(
            "/api/auth/register",
            json={"username": "testuser", "password": "password123"}
        )
        
        # Try to register with same username
        response = client.post(
            "/api/auth/register",
            json={"username": "testuser", "password": "different_password"}
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()
    
    def test_register_short_username(self):
        """Test registering with username shorter than 3 characters"""
        response = client.post(
            "/api/auth/register",
            json={"username": "ab", "password": "password123"}
        )
        assert response.status_code == 400
        assert "username" in response.json()["detail"].lower()
    
    def test_register_short_password(self):
        """Test registering with password shorter than 6 characters"""
        response = client.post(
            "/api/auth/register",
            json={"username": "testuser", "password": "12345"}
        )
        assert response.status_code == 400
        assert "password" in response.json()["detail"].lower()

class TestLogin:
    """Test user login endpoint"""
    
    def test_login_valid_credentials(self):
        """Test logging in with valid credentials"""
        # Register a user first
        client.post(
            "/api/auth/register",
            json={"username": "testuser", "password": "password123"}
        )
        
        # Login
        response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "password123"}
        )
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"
    
    def test_login_invalid_username(self):
        """Test logging in with non-existent username"""
        response = client.post(
            "/api/auth/login",
            json={"username": "nonexistent", "password": "password123"}
        )
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    def test_login_invalid_password(self):
        """Test logging in with incorrect password"""
        # Register a user first
        client.post(
            "/api/auth/register",
            json={"username": "testuser", "password": "password123"}
        )
        
        # Try login with wrong password
        response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "wrongpassword"}
        )
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    def test_login_returns_valid_token(self):
        """Test that login returns a token that can be used for authentication"""
        # Register and login
        client.post(
            "/api/auth/register",
            json={"username": "testuser", "password": "password123"}
        )
        login_response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "password123"}
        )
        token = login_response.json()["access_token"]
        
        # Use token to access protected endpoint
        profile_response = client.get(
            "/api/auth/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert profile_response.status_code == 200
        assert profile_response.json()["username"] == "testuser"

class TestProfile:
    """Test user profile endpoint"""
    
    def test_get_profile_with_valid_token(self):
        """Test getting profile with valid authentication token"""
        # Register and login
        client.post(
            "/api/auth/register",
            json={"username": "testuser", "password": "password123"}
        )
        login_response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "password123"}
        )
        token = login_response.json()["access_token"]
        
        # Get profile
        response = client.get(
            "/api/auth/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["username"] == "testuser"
        assert "created_at" in response.json()
    
    def test_get_profile_without_token(self):
        """Test getting profile without authentication token"""
        response = client.get("/api/auth/profile")
        assert response.status_code == 403  # FastAPI returns 403 for missing credentials
    
    def test_get_profile_with_invalid_token(self):
        """Test getting profile with invalid token"""
        response = client.get(
            "/api/auth/profile",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        assert response.status_code == 401
    
    def test_get_profile_with_blacklisted_token(self):
        """Test that profile cannot be accessed with a blacklisted token"""
        # Register, login, and logout
        client.post(
            "/api/auth/register",
            json={"username": "testuser", "password": "password123"}
        )
        login_response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "password123"}
        )
        token = login_response.json()["access_token"]
        
        # Logout (blacklist token)
        client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Try to access profile with blacklisted token
        response = client.get(
            "/api/auth/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 401
        assert "revoked" in response.json()["detail"].lower()

class TestLogout:
    """Test user logout endpoint"""
    
    def test_logout_with_valid_token(self):
        """Test logging out with valid token"""
        # Register and login
        client.post(
            "/api/auth/register",
            json={"username": "testuser", "password": "password123"}
        )
        login_response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "password123"}
        )
        token = login_response.json()["access_token"]
        
        # Logout
        response = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert "logged out" in response.json()["message"].lower()
    
    def test_logout_without_token(self):
        """Test logging out without token"""
        response = client.post("/api/auth/logout")
        assert response.status_code == 403
    
    def test_logout_invalidates_token(self):
        """Test that logout properly invalidates the token"""
        # Register and login
        client.post(
            "/api/auth/register",
            json={"username": "testuser", "password": "password123"}
        )
        login_response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "password123"}
        )
        token = login_response.json()["access_token"]
        
        # Verify token works before logout
        profile_response = client.get(
            "/api/auth/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert profile_response.status_code == 200
        
        # Logout
        client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Verify token no longer works
        profile_response = client.get(
            "/api/auth/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert profile_response.status_code == 401

class TestPasswordSecurity:
    """Test password security features"""
    
    def test_password_not_stored_in_plain_text(self):
        """Test that passwords are hashed in database"""
        # Register a user
        client.post(
            "/api/auth/register",
            json={"username": "testuser", "password": "password123"}
        )
        
        # Check database directly
        conn = sqlite3.connect(TEST_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE username = ?", ("testuser",))
        password_hash = cursor.fetchone()[0]
        conn.close()
        
        # Verify password is hashed (not plain text)
        assert password_hash != "password123"
        assert len(password_hash) > 20  # Bcrypt hashes are long
    
    def test_same_password_different_hashes(self):
        """Test that same password produces different hashes (salt)"""
        # Register two users with same password
        client.post(
            "/api/auth/register",
            json={"username": "user1", "password": "samepassword"}
        )
        client.post(
            "/api/auth/register",
            json={"username": "user2", "password": "samepassword"}
        )
        
        # Check database directly
        conn = sqlite3.connect(TEST_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE username IN (?, ?)", ("user1", "user2"))
        hashes = cursor.fetchall()
        conn.close()
        
        # Verify hashes are different (due to different salts)
        assert hashes[0][0] != hashes[1][0]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

