import pytest
import httpx
import os
import sys
from pathlib import Path

# Add backend directory to Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from fastapi.testclient import TestClient
from main import app
from database import Database
from auth import get_password_hash

# Test database path
TEST_DB_PATH = str(Path(__file__).parent / "test_auth.db")

@pytest.fixture(scope="function")
def client():
    """Create a test client with a fresh database for each test"""
    import uuid
    import tempfile
    
    # Create a unique test database for each test
    test_db_name = f"test_auth_{uuid.uuid4().hex[:8]}.db"
    test_db_path = os.path.join(tempfile.gettempdir(), test_db_name)
    
    # Create test database
    test_db = Database(test_db_path)
    
    # Override the database in auth module
    import auth
    original_db = auth.db
    auth.db = test_db
    
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        # Restore original database
        auth.db = original_db
        
        # Cleanup test database
        try:
            if os.path.exists(test_db_path):
                os.remove(test_db_path)
        except PermissionError:
            pass  # File might be in use, that's okay

@pytest.fixture
def test_user():
    """Test user data"""
    return {
        "username": "testuser",
        "password": "testpass123"
    }

class TestUserRegistration:
    """Test user registration endpoint"""
    
    def test_register_valid_user(self, client, test_user):
        """Test successful user registration"""
        response = client.post("/api/auth/register", json=test_user)
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "User registered successfully"
    
    def test_register_duplicate_username(self, client, test_user):
        """Test registration with duplicate username"""
        # Register user first time
        client.post("/api/auth/register", json=test_user)
        
        # Try to register same username again
        response = client.post("/api/auth/register", json=test_user)
        assert response.status_code == 400
        data = response.json()
        assert "already exists" in data["detail"]
    
    def test_register_short_username(self, client):
        """Test registration with username too short"""
        user_data = {"username": "ab", "password": "testpass123"}
        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code == 400
        data = response.json()
        assert "at least 3 characters" in data["detail"]
    
    def test_register_short_password(self, client):
        """Test registration with password too short"""
        user_data = {"username": "testuser", "password": "123"}
        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code == 400
        data = response.json()
        assert "at least 6 characters" in data["detail"]
    
    def test_register_empty_fields(self, client):
        """Test registration with empty fields"""
        user_data = {"username": "", "password": ""}
        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code == 400

class TestUserLogin:
    """Test user login endpoint"""
    
    def test_login_valid_credentials(self, client, test_user):
        """Test successful login with valid credentials"""
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
        response = client.post("/api/auth/login", json=test_user)
        assert response.status_code == 401
        data = response.json()
        assert "Incorrect username or password" in data["detail"]
    
    def test_login_invalid_password(self, client, test_user):
        """Test login with wrong password"""
        # Register user first
        client.post("/api/auth/register", json=test_user)
        
        # Login with wrong password
        wrong_credentials = {"username": test_user["username"], "password": "wrongpass"}
        response = client.post("/api/auth/login", json=wrong_credentials)
        assert response.status_code == 401
        data = response.json()
        assert "Incorrect username or password" in data["detail"]
    
    def test_login_empty_credentials(self, client):
        """Test login with empty credentials"""
        response = client.post("/api/auth/login", json={"username": "", "password": ""})
        assert response.status_code == 401

class TestUserProfile:
    """Test user profile endpoint"""
    
    def test_get_profile_valid_token(self, client, test_user):
        """Test getting profile with valid token"""
        # Register and login user
        client.post("/api/auth/register", json=test_user)
        login_response = client.post("/api/auth/login", json=test_user)
        token = login_response.json()["access_token"]
        
        # Get profile
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/auth/profile", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user["username"]
        assert "id" in data
        assert "created_at" in data
        assert "password" not in data  # Password should not be in response
    
    def test_get_profile_invalid_token(self, client):
        """Test getting profile with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/auth/profile", headers=headers)
        assert response.status_code == 401
        data = response.json()
        assert "Invalid or expired token" in data["detail"]
    
    def test_get_profile_no_token(self, client):
        """Test getting profile without token"""
        response = client.get("/api/auth/profile")
        assert response.status_code == 403  # FastAPI returns 403 for missing auth
    
    def test_get_profile_malformed_header(self, client):
        """Test getting profile with malformed authorization header"""
        headers = {"Authorization": "InvalidFormat token"}
        response = client.get("/api/auth/profile", headers=headers)
        assert response.status_code == 403

class TestUserLogout:
    """Test user logout endpoint"""
    
    def test_logout_valid_token(self, client, test_user):
        """Test successful logout with valid token"""
        # Register and login user
        client.post("/api/auth/register", json=test_user)
        login_response = client.post("/api/auth/login", json=test_user)
        token = login_response.json()["access_token"]
        
        # Logout
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/api/auth/logout", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Successfully logged out"
        
        # Verify token is blacklisted by trying to access profile
        profile_response = client.get("/api/auth/profile", headers=headers)
        assert profile_response.status_code == 401
    
    def test_logout_invalid_token(self, client):
        """Test logout with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.post("/api/auth/logout", headers=headers)
        assert response.status_code == 200  # Logout should succeed even with invalid token
    
    def test_logout_no_token(self, client):
        """Test logout without token"""
        response = client.post("/api/auth/logout")
        assert response.status_code == 403  # FastAPI returns 403 for missing auth
    
    def test_logout_twice_same_token(self, client, test_user):
        """Test logging out twice with the same token"""
        # Register and login user
        client.post("/api/auth/register", json=test_user)
        login_response = client.post("/api/auth/login", json=test_user)
        token = login_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # First logout
        response1 = client.post("/api/auth/logout", headers=headers)
        assert response1.status_code == 200
        
        # Second logout with same token
        response2 = client.post("/api/auth/logout", headers=headers)
        assert response2.status_code == 200  # Should still succeed

class TestIntegrationFlow:
    """Test complete authentication flow"""
    
    def test_complete_auth_flow(self, client, test_user):
        """Test complete registration -> login -> profile -> logout flow"""
        # 1. Register
        register_response = client.post("/api/auth/register", json=test_user)
        assert register_response.status_code == 200
        
        # 2. Login
        login_response = client.post("/api/auth/login", json=test_user)
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # 3. Get Profile
        headers = {"Authorization": f"Bearer {token}"}
        profile_response = client.get("/api/auth/profile", headers=headers)
        assert profile_response.status_code == 200
        profile_data = profile_response.json()
        assert profile_data["username"] == test_user["username"]
        
        # 4. Logout
        logout_response = client.post("/api/auth/logout", headers=headers)
        assert logout_response.status_code == 200
        
        # 5. Verify token is invalidated
        profile_after_logout = client.get("/api/auth/profile", headers=headers)
        assert profile_after_logout.status_code == 401
    
    def test_multiple_users(self, client):
        """Test multiple users can register and login independently"""
        user1 = {"username": "user1", "password": "password123"}
        user2 = {"username": "user2", "password": "password456"}
        
        # Register both users
        client.post("/api/auth/register", json=user1)
        client.post("/api/auth/register", json=user2)
        
        # Login both users
        login1 = client.post("/api/auth/login", json=user1)
        login2 = client.post("/api/auth/login", json=user2)
        
        assert login1.status_code == 200
        assert login2.status_code == 200
        
        token1 = login1.json()["access_token"]
        token2 = login2.json()["access_token"]
        
        # Verify different tokens
        assert token1 != token2
        
        # Verify both can access their profiles
        headers1 = {"Authorization": f"Bearer {token1}"}
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        profile1 = client.get("/api/auth/profile", headers=headers1)
        profile2 = client.get("/api/auth/profile", headers=headers2)
        
        assert profile1.status_code == 200
        assert profile2.status_code == 200
        assert profile1.json()["username"] == "user1"
        assert profile2.json()["username"] == "user2"
