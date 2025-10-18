import pytest
import json
import os
from fastapi.testclient import TestClient
from backend.main import app, USERS_FILE

# Create test client
client = TestClient(app)

# Test fixtures
@pytest.fixture(autouse=True)
def cleanup_users_file():
    """Clean up users file before and after each test."""
    # Remove users file before test
    if os.path.exists(USERS_FILE):
        os.remove(USERS_FILE)
    
    yield
    
    # Remove users file after test
    if os.path.exists(USERS_FILE):
        os.remove(USERS_FILE)

@pytest.fixture
def test_user():
    """Test user data."""
    return {
        "username": "testuser",
        "password": "testpass123"
    }

@pytest.fixture
def registered_user(test_user):
    """Register a test user and return the user data."""
    response = client.post("/api/auth/register", json=test_user)
    assert response.status_code == 200
    return test_user

@pytest.fixture
def logged_in_user(registered_user):
    """Register and login a test user, return user data and token."""
    response = client.post("/api/auth/login", json=registered_user)
    assert response.status_code == 200
    token_data = response.json()
    return {
        "user": registered_user,
        "token": token_data["access_token"],
        "headers": {"Authorization": f"Bearer {token_data['access_token']}"}
    }

class TestUserRegistration:
    """Test user registration functionality."""
    
    def test_register_new_user_success(self, test_user):
        """Test successful user registration."""
        response = client.post("/api/auth/register", json=test_user)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "User registered successfully"
        assert data["username"] == test_user["username"]
        
        # Verify user was saved to file
        assert os.path.exists(USERS_FILE)
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
            assert test_user["username"] in users
            assert "hashed_password" in users[test_user["username"]]
            assert "created_at" in users[test_user["username"]]
    
    def test_register_duplicate_user(self, registered_user):
        """Test registration with existing username."""
        response = client.post("/api/auth/register", json=registered_user)
        
        assert response.status_code == 400
        data = response.json()
        assert "already registered" in data["detail"].lower()
    
    def test_register_missing_username(self):
        """Test registration with missing username."""
        response = client.post("/api/auth/register", json={"password": "testpass123"})
        
        assert response.status_code == 422  # Validation error
    
    def test_register_missing_password(self):
        """Test registration with missing password."""
        response = client.post("/api/auth/register", json={"username": "testuser"})
        
        assert response.status_code == 422  # Validation error
    
    def test_register_empty_fields(self):
        """Test registration with empty fields."""
        response = client.post("/api/auth/register", json={"username": "", "password": ""})
        
        assert response.status_code == 400
        data = response.json()
        assert "required" in data["detail"].lower()
    
    def test_register_short_password(self):
        """Test registration with password too short."""
        response = client.post("/api/auth/register", json={"username": "testuser", "password": "123"})
        
        assert response.status_code == 400
        data = response.json()
        assert "6 characters" in data["detail"]

class TestUserLogin:
    """Test user login functionality."""
    
    def test_login_valid_credentials(self, registered_user):
        """Test successful login with valid credentials."""
        response = client.post("/api/auth/login", json=registered_user)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
    
    def test_login_invalid_username(self, registered_user):
        """Test login with invalid username."""
        response = client.post("/api/auth/login", json={
            "username": "nonexistent",
            "password": registered_user["password"]
        })
        
        assert response.status_code == 401
        data = response.json()
        assert "incorrect username or password" in data["detail"].lower()
    
    def test_login_invalid_password(self, registered_user):
        """Test login with invalid password."""
        response = client.post("/api/auth/login", json={
            "username": registered_user["username"],
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        data = response.json()
        assert "incorrect username or password" in data["detail"].lower()
    
    def test_login_missing_credentials(self):
        """Test login with missing credentials."""
        response = client.post("/api/auth/login", json={})
        
        assert response.status_code == 422  # Validation error
    
    def test_login_unregistered_user(self):
        """Test login with unregistered user."""
        response = client.post("/api/auth/login", json={
            "username": "unregistered",
            "password": "password123"
        })
        
        assert response.status_code == 401

class TestUserLogout:
    """Test user logout functionality."""
    
    def test_logout_with_valid_token(self, logged_in_user):
        """Test successful logout with valid token."""
        response = client.post("/api/auth/logout", headers=logged_in_user["headers"])
        
        assert response.status_code == 200
        data = response.json()
        assert "successfully logged out" in data["message"].lower()
    
    def test_logout_without_token(self):
        """Test logout without authentication token."""
        response = client.post("/api/auth/logout")
        
        assert response.status_code == 403  # No credentials provided
    
    def test_logout_with_invalid_token(self):
        """Test logout with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.post("/api/auth/logout", headers=headers)
        
        assert response.status_code == 401
        data = response.json()
        assert "invalid token" in data["detail"].lower()
    
    def test_token_invalidation_after_logout(self, logged_in_user):
        """Test that token is invalidated after logout."""
        # First logout
        response = client.post("/api/auth/logout", headers=logged_in_user["headers"])
        assert response.status_code == 200
        
        # Try to access profile with the same token
        response = client.get("/api/auth/profile", headers=logged_in_user["headers"])
        assert response.status_code == 401
        data = response.json()
        assert "invalidated" in data["detail"].lower()

class TestUserProfile:
    """Test user profile functionality."""
    
    def test_get_profile_with_valid_token(self, logged_in_user):
        """Test getting profile with valid token."""
        response = client.get("/api/auth/profile", headers=logged_in_user["headers"])
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == logged_in_user["user"]["username"]
        assert "created_at" in data
        
        # Verify created_at is a valid ISO datetime string
        from datetime import datetime
        datetime.fromisoformat(data["created_at"].replace('Z', '+00:00'))
    
    def test_get_profile_without_token(self):
        """Test getting profile without authentication token."""
        response = client.get("/api/auth/profile")
        
        assert response.status_code == 403  # No credentials provided
    
    def test_get_profile_with_invalid_token(self):
        """Test getting profile with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/auth/profile", headers=headers)
        
        assert response.status_code == 401
        data = response.json()
        assert "could not validate credentials" in data["detail"].lower()
    
    def test_get_profile_with_malformed_token(self):
        """Test getting profile with malformed token."""
        headers = {"Authorization": "InvalidFormat"}
        response = client.get("/api/auth/profile", headers=headers)
        
        assert response.status_code == 403  # Invalid authorization header format
    
    def test_get_profile_after_logout(self, logged_in_user):
        """Test getting profile after logout."""
        # First logout
        client.post("/api/auth/logout", headers=logged_in_user["headers"])
        
        # Try to get profile
        response = client.get("/api/auth/profile", headers=logged_in_user["headers"])
        
        assert response.status_code == 401
        data = response.json()
        assert "invalidated" in data["detail"].lower()

class TestIntegrationFlow:
    """Test complete authentication flow."""
    
    def test_complete_auth_flow(self, test_user):
        """Test complete registration -> login -> profile -> logout flow."""
        # 1. Register user
        response = client.post("/api/auth/register", json=test_user)
        assert response.status_code == 200
        
        # 2. Login user
        response = client.post("/api/auth/login", json=test_user)
        assert response.status_code == 200
        token_data = response.json()
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        
        # 3. Get profile
        response = client.get("/api/auth/profile", headers=headers)
        assert response.status_code == 200
        profile_data = response.json()
        assert profile_data["username"] == test_user["username"]
        
        # 4. Logout
        response = client.post("/api/auth/logout", headers=headers)
        assert response.status_code == 200
        
        # 5. Verify token is invalidated
        response = client.get("/api/auth/profile", headers=headers)
        assert response.status_code == 401

class TestHealthCheck:
    """Test health check endpoint."""
    
    def test_root_endpoint(self):
        """Test the root health check endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "running" in data["message"].lower()

# Run tests with: pytest tests/test_auth_api.py -v