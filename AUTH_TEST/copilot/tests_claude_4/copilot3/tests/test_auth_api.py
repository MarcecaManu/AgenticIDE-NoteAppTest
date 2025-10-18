import pytest
import os
import sys
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app
from database import get_db, Base

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def client():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create test client
    with TestClient(app) as test_client:
        yield test_client
    
    # Drop tables after each test
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def test_user():
    return {
        "username": "testuser",
        "password": "testpass123"
    }

@pytest.fixture(scope="function")
def authenticated_client(client, test_user):
    # Register user
    client.post("/api/auth/register", json=test_user)
    
    # Login and get token
    response = client.post("/api/auth/login", json=test_user)
    token = response.json()["access_token"]
    
    # Create authenticated client
    class AuthenticatedClient:
        def __init__(self, client, token):
            self.client = client
            self.token = token
            self.headers = {"Authorization": f"Bearer {token}"}
        
        def get(self, url):
            return self.client.get(url, headers=self.headers)
        
        def post(self, url, **kwargs):
            return self.client.post(url, headers=self.headers, **kwargs)
    
    return AuthenticatedClient(client, token)


class TestUserRegistration:
    """Test user registration functionality."""
    
    def test_register_new_user_success(self, client, test_user):
        """Test successful user registration."""
        response = client.post("/api/auth/register", json=test_user)
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == test_user["username"]
        assert "id" in data
        assert "created_at" in data
        assert "password" not in data  # Ensure password is not returned
    
    def test_register_duplicate_username_fails(self, client, test_user):
        """Test registration fails with duplicate username."""
        # Register user once
        client.post("/api/auth/register", json=test_user)
        
        # Try to register again with same username
        response = client.post("/api/auth/register", json=test_user)
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]
    
    def test_register_short_username_fails(self, client):
        """Test registration fails with username too short."""
        response = client.post("/api/auth/register", json={
            "username": "ab",  # Too short
            "password": "validpass123"
        })
        
        assert response.status_code == 400
        assert "at least 3 characters" in response.json()["detail"]
    
    def test_register_short_password_fails(self, client):
        """Test registration fails with password too short."""
        response = client.post("/api/auth/register", json={
            "username": "validuser",
            "password": "12345"  # Too short
        })
        
        assert response.status_code == 400
        assert "at least 6 characters" in response.json()["detail"]
    
    def test_register_empty_fields_fails(self, client):
        """Test registration fails with empty fields."""
        response = client.post("/api/auth/register", json={
            "username": "",
            "password": ""
        })
        
        assert response.status_code == 400


class TestUserLogin:
    """Test user login functionality."""
    
    def test_login_valid_credentials_success(self, client, test_user):
        """Test successful login with valid credentials."""
        # Register user first
        client.post("/api/auth/register", json=test_user)
        
        # Login
        response = client.post("/api/auth/login", json=test_user)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
    
    def test_login_invalid_username_fails(self, client, test_user):
        """Test login fails with invalid username."""
        # Register user first
        client.post("/api/auth/register", json=test_user)
        
        # Try login with wrong username
        response = client.post("/api/auth/login", json={
            "username": "wronguser",
            "password": test_user["password"]
        })
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    def test_login_invalid_password_fails(self, client, test_user):
        """Test login fails with invalid password."""
        # Register user first
        client.post("/api/auth/register", json=test_user)
        
        # Try login with wrong password
        response = client.post("/api/auth/login", json={
            "username": test_user["username"],
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    def test_login_nonexistent_user_fails(self, client):
        """Test login fails for non-existent user."""
        response = client.post("/api/auth/login", json={
            "username": "nonexistentuser",
            "password": "somepassword"
        })
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]


class TestUserProfile:
    """Test user profile functionality."""
    
    def test_get_profile_with_valid_token_success(self, authenticated_client, test_user):
        """Test successful profile retrieval with valid token."""
        response = authenticated_client.get("/api/auth/profile")
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user["username"]
        assert "id" in data
        assert "created_at" in data
        assert "password" not in data  # Ensure password is not returned
    
    def test_get_profile_without_token_fails(self, client):
        """Test profile retrieval fails without token."""
        response = client.get("/api/auth/profile")
        
        assert response.status_code == 403  # FastAPI returns 403 for missing auth header
    
    def test_get_profile_with_invalid_token_fails(self, client):
        """Test profile retrieval fails with invalid token."""
        response = client.get("/api/auth/profile", headers={
            "Authorization": "Bearer invalid_token_here"
        })
        
        assert response.status_code == 401
        assert "Invalid authentication credentials" in response.json()["detail"]


class TestUserLogout:
    """Test user logout functionality."""
    
    def test_logout_with_valid_token_success(self, authenticated_client):
        """Test successful logout with valid token."""
        response = authenticated_client.post("/api/auth/logout")
        
        assert response.status_code == 200
        assert "Successfully logged out" in response.json()["message"]
    
    def test_logout_without_token_fails(self, client):
        """Test logout fails without token."""
        response = client.post("/api/auth/logout")
        
        assert response.status_code == 403  # FastAPI returns 403 for missing auth header
    
    def test_access_after_logout_fails(self, authenticated_client):
        """Test that accessing protected resources fails after logout."""
        # Logout
        logout_response = authenticated_client.post("/api/auth/logout")
        assert logout_response.status_code == 200
        
        # Try to access profile after logout
        profile_response = authenticated_client.get("/api/auth/profile")
        assert profile_response.status_code == 401
        assert "invalidated" in profile_response.json()["detail"]


class TestAuthenticationFlow:
    """Test complete authentication flow."""
    
    def test_complete_auth_flow(self, client):
        """Test complete registration -> login -> profile -> logout flow."""
        user_data = {
            "username": "flowuser",
            "password": "flowpass123"
        }
        
        # 1. Register
        register_response = client.post("/api/auth/register", json=user_data)
        assert register_response.status_code == 201
        user_id = register_response.json()["id"]
        
        # 2. Login
        login_response = client.post("/api/auth/login", json=user_data)
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Get profile
        profile_response = client.get("/api/auth/profile", headers=headers)
        assert profile_response.status_code == 200
        profile_data = profile_response.json()
        assert profile_data["username"] == user_data["username"]
        assert profile_data["id"] == user_id
        
        # 4. Logout
        logout_response = client.post("/api/auth/logout", headers=headers)
        assert logout_response.status_code == 200
        
        # 5. Verify access is denied after logout
        profile_after_logout = client.get("/api/auth/profile", headers=headers)
        assert profile_after_logout.status_code == 401


class TestHealthCheck:
    """Test health check endpoint."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"