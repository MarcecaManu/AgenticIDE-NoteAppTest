import sys
import os
from pathlib import Path

# Add backend directory to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from database import Base, get_db
from models import User

# Test database (separate from production)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth_database.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and drop after"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    # Clear token blacklist
    from auth import token_blacklist
    token_blacklist.clear()


class TestAuthentication:
    """Test suite for authentication endpoints"""
    
    def test_register_new_user(self):
        """Test POST /api/auth/register - successfully register a new user"""
        response = client.post(
            "/api/auth/register",
            json={"username": "testuser", "password": "testpass123"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["username"] == "testuser"
        assert "created_at" in data
        assert "password" not in data  # Password should never be in response
        assert "hashed_password" not in data
    
    def test_register_duplicate_username(self):
        """Test registration fails with duplicate username"""
        # Register first user
        client.post(
            "/api/auth/register",
            json={"username": "testuser", "password": "password123"}
        )
        
        # Try to register same username again
        response = client.post(
            "/api/auth/register",
            json={"username": "testuser", "password": "different_password"}
        )
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    def test_register_validation_short_username(self):
        """Test registration validation - username too short"""
        response = client.post(
            "/api/auth/register",
            json={"username": "ab", "password": "password123"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_register_validation_short_password(self):
        """Test registration validation - password too short"""
        response = client.post(
            "/api/auth/register",
            json={"username": "testuser", "password": "12345"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_login_success(self):
        """Test POST /api/auth/login - successfully login with valid credentials"""
        # First register a user
        client.post(
            "/api/auth/register",
            json={"username": "testuser", "password": "testpass123"}
        )
        
        # Now login
        response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "testpass123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
    
    def test_login_wrong_password(self):
        """Test login fails with incorrect password"""
        # Register user
        client.post(
            "/api/auth/register",
            json={"username": "testuser", "password": "correct_password"}
        )
        
        # Try to login with wrong password
        response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "wrong_password"}
        )
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    def test_login_nonexistent_user(self):
        """Test login fails with non-existent username"""
        response = client.post(
            "/api/auth/login",
            json={"username": "nonexistent", "password": "somepassword"}
        )
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    def test_get_profile_authenticated(self):
        """Test GET /api/auth/profile - successfully retrieve profile with valid token"""
        # Register and login
        client.post(
            "/api/auth/register",
            json={"username": "testuser", "password": "testpass123"}
        )
        
        login_response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "testpass123"}
        )
        token = login_response.json()["access_token"]
        
        # Get profile
        response = client.get(
            "/api/auth/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert "id" in data
        assert "created_at" in data
        assert "password" not in data
        assert "hashed_password" not in data
    
    def test_get_profile_no_token(self):
        """Test profile endpoint fails without authentication token"""
        response = client.get("/api/auth/profile")
        
        assert response.status_code == 403  # Forbidden (no credentials)
    
    def test_get_profile_invalid_token(self):
        """Test profile endpoint fails with invalid token"""
        response = client.get(
            "/api/auth/profile",
            headers={"Authorization": "Bearer invalid_token_12345"}
        )
        
        assert response.status_code == 401
    
    def test_logout_success(self):
        """Test POST /api/auth/logout - successfully logout and invalidate token"""
        # Register and login
        client.post(
            "/api/auth/register",
            json={"username": "testuser", "password": "testpass123"}
        )
        
        login_response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "testpass123"}
        )
        token = login_response.json()["access_token"]
        
        # Verify token works before logout
        profile_response = client.get(
            "/api/auth/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert profile_response.status_code == 200
        
        # Logout
        logout_response = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert logout_response.status_code == 200
        assert "logged out" in logout_response.json()["message"].lower()
        
        # Verify token no longer works after logout
        profile_response_after_logout = client.get(
            "/api/auth/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert profile_response_after_logout.status_code == 401
    
    def test_logout_no_token(self):
        """Test logout fails without authentication token"""
        response = client.post("/api/auth/logout")
        
        assert response.status_code == 403
    
    def test_password_hashing(self):
        """Test that passwords are hashed and never stored in plain text"""
        # Register user
        client.post(
            "/api/auth/register",
            json={"username": "testuser", "password": "plain_password"}
        )
        
        # Check database directly
        db = TestingSessionLocal()
        try:
            user = db.query(User).filter(User.username == "testuser").first()
            assert user is not None
            # Password should be hashed, not plain text
            assert user.hashed_password != "plain_password"
            assert len(user.hashed_password) > 50  # Bcrypt hashes are long
            assert user.hashed_password.startswith("$2b$")  # Bcrypt identifier
        finally:
            db.close()
    
    def test_full_authentication_flow(self):
        """Test complete authentication flow: register -> login -> profile -> logout"""
        # Step 1: Register
        register_response = client.post(
            "/api/auth/register",
            json={"username": "flowtest", "password": "password123"}
        )
        assert register_response.status_code == 201
        
        # Step 2: Login
        login_response = client.post(
            "/api/auth/login",
            json={"username": "flowtest", "password": "password123"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Step 3: Get Profile
        profile_response = client.get(
            "/api/auth/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert profile_response.status_code == 200
        assert profile_response.json()["username"] == "flowtest"
        
        # Step 4: Logout
        logout_response = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert logout_response.status_code == 200
        
        # Step 5: Verify can't access profile after logout
        profile_after_logout = client.get(
            "/api/auth/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert profile_after_logout.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

