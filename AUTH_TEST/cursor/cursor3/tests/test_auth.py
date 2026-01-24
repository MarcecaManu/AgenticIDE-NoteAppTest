import pytest
import sys
import os
import time
from fastapi.testclient import TestClient

# Add backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app

# Create a test client
client = TestClient(app)

# Test database path (unique per test session)
TEST_DB_PATH = f"test_users_{os.getpid()}.db"


@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown():
    """Setup and teardown for each test"""
    # Override database path for testing
    import main
    original_db_path = main.DATABASE_PATH
    main.DATABASE_PATH = TEST_DB_PATH
    
    # Remove existing test database if it exists
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except PermissionError:
            time.sleep(0.1)
            os.remove(TEST_DB_PATH)
    
    # Initialize test database
    main.init_db()
    
    yield
    
    # Restore original database path
    main.DATABASE_PATH = original_db_path
    
    # Cleanup: remove test database with retry logic for Windows
    max_attempts = 5
    for attempt in range(max_attempts):
        try:
            if os.path.exists(TEST_DB_PATH):
                os.remove(TEST_DB_PATH)
            break
        except PermissionError:
            if attempt < max_attempts - 1:
                time.sleep(0.2)
            else:
                # If we still can't delete, just pass (file will be cleaned up next run)
                pass


def test_register_new_user():
    """Test user registration with valid credentials"""
    # Arrange
    user_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    # Act
    response = client.post("/api/auth/register", json=user_data)
    
    # Assert
    assert response.status_code == 201
    assert response.json() == {"message": "User registered successfully"}


def test_register_duplicate_username():
    """Test registration with already existing username"""
    # Arrange
    user_data = {
        "username": "duplicateuser",
        "password": "testpass123"
    }
    
    # Register user first time
    client.post("/api/auth/register", json=user_data)
    
    # Act - Try to register again
    response = client.post("/api/auth/register", json=user_data)
    
    # Assert
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_register_invalid_username():
    """Test registration with username that's too short"""
    # Arrange
    user_data = {
        "username": "ab",  # Too short (min 3 chars)
        "password": "testpass123"
    }
    
    # Act
    response = client.post("/api/auth/register", json=user_data)
    
    # Assert
    assert response.status_code == 422  # Validation error


def test_register_invalid_password():
    """Test registration with password that's too short"""
    # Arrange
    user_data = {
        "username": "testuser",
        "password": "12345"  # Too short (min 6 chars)
    }
    
    # Act
    response = client.post("/api/auth/register", json=user_data)
    
    # Assert
    assert response.status_code == 422  # Validation error


def test_login_success():
    """Test successful login with valid credentials"""
    # Arrange - Register a user first
    user_data = {
        "username": "loginuser",
        "password": "securepass123"
    }
    client.post("/api/auth/register", json=user_data)
    
    # Act - Login with same credentials
    response = client.post("/api/auth/login", json=user_data)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0


def test_login_wrong_password():
    """Test login with incorrect password"""
    # Arrange - Register a user
    client.post("/api/auth/register", json={
        "username": "loginuser2",
        "password": "correctpass"
    })
    
    # Act - Try to login with wrong password
    response = client.post("/api/auth/login", json={
        "username": "loginuser2",
        "password": "wrongpass"
    })
    
    # Assert
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


def test_login_nonexistent_user():
    """Test login with non-existent username"""
    # Act
    response = client.post("/api/auth/login", json={
        "username": "nonexistent",
        "password": "somepass"
    })
    
    # Assert
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


def test_get_profile_authenticated():
    """Test retrieving user profile with valid authentication token"""
    # Arrange - Register and login
    user_data = {
        "username": "profileuser",
        "password": "testpass123"
    }
    client.post("/api/auth/register", json=user_data)
    login_response = client.post("/api/auth/login", json=user_data)
    token = login_response.json()["access_token"]
    
    # Act - Get profile with token
    response = client.get(
        "/api/auth/profile",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "profileuser"
    assert "created_at" in data


def test_get_profile_no_token():
    """Test accessing profile without authentication token"""
    # Act
    response = client.get("/api/auth/profile")
    
    # Assert
    assert response.status_code == 403  # Forbidden - no credentials


def test_get_profile_invalid_token():
    """Test accessing profile with invalid token"""
    # Act
    response = client.get(
        "/api/auth/profile",
        headers={"Authorization": "Bearer invalidtoken123"}
    )
    
    # Assert
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


def test_logout_success():
    """Test successful logout with valid token"""
    # Arrange - Register and login
    user_data = {
        "username": "logoutuser",
        "password": "testpass123"
    }
    client.post("/api/auth/register", json=user_data)
    login_response = client.post("/api/auth/login", json=user_data)
    token = login_response.json()["access_token"]
    
    # Act - Logout
    response = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": "Logged out successfully"}


def test_logout_token_blacklisted():
    """Test that token is blacklisted after logout"""
    # Arrange - Register, login, and logout
    user_data = {
        "username": "blacklistuser",
        "password": "testpass123"
    }
    client.post("/api/auth/register", json=user_data)
    login_response = client.post("/api/auth/login", json=user_data)
    token = login_response.json()["access_token"]
    
    # Logout
    client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Act - Try to access profile with blacklisted token
    response = client.get(
        "/api/auth/profile",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Assert
    assert response.status_code == 401
    assert "revoked" in response.json()["detail"].lower()


def test_logout_no_token():
    """Test logout without authentication token"""
    # Act
    response = client.post("/api/auth/logout")
    
    # Assert
    assert response.status_code == 403  # Forbidden - no credentials


def test_logout_invalid_token():
    """Test logout with invalid token"""
    # Act
    response = client.post(
        "/api/auth/logout",
        headers={"Authorization": "Bearer invalidtoken"}
    )
    
    # Assert
    assert response.status_code == 401


def test_password_is_hashed():
    """Test that passwords are stored hashed, not in plain text"""
    # Arrange
    user_data = {
        "username": "hashtest",
        "password": "myplainpass"
    }
    client.post("/api/auth/register", json=user_data)
    
    # Act - Check database directly
    import sqlite3
    conn = sqlite3.connect(TEST_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE username = ?", ("hashtest",))
    stored_hash = cursor.fetchone()[0]
    conn.close()
    
    # Assert - Password should not match the plain text
    assert stored_hash != "myplainpass"
    assert len(stored_hash) > 50  # Bcrypt hashes are long


def test_end_to_end_flow():
    """Test complete authentication flow: register -> login -> profile -> logout"""
    # 1. Register
    user_data = {
        "username": "e2euser",
        "password": "e2epass123"
    }
    register_response = client.post("/api/auth/register", json=user_data)
    assert register_response.status_code == 201
    
    # 2. Login
    login_response = client.post("/api/auth/login", json=user_data)
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # 3. Get Profile
    profile_response = client.get(
        "/api/auth/profile",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert profile_response.status_code == 200
    assert profile_response.json()["username"] == "e2euser"
    
    # 4. Logout
    logout_response = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert logout_response.status_code == 200
    
    # 5. Verify token is invalid after logout
    profile_after_logout = client.get(
        "/api/auth/profile",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert profile_after_logout.status_code == 401

