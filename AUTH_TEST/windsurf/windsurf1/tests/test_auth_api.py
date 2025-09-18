import pytest
import json
import os
import sys
from fastapi.testclient import TestClient

# Add the backend directory to the path so we can import main
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app

# Test client
client = TestClient(app)

# Test data
TEST_USER = {
    "username": "testuser",
    "password": "testpassword123"
}

TEST_USER_2 = {
    "username": "testuser2", 
    "password": "testpassword456"
}

# Fixtures
@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Clean up test data before and after each test"""
    # Clean up before test
    if os.path.exists("users.json"):
        os.remove("users.json")
    
    # Clear the blacklisted tokens set
    from main import blacklisted_tokens
    blacklisted_tokens.clear()
    
    yield
    
    # Clean up after test
    if os.path.exists("users.json"):
        os.remove("users.json")
    
    # Clear the blacklisted tokens set again
    blacklisted_tokens.clear()

@pytest.fixture
def registered_user():
    """Create a registered user for testing"""
    response = client.post("/api/auth/register", json=TEST_USER)
    assert response.status_code == 200
    return TEST_USER

@pytest.fixture
def authenticated_user(registered_user):
    """Create an authenticated user and return the token"""
    response = client.post("/api/auth/login", json=registered_user)
    assert response.status_code == 200
    data = response.json()
    return {
        "token": data["access_token"],
        "user": registered_user
    }

class TestUserRegistration:
    """Test cases for user registration endpoint"""
    
    def test_register_new_user_success(self):
        """Test successful user registration"""
        response = client.post("/api/auth/register", json=TEST_USER)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "User registered successfully"
        
        # Verify user was saved to file
        assert os.path.exists("users.json")
        with open("users.json", 'r') as f:
            users = json.load(f)
        
        assert TEST_USER["username"] in users
        user_data = users[TEST_USER["username"]]
        assert user_data["username"] == TEST_USER["username"]
        assert "hashed_password" in user_data
        assert "created_at" in user_data
        # Ensure password is not stored in plain text
        assert user_data["hashed_password"] != TEST_USER["password"]
    
    def test_register_duplicate_user_fails(self):
        """Test that registering a duplicate user fails"""
        # Register user first time
        response1 = client.post("/api/auth/register", json=TEST_USER)
        assert response1.status_code == 200
        
        # Try to register same user again
        response2 = client.post("/api/auth/register", json=TEST_USER)
        assert response2.status_code == 400
        data = response2.json()
        assert data["detail"] == "Username already registered"
    
    def test_register_invalid_data(self):
        """Test registration with invalid data"""
        # Missing password
        response = client.post("/api/auth/register", json={"username": "testuser"})
        assert response.status_code == 422
        
        # Missing username
        response = client.post("/api/auth/register", json={"password": "testpass"})
        assert response.status_code == 422
        
        # Empty request
        response = client.post("/api/auth/register", json={})
        assert response.status_code == 422

class TestUserLogin:
    """Test cases for user login endpoint"""
    
    def test_login_valid_credentials(self, registered_user):
        """Test successful login with valid credentials"""
        response = client.post("/api/auth/login", json=registered_user)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
    
    def test_login_invalid_username(self):
        """Test login with non-existent username"""
        invalid_user = {"username": "nonexistent", "password": "password123"}
        response = client.post("/api/auth/login", json=invalid_user)
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Incorrect username or password"
    
    def test_login_invalid_password(self, registered_user):
        """Test login with incorrect password"""
        invalid_credentials = {
            "username": registered_user["username"],
            "password": "wrongpassword"
        }
        response = client.post("/api/auth/login", json=invalid_credentials)
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Incorrect username or password"
    
    def test_login_missing_credentials(self):
        """Test login with missing credentials"""
        # Missing password
        response = client.post("/api/auth/login", json={"username": "testuser"})
        assert response.status_code == 422
        
        # Missing username
        response = client.post("/api/auth/login", json={"password": "testpass"})
        assert response.status_code == 422

class TestUserLogout:
    """Test cases for user logout endpoint"""
    
    def test_logout_valid_token(self, authenticated_user):
        """Test successful logout with valid token"""
        headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
        response = client.post("/api/auth/logout", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Successfully logged out"
    
    def test_logout_invalid_token(self):
        """Test logout with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.post("/api/auth/logout", headers=headers)
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Invalid token"
    
    def test_logout_missing_token(self):
        """Test logout without authorization header"""
        response = client.post("/api/auth/logout")
        
        assert response.status_code == 403
        data = response.json()
        assert data["detail"] == "Not authenticated"
    
    def test_logout_blacklisted_token(self, authenticated_user):
        """Test that using a blacklisted token fails"""
        headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
        
        # First logout (blacklists the token)
        response1 = client.post("/api/auth/logout", headers=headers)
        assert response1.status_code == 200
        
        # Try to logout again with same token
        response2 = client.post("/api/auth/logout", headers=headers)
        assert response2.status_code == 401
        data = response2.json()
        assert data["detail"] == "Token already invalidated"

class TestUserProfile:
    """Test cases for user profile endpoint"""
    
    def test_get_profile_valid_token(self, authenticated_user):
        """Test getting profile with valid token"""
        headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
        response = client.get("/api/auth/profile", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == authenticated_user["user"]["username"]
        assert "created_at" in data
        # Verify created_at is a valid ISO format string
        from datetime import datetime
        datetime.fromisoformat(data["created_at"].replace('Z', '+00:00'))
    
    def test_get_profile_invalid_token(self):
        """Test getting profile with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/auth/profile", headers=headers)
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Could not validate credentials"
    
    def test_get_profile_missing_token(self):
        """Test getting profile without authorization header"""
        response = client.get("/api/auth/profile")
        
        assert response.status_code == 403
        data = response.json()
        assert data["detail"] == "Not authenticated"
    
    def test_get_profile_blacklisted_token(self, authenticated_user):
        """Test that blacklisted token cannot access profile"""
        headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
        
        # First logout (blacklists the token)
        logout_response = client.post("/api/auth/logout", headers=headers)
        assert logout_response.status_code == 200
        
        # Try to access profile with blacklisted token
        profile_response = client.get("/api/auth/profile", headers=headers)
        assert profile_response.status_code == 401
        data = profile_response.json()
        assert data["detail"] == "Token has been invalidated"

class TestIntegrationScenarios:
    """Integration test scenarios"""
    
    def test_complete_user_flow(self):
        """Test complete user registration -> login -> profile -> logout flow"""
        # 1. Register user
        register_response = client.post("/api/auth/register", json=TEST_USER)
        assert register_response.status_code == 200
        
        # 2. Login user
        login_response = client.post("/api/auth/login", json=TEST_USER)
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # 3. Get profile
        headers = {"Authorization": f"Bearer {token}"}
        profile_response = client.get("/api/auth/profile", headers=headers)
        assert profile_response.status_code == 200
        profile_data = profile_response.json()
        assert profile_data["username"] == TEST_USER["username"]
        
        # 4. Logout
        logout_response = client.post("/api/auth/logout", headers=headers)
        assert logout_response.status_code == 200
        
        # 5. Verify token is invalidated
        profile_response_after_logout = client.get("/api/auth/profile", headers=headers)
        assert profile_response_after_logout.status_code == 401
    
    def test_multiple_users(self):
        """Test multiple users can register and authenticate independently"""
        # Register two users
        response1 = client.post("/api/auth/register", json=TEST_USER)
        assert response1.status_code == 200
        
        response2 = client.post("/api/auth/register", json=TEST_USER_2)
        assert response2.status_code == 200
        
        # Both users can login
        login1 = client.post("/api/auth/login", json=TEST_USER)
        assert login1.status_code == 200
        token1 = login1.json()["access_token"]
        
        login2 = client.post("/api/auth/login", json=TEST_USER_2)
        assert login2.status_code == 200
        token2 = login2.json()["access_token"]
        
        # Both users can access their profiles
        headers1 = {"Authorization": f"Bearer {token1}"}
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        profile1 = client.get("/api/auth/profile", headers=headers1)
        assert profile1.status_code == 200
        assert profile1.json()["username"] == TEST_USER["username"]
        
        profile2 = client.get("/api/auth/profile", headers=headers2)
        assert profile2.status_code == 200
        assert profile2.json()["username"] == TEST_USER_2["username"]
        
        # User 1 logout doesn't affect user 2
        logout1 = client.post("/api/auth/logout", headers=headers1)
        assert logout1.status_code == 200
        
        profile2_after_user1_logout = client.get("/api/auth/profile", headers=headers2)
        assert profile2_after_user1_logout.status_code == 200

class TestHealthCheck:
    """Test health check endpoint"""
    
    def test_root_endpoint(self):
        """Test that root endpoint returns health check"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Authentication API is running"
