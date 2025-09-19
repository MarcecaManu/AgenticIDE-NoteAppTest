import pytest
from fastapi.testclient import TestClient
from conftest import test_client, sample_user, authenticated_client

class TestUserRegistration:
    """Test user registration functionality."""
    
    def test_successful_registration(self, test_client, sample_user):
        """Test successful user registration."""
        response = test_client.post("/api/auth/register", json=sample_user)
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["username"] == sample_user["username"]
        assert "created_at" in data
        assert "password" not in data  # Password should not be returned
    
    def test_duplicate_username_registration(self, test_client, sample_user):
        """Test registration with duplicate username."""
        # Register user first time
        test_client.post("/api/auth/register", json=sample_user)
        
        # Try to register with same username
        response = test_client.post("/api/auth/register", json=sample_user)
        
        assert response.status_code == 400
        data = response.json()
        assert "already registered" in data["detail"].lower()
    
    def test_invalid_username_registration(self, test_client):
        """Test registration with invalid username."""
        invalid_users = [
            {"username": "ab", "password": "validpassword"},  # Too short
            {"username": "", "password": "validpassword"},    # Empty
            {"username": "a" * 51, "password": "validpassword"}  # Too long
        ]
        
        for user_data in invalid_users:
            response = test_client.post("/api/auth/register", json=user_data)
            assert response.status_code == 422  # Validation error
    
    def test_invalid_password_registration(self, test_client):
        """Test registration with invalid password."""
        invalid_users = [
            {"username": "validuser", "password": "short"},   # Too short
            {"username": "validuser", "password": ""},        # Empty
        ]
        
        for user_data in invalid_users:
            response = test_client.post("/api/auth/register", json=user_data)
            assert response.status_code == 422  # Validation error

class TestUserLogin:
    """Test user login functionality."""
    
    def test_successful_login(self, test_client, sample_user):
        """Test successful user login."""
        # Register user first
        test_client.post("/api/auth/register", json=sample_user)
        
        # Login
        response = test_client.post("/api/auth/login", json=sample_user)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
    
    def test_login_with_invalid_username(self, test_client, sample_user):
        """Test login with non-existent username."""
        response = test_client.post("/api/auth/login", json={
            "username": "nonexistentuser",
            "password": "password123"
        })
        
        assert response.status_code == 401
        data = response.json()
        assert "incorrect" in data["detail"].lower()
    
    def test_login_with_invalid_password(self, test_client, sample_user):
        """Test login with wrong password."""
        # Register user first
        test_client.post("/api/auth/register", json=sample_user)
        
        # Try login with wrong password
        response = test_client.post("/api/auth/login", json={
            "username": sample_user["username"],
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        data = response.json()
        assert "incorrect" in data["detail"].lower()
    
    def test_login_missing_credentials(self, test_client):
        """Test login with missing credentials."""
        # Missing username
        response = test_client.post("/api/auth/login", json={"password": "password123"})
        assert response.status_code == 422
        
        # Missing password
        response = test_client.post("/api/auth/login", json={"username": "testuser"})
        assert response.status_code == 422
        
        # Missing both
        response = test_client.post("/api/auth/login", json={})
        assert response.status_code == 422

class TestUserLogout:
    """Test user logout functionality."""
    
    def test_successful_logout(self, authenticated_client):
        """Test successful user logout."""
        response = authenticated_client.post("/api/auth/logout")
        
        assert response.status_code == 200
        data = response.json()
        assert "successfully logged out" in data["message"].lower()
    
    def test_logout_with_invalid_token(self, test_client):
        """Test logout with invalid token."""
        response = test_client.post(
            "/api/auth/logout",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
    
    def test_logout_without_token(self, test_client):
        """Test logout without authorization header."""
        response = test_client.post("/api/auth/logout")
        
        assert response.status_code == 403  # Forbidden due to missing auth
    
    def test_token_blacklisted_after_logout(self, authenticated_client):
        """Test that token is blacklisted after logout."""
        # First, logout the user
        logout_response = authenticated_client.post("/api/auth/logout")
        assert logout_response.status_code == 200
        
        # Try to access profile with the same token
        profile_response = authenticated_client.get("/api/auth/profile")
        assert profile_response.status_code == 401
        
        data = profile_response.json()
        assert "invalidated" in data["detail"].lower()

class TestUserProfile:
    """Test user profile functionality."""
    
    def test_get_profile_success(self, authenticated_client, sample_user):
        """Test successful profile retrieval."""
        response = authenticated_client.get("/api/auth/profile")
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["username"] == sample_user["username"]
        assert "created_at" in data
        assert "password" not in data  # Password should not be returned
    
    def test_get_profile_without_token(self, test_client):
        """Test profile access without token."""
        response = test_client.get("/api/auth/profile")
        
        assert response.status_code == 403  # Forbidden
    
    def test_get_profile_with_invalid_token(self, test_client):
        """Test profile access with invalid token."""
        response = test_client.get(
            "/api/auth/profile",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
    
    def test_get_profile_with_malformed_token(self, test_client):
        """Test profile access with malformed authorization header."""
        # Missing 'Bearer' prefix
        response = test_client.get(
            "/api/auth/profile",
            headers={"Authorization": "invalid_token"}
        )
        
        assert response.status_code == 403

class TestEndpointIntegration:
    """Test complete user flow integration."""
    
    def test_complete_user_flow(self, test_client):
        """Test complete user registration -> login -> profile -> logout flow."""
        user_data = {"username": "flowtest", "password": "flowpassword123"}
        
        # 1. Register
        register_response = test_client.post("/api/auth/register", json=user_data)
        assert register_response.status_code == 201
        user_id = register_response.json()["id"]
        
        # 2. Login
        login_response = test_client.post("/api/auth/login", json=user_data)
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # 3. Access profile
        profile_response = test_client.get(
            "/api/auth/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert profile_response.status_code == 200
        profile_data = profile_response.json()
        assert profile_data["id"] == user_id
        assert profile_data["username"] == user_data["username"]
        
        # 4. Logout
        logout_response = test_client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert logout_response.status_code == 200
        
        # 5. Verify token is invalidated
        final_profile_response = test_client.get(
            "/api/auth/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert final_profile_response.status_code == 401
    
    def test_multiple_user_registration(self, test_client):
        """Test that multiple users can register and login independently."""
        users = [
            {"username": "user1", "password": "password1"},
            {"username": "user2", "password": "password2"},
            {"username": "user3", "password": "password3"}
        ]
        
        tokens = []
        
        # Register and login all users
        for user_data in users:
            # Register
            register_response = test_client.post("/api/auth/register", json=user_data)
            assert register_response.status_code == 201
            
            # Login
            login_response = test_client.post("/api/auth/login", json=user_data)
            assert login_response.status_code == 200
            token = login_response.json()["access_token"]
            tokens.append(token)
        
        # Verify each user can access their profile
        for i, (user_data, token) in enumerate(zip(users, tokens)):
            profile_response = test_client.get(
                "/api/auth/profile",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert profile_response.status_code == 200
            profile_data = profile_response.json()
            assert profile_data["username"] == user_data["username"]

class TestHealthCheck:
    """Test health check endpoint."""
    
    def test_health_check(self, test_client):
        """Test health check endpoint."""
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"