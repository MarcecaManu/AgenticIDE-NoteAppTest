# api_test.py - Test authentication API endpoints
import httpx
import uuid

BASE_URL = "http://localhost:8000"

def test_auth_flow():
    """Test the complete authentication flow: register, login, profile, logout"""
    unique_user = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "testpassword123"  # Must be at least 6 characters

    print(f"Testing with user: {unique_user}")

    # REGISTER
    print("Testing registration...")
    response = httpx.post(f"{BASE_URL}/api/auth/register", json={
        "username": unique_user,
        "password": password
    })
    print(f"Register response: {response.status_code}")
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    register_data = response.json()
    assert register_data.get("username") == unique_user
    print("✅ Registration successful")
    
    # LOGIN
    print("Testing login...")
    response = httpx.post(f"{BASE_URL}/api/auth/login", json={
        "username": unique_user,
        "password": password
    })
    print(f"Login response: {response.status_code}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    login_data = response.json()
    token = login_data.get("access_token")
    assert token is not None, "Access token not received"
    assert login_data.get("token_type") == "bearer"
    print("✅ Login successful")

    headers = {"Authorization": f"Bearer {token}"}

    # PROFILE
    print("Testing profile retrieval...")
    response = httpx.get(f"{BASE_URL}/api/auth/profile", headers=headers)
    print(f"Profile response: {response.status_code}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    profile = response.json()
    assert profile.get("username") == unique_user
    assert "id" in profile
    assert "created_at" in profile
    print("✅ Profile retrieval successful")

    # LOGOUT
    print("Testing logout...")
    response = httpx.post(f"{BASE_URL}/api/auth/logout", headers=headers)
    print(f"Logout response: {response.status_code}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    logout_data = response.json()
    assert logout_data.get("message") == "Successfully logged out"
    print("✅ Logout successful")

    # Test that token is invalidated
    print("Testing token invalidation...")
    response = httpx.get(f"{BASE_URL}/api/auth/profile", headers=headers)
    print(f"Profile after logout response: {response.status_code}")
    assert response.status_code == 401, f"Expected 401 after logout, got {response.status_code}"
    print("✅ Token properly invalidated")

def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check...")
    response = httpx.get(f"{BASE_URL}/api/health")
    assert response.status_code == 200
    health_data = response.json()
    assert health_data.get("status") == "healthy"
    print("✅ Health check successful")

def test_error_cases():
    """Test various error scenarios"""
    print("Testing error cases...")
    
    # Test registration with short username
    response = httpx.post(f"{BASE_URL}/api/auth/register", json={
        "username": "ab",  # Too short
        "password": "testpassword123"
    })
    assert response.status_code == 400
    print("✅ Short username properly rejected")
    
    # Test registration with short password
    response = httpx.post(f"{BASE_URL}/api/auth/register", json={
        "username": "validuser@example.com",
        "password": "12345"  # Too short
    })
    assert response.status_code == 400
    print("✅ Short password properly rejected")
    
    # Test login with invalid credentials
    response = httpx.post(f"{BASE_URL}/api/auth/login", json={
        "username": "nonexistent@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    print("✅ Invalid credentials properly rejected")

if __name__ == "__main__":
    try:
        test_health_check()
        test_auth_flow()
        test_error_cases()
        print("\n🎉 All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise
