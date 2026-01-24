"""
Integration test for the authentication API
Run this with the backend server running: python test_api_integration.py
"""
import httpx
import uuid
import sys

BASE_URL = "http://localhost:8000"

def test_auth_flow():
    """Test complete authentication flow"""
    print("Testing Authentication API Integration...")
    print("=" * 50)
    
    # Generate unique username
    unique_user = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "testpassword"
    
    print(f"Test user: {unique_user}")
    print()
    
    # 1. REGISTER
    print("1. Testing REGISTER...")
    try:
        response = httpx.post(f"{BASE_URL}/api/auth/register", json={
            "username": unique_user,
            "password": password
        }, timeout=10.0)
        
        assert response.status_code in (200, 201), f"Register failed with status {response.status_code}: {response.text}"
        print(f"   [OK] Registration successful: {response.json()}")
    except httpx.ConnectError:
        print("   [ERROR] Cannot connect to backend server!")
        print("   Make sure the backend is running on http://localhost:8000")
        sys.exit(1)
    except AssertionError as e:
        print(f"   [FAIL] {e}")
        sys.exit(1)
    
    # 2. LOGIN
    print("\n2. Testing LOGIN...")
    try:
        response = httpx.post(f"{BASE_URL}/api/auth/login", json={
            "username": unique_user,
            "password": password
        }, timeout=10.0)
        
        assert response.status_code == 200, f"Login failed with status {response.status_code}: {response.text}"
        data = response.json()
        token = data.get("access_token")
        assert token, "No access token in login response"
        print(f"   [OK] Login successful, received token: {token[:20]}...")
    except AssertionError as e:
        print(f"   [FAIL] {e}")
        sys.exit(1)
    
    # 3. GET PROFILE
    print("\n3. Testing GET PROFILE...")
    try:
        response = httpx.get(
            f"{BASE_URL}/api/auth/profile",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10.0
        )
        
        assert response.status_code == 200, f"Get profile failed with status {response.status_code}: {response.text}"
        profile = response.json()
        assert profile["username"] == unique_user, "Username mismatch"
        print(f"   [OK] Profile retrieved: {profile}")
    except AssertionError as e:
        print(f"   [FAIL] {e}")
        sys.exit(1)
    
    # 4. LOGOUT
    print("\n4. Testing LOGOUT...")
    try:
        response = httpx.post(
            f"{BASE_URL}/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10.0
        )
        
        assert response.status_code == 200, f"Logout failed with status {response.status_code}: {response.text}"
        print(f"   [OK] Logout successful: {response.json()}")
    except AssertionError as e:
        print(f"   [FAIL] {e}")
        sys.exit(1)
    
    # 5. VERIFY TOKEN IS INVALID AFTER LOGOUT
    print("\n5. Testing TOKEN INVALIDATION...")
    try:
        response = httpx.get(
            f"{BASE_URL}/api/auth/profile",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10.0
        )
        
        assert response.status_code == 401, f"Expected 401 after logout, got {response.status_code}"
        print(f"   [OK] Token correctly invalidated after logout")
    except AssertionError as e:
        print(f"   [FAIL] {e}")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("[SUCCESS] ALL INTEGRATION TESTS PASSED!")
    print("=" * 50)

if __name__ == "__main__":
    test_auth_flow()

