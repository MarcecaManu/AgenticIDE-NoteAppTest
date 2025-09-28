#!/usr/bin/env python3
"""
API Test Script for Authentication System
Tests all authentication endpoints with proper error handling
"""
import httpx
import uuid
import sys
import json

BASE_URL = "http://localhost:8000"

def print_response(response, operation):
    """Helper function to print response details"""
    print(f"\n{operation}:")
    print(f"  Status Code: {response.status_code}")
    try:
        print(f"  Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"  Response Text: {response.text}")

def test_auth_flow():
    """Test complete authentication flow"""
    print("Starting Authentication API Test...")
    
    # Generate unique username
    unique_user = f"testuser_{uuid.uuid4().hex[:8]}"
    password = "testpassword123"
    
    print(f"Testing with username: {unique_user}")
    
    try:
        # 1. REGISTER
        print("\n=== REGISTRATION TEST ===")
        response = httpx.post(f"{BASE_URL}/api/auth/register", json={
            "username": unique_user,
            "password": password
        })
        print_response(response, "Register")
        
        if response.status_code not in (200, 201):
            print(f"❌ Registration failed with status {response.status_code}")
            return False
        print("✅ Registration successful")
        
        # 2. LOGIN
        print("\n=== LOGIN TEST ===")
        response = httpx.post(f"{BASE_URL}/api/auth/login", json={
            "username": unique_user,
            "password": password
        })
        print_response(response, "Login")
        
        if response.status_code != 200:
            print(f"❌ Login failed with status {response.status_code}")
            return False
            
        token_data = response.json()
        token = token_data.get("access_token")
        if not token:
            print("❌ No access token received")
            return False
        print("✅ Login successful, token received")

        headers = {"Authorization": f"Bearer {token}"}

        # 3. PROFILE
        print("\n=== PROFILE TEST ===")
        response = httpx.get(f"{BASE_URL}/api/auth/profile", headers=headers)
        print_response(response, "Get Profile")
        
        if response.status_code != 200:
            print(f"❌ Profile retrieval failed with status {response.status_code}")
            return False
            
        profile = response.json()
        if profile.get("username") != unique_user:
            print(f"❌ Profile username mismatch. Expected: {unique_user}, Got: {profile.get('username')}")
            return False
        print("✅ Profile retrieval successful")

        # 4. LOGOUT
        print("\n=== LOGOUT TEST ===")
        response = httpx.post(f"{BASE_URL}/api/auth/logout", headers=headers)
        print_response(response, "Logout")
        
        if response.status_code not in (200, 204):
            print(f"❌ Logout failed with status {response.status_code}")
            return False
        print("✅ Logout successful")
        
        # 5. VERIFY TOKEN IS BLACKLISTED
        print("\n=== TOKEN BLACKLIST VERIFICATION ===")
        response = httpx.get(f"{BASE_URL}/api/auth/profile", headers=headers)
        print_response(response, "Profile with blacklisted token")
        
        if response.status_code == 200:
            print("❌ Token should be blacklisted but still works")
            return False
        print("✅ Token successfully blacklisted")
        
        print("\n🎉 All tests passed successfully!")
        return True
        
    except httpx.ConnectError:
        print("❌ Connection error: Make sure the server is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_error_cases():
    """Test error handling"""
    print("\n=== ERROR HANDLING TESTS ===")
    
    try:
        # Test invalid registration
        print("\nTesting invalid registration (short password)...")
        response = httpx.post(f"{BASE_URL}/api/auth/register", json={
            "username": "testuser",
            "password": "123"  # Too short
        })
        print_response(response, "Invalid Registration")
        if response.status_code == 400:
            print("✅ Short password correctly rejected")
        
        # Test invalid login
        print("\nTesting invalid login...")
        response = httpx.post(f"{BASE_URL}/api/auth/login", json={
            "username": "nonexistent",
            "password": "wrongpassword"
        })
        print_response(response, "Invalid Login")
        if response.status_code == 401:
            print("✅ Invalid credentials correctly rejected")
            
        # Test profile without token
        print("\nTesting profile access without token...")
        response = httpx.get(f"{BASE_URL}/api/auth/profile")
        print_response(response, "Profile without token")
        if response.status_code == 403:
            print("✅ Unauthorized access correctly rejected")
            
    except Exception as e:
        print(f"Error in error handling tests: {e}")

if __name__ == "__main__":
    print("Authentication API Test Suite")
    print("=" * 50)
    
    # Test server availability
    try:
        response = httpx.get(f"{BASE_URL}/")
        print(f"✅ Server is running at {BASE_URL}")
    except httpx.ConnectError:
        print(f"❌ Server is not running at {BASE_URL}")
        print("Please start the server with: python backend/main.py")
        sys.exit(1)
    
    # Run main test
    success = test_auth_flow()
    
    # Run error handling tests
    test_error_cases()
    
    if success:
        print("\n🎉 API Test Suite completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ API Test Suite failed!")
        sys.exit(1)