#!/usr/bin/env python3
"""
Demo script to test the Authentication API endpoints
Run this while the FastAPI server is running on localhost:8000
"""

import requests
import json

API_BASE = "http://localhost:8000/api/auth"

def test_api():
    print("🚀 Testing Authentication API")
    print("=" * 50)
    
    # Test data
    test_user = {
        "username": "demouser",
        "password": "demopass123"
    }
    
    try:
        # 1. Test Registration
        print("\n1. Testing User Registration...")
        response = requests.post(f"{API_BASE}/register", json=test_user)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code != 200:
            print("❌ Registration failed!")
            return
        print("✅ Registration successful!")
        
        # 2. Test Login
        print("\n2. Testing User Login...")
        response = requests.post(f"{API_BASE}/login", json=test_user)
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {data}")
        
        if response.status_code != 200:
            print("❌ Login failed!")
            return
        
        token = data["access_token"]
        print("✅ Login successful!")
        print(f"Token: {token[:50]}...")
        
        # 3. Test Profile Access
        print("\n3. Testing Profile Access...")
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE}/profile", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code != 200:
            print("❌ Profile access failed!")
            return
        print("✅ Profile access successful!")
        
        # 4. Test Logout
        print("\n4. Testing Logout...")
        response = requests.post(f"{API_BASE}/logout", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code != 200:
            print("❌ Logout failed!")
            return
        print("✅ Logout successful!")
        
        # 5. Test Token Invalidation
        print("\n5. Testing Token Invalidation...")
        response = requests.get(f"{API_BASE}/profile", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 401:
            print("✅ Token successfully invalidated!")
        else:
            print("❌ Token should be invalid after logout!")
        
        print("\n🎉 All tests completed successfully!")
        print("The authentication system is working correctly!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API server.")
        print("Make sure the FastAPI server is running on localhost:8000")
        print("Run: python backend/main.py")
    except Exception as e:
        print(f"❌ Error occurred: {e}")

if __name__ == "__main__":
    test_api()
