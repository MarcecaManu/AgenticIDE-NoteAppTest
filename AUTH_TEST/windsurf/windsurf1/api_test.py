# test_auth_flow.py
import httpx
import uuid

BASE_URL = "http://localhost:8000"

def test_auth_flow():
    unique_user = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "testpassword"

    # REGISTER
    response = httpx.post(f"{BASE_URL}/api/auth/register", json={
        "username": unique_user,
        "password": password
    })
    assert response.status_code in (200, 201)
    
    # LOGIN
    response = httpx.post(f"{BASE_URL}/api/auth/login", json={  # Changed from data= to json=
        "username": unique_user,
        "password": password
    })
    assert response.status_code == 200
    token = response.json().get("access_token")
    assert token is not None

    headers = {"Authorization": f"Bearer {token}"}

    # PROFILE
    response = httpx.get(f"{BASE_URL}/api/auth/profile", headers=headers)
    assert response.status_code == 200
    profile = response.json()
    assert profile.get("username") == unique_user

    # LOGOUT
    response = httpx.post(f"{BASE_URL}/api/auth/logout", headers=headers)
    assert response.status_code in (200, 204)