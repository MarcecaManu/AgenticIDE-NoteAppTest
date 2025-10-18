import sys
import os
import pytest
from fastapi.testclient import TestClient

# Add the parent directory to Python path for absolute imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.app.main import app

client = TestClient(app)

def test_register():
    # Test successful registration
    response = client.post(
        "/api/auth/register",
        json={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

    # Test duplicate registration
    response = client.post(
        "/api/auth/register",
        json={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 400

def test_login():
    # Register a user first
    client.post(
        "/api/auth/register",
        json={"username": "logintest", "password": "testpass"}
    )

    # Test successful login
    response = client.post(
        "/api/auth/login",
        data={"username": "logintest", "password": "testpass"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

    # Test failed login
    response = client.post(
        "/api/auth/login",
        data={"username": "logintest", "password": "wrongpass"}
    )
    assert response.status_code == 401

def test_profile():
    # Register and login first
    client.post(
        "/api/auth/register",
        json={"username": "profiletest", "password": "testpass"}
    )
    login_response = client.post(
        "/api/auth/login",
        data={"username": "profiletest", "password": "testpass"}
    )
    token = login_response.json()["access_token"]

    # Test profile access with valid token
    response = client.get(
        "/api/auth/profile",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "profiletest"

    # Test profile access without token
    response = client.get("/api/auth/profile")
    assert response.status_code == 401

def test_logout():
    # Register and login first
    client.post(
        "/api/auth/register",
        json={"username": "logouttest", "password": "testpass"}
    )
    login_response = client.post(
        "/api/auth/login",
        data={"username": "logouttest", "password": "testpass"}
    )
    token = login_response.json()["access_token"]

    # Test logout with valid token
    response = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Successfully logged out"

    # Test logout without token
    response = client.post("/api/auth/logout")
    assert response.status_code == 401
