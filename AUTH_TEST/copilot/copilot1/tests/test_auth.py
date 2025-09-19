import pytest
from fastapi.testclient import TestClient
from backend.main import app
import json
import os

client = TestClient(app)

def setup_module(module):
    # Remove test database if it exists
    if os.path.exists("users.db"):
        try:
            os.remove("users.db")
        except PermissionError:
            pass
    # Initialize the database
    from backend.main import init_db
    init_db()

def teardown_module(module):
    # Clean up test database
    try:
        if os.path.exists("users.db"):
            os.remove("users.db")
    except PermissionError:
        pass  # Database file might be locked

def test_register():
    response = client.post(
        "/api/auth/register",
        json={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "User registered successfully"}

    # Test duplicate registration
    response = client.post(
        "/api/auth/register",
        json={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 400
    assert "Username already registered" in response.json()["detail"]

def test_login():
    # Register a user first
    client.post(
        "/api/auth/register",
        json={"username": "loginuser", "password": "testpass"}
    )

    # Test successful login
    response = client.post(
        "/api/auth/login",
        data={"username": "loginuser", "password": "testpass"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

    # Test failed login
    response = client.post(
        "/api/auth/login",
        data={"username": "loginuser", "password": "wrongpass"}
    )
    assert response.status_code == 401

def test_profile():
    # Register and login
    client.post(
        "/api/auth/register",
        json={"username": "profileuser", "password": "testpass"}
    )
    response = client.post(
        "/api/auth/login",
        data={"username": "profileuser", "password": "testpass"}
    )
    token = response.json()["access_token"]

    # Test profile access with token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/auth/profile", headers=headers)
    assert response.status_code == 200
    assert response.json()["username"] == "profileuser"

    # Test profile access without token
    response = client.get("/api/auth/profile")
    assert response.status_code == 401

def test_logout():
    response = client.post("/api/auth/logout")
    assert response.status_code == 200
    assert response.json() == {"message": "Logged out successfully"}
