import os
import pytest
from httpx import AsyncClient
import json
from ..backend.main import app

@pytest.fixture(autouse=True)
def cleanup_users_file():
    # Before each test
    if os.path.exists("users.json"):
        os.remove("users.json")
    yield
    # After each test
    if os.path.exists("users.json"):
        os.remove("users.json")

@pytest.mark.asyncio
async def test_register_new_user():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/auth/register",
            json={"username": "testuser", "password": "testpass"}
        )
        assert response.status_code == 200
        assert response.json() == {"message": "User created successfully"}

        # Try registering the same user again
        response = await client.post(
            "/api/auth/register",
            json={"username": "testuser", "password": "testpass"}
        )
        assert response.status_code == 400

@pytest.mark.asyncio
async def test_login():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register a user first
        await client.post(
            "/api/auth/register",
            json={"username": "testuser", "password": "testpass"}
        )

        # Login with correct credentials
        response = await client.post(
            "/api/auth/login",
            data={"username": "testuser", "password": "testpass"}
        )
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"

        # Login with incorrect password
        response = await client.post(
            "/api/auth/login",
            data={"username": "testuser", "password": "wrongpass"}
        )
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_profile():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register and login
        await client.post(
            "/api/auth/register",
            json={"username": "testuser", "password": "testpass"}
        )
        login_response = await client.post(
            "/api/auth/login",
            data={"username": "testuser", "password": "testpass"}
        )
        token = login_response.json()["access_token"]

        # Get profile with valid token
        response = await client.get(
            "/api/auth/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["username"] == "testuser"

        # Get profile with invalid token
        response = await client.get(
            "/api/auth/profile",
            headers={"Authorization": "Bearer invalidtoken"}
        )
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_logout():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register and login
        await client.post(
            "/api/auth/register",
            json={"username": "testuser", "password": "testpass"}
        )
        login_response = await client.post(
            "/api/auth/login",
            data={"username": "testuser", "password": "testpass"}
        )
        token = login_response.json()["access_token"]

        # Logout with valid token
        response = await client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json() == {"message": "Successfully logged out"}
