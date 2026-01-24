"""
Test configuration and fixtures for chat system tests.
"""
import pytest
import asyncio
import sys
import time
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from fastapi.testclient import TestClient
from httpx import AsyncClient
import aiosqlite

# Import app components
from main import app
from database import init_db, DB_PATH


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


def cleanup_database():
    """Synchronously cleanup the database file."""
    if DB_PATH.exists():
        # Try multiple times to handle file locking on Windows
        for _ in range(5):
            try:
                DB_PATH.unlink()
                break
            except PermissionError:
                time.sleep(0.1)


@pytest.fixture(autouse=True)
def setup_test_db():
    """Setup and teardown test database for each test."""
    # Cleanup any existing database
    cleanup_database()
    
    # Initialize fresh database synchronously
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(init_db())
    loop.close()
    
    yield
    
    # Cleanup after test
    cleanup_database()


@pytest.fixture
def client(setup_test_db):
    """Create a test client for synchronous requests."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
async def async_client():
    """Create an async test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

