import pytest
import os
import sys
import tempfile
from fastapi.testclient import TestClient

# Add the backend directory to the Python path
backend_dir = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_dir)

from main import app
from database import init_database, get_db_connection

@pytest.fixture(scope="function")
def test_client():
    """Create a test client with a temporary database."""
    # Create a temporary database file
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    # Override the database file
    import database
    original_db_file = database.DATABASE_FILE
    database.DATABASE_FILE = temp_db.name
    
    # Initialize the test database
    init_database()
    
    # Create test client
    client = TestClient(app)
    
    yield client
    
    # Cleanup
    database.DATABASE_FILE = original_db_file
    try:
        os.unlink(temp_db.name)
    except OSError:
        pass

@pytest.fixture
def sample_user():
    """Sample user data for testing."""
    return {
        "username": "testuser",
        "password": "testpassword123"
    }

@pytest.fixture
def authenticated_client(test_client, sample_user):
    """Create an authenticated client with a registered user."""
    # Register user
    test_client.post("/api/auth/register", json=sample_user)
    
    # Login to get token
    response = test_client.post("/api/auth/login", json=sample_user)
    token = response.json()["access_token"]
    
    # Create authenticated client
    test_client.headers = {"Authorization": f"Bearer {token}"}
    test_client.token = token
    
    return test_client