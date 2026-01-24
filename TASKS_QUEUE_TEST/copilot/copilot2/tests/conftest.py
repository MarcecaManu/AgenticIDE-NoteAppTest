"""
Pytest configuration and fixtures for testing the Task Queue system.
"""

import pytest
import sys
import os
import uuid
import time
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.main import app
from backend.database import Base, get_db


@pytest.fixture(scope="function")
def test_db():
    """Create a fresh test database for each test"""
    # Use in-memory database to avoid file locking issues on Windows
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Override get_db dependency
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    db = TestingSessionLocal()
    yield db
    
    # Cleanup
    db.close()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def sample_task_data():
    """Sample task data for testing"""
    return {
        "data_processing": {
            "task_type": "data_processing",
            "input_data": {"rows": 100}
        },
        "data_processing_alt": {
            "task_type": "DATA_PROCESSING",
            "parameters": {"num_rows": 100, "processing_time": 2}
        },
        "email_simulation": {
            "task_type": "email_simulation",
            "input_data": {"recipient_count": 5, "delay_per_email": 0.5}
        },
        "email_simulation_alt": {
            "task_type": "EMAIL_SIMULATION",
            "parameters": {"num_emails": 5, "delay_per_email": 0.5}
        },
        "image_processing": {
            "task_type": "image_processing",
            "input_data": {"image_count": 3, "operation": "resize", "target_size": "800x600"}
        },
        "image_processing_alt": {
            "task_type": "IMAGE_PROCESSING",
            "parameters": {"num_images": 3, "target_size": "800x600", "output_format": "resize"}
        }
    }
