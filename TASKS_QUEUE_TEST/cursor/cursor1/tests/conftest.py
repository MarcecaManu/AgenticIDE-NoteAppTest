import pytest
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with test database"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_task_data():
    """Sample task data for testing"""
    return {
        "csv_processing": {
            "task_type": "csv_processing",
            "input_params": {
                "num_rows": 100,
                "processing_time": 1
            }
        },
        "email_sending": {
            "task_type": "email_sending",
            "input_params": {
                "num_emails": 3,
                "subject": "Test Email",
                "delay_per_email": 0.5
            }
        },
        "image_processing": {
            "task_type": "image_processing",
            "input_params": {
                "num_images": 2,
                "target_width": 800,
                "target_height": 600
            }
        }
    }

