"""Pytest configuration and fixtures."""
import pytest
import sys
import os
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from database import Base, get_db


@pytest.fixture(scope="function")
def test_engine():
    """Create a test database engine."""
    # Use a temporary file-based database instead of in-memory
    # This ensures all sessions share the same database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    
    # Clean up the temporary file
    try:
        os.unlink(db_path)
    except:
        pass


@pytest.fixture(scope="function")
def test_sessionlocal(test_engine):
    """Create a test SessionLocal factory."""
    return sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def override_get_db(test_engine, test_sessionlocal):
    """Override the get_db dependency and inject test session into task_queue."""
    # Import here to avoid circular imports and ensure fresh imports
    from main import app, get_task_queue
    import task_queue as tq
    
    def _get_test_db():
        db = test_sessionlocal()
        try:
            yield db
        finally:
            db.close()
    
    # Create a new task_queue with test session factory
    test_task_queue = tq.TaskQueue(session_factory=test_sessionlocal)
    
    def _get_test_task_queue():
        return test_task_queue
    
    # Override FastAPI dependencies
    app.dependency_overrides[get_db] = _get_test_db
    app.dependency_overrides[get_task_queue] = _get_test_task_queue
    
    yield
    
    # Clean up
    app.dependency_overrides.clear()

