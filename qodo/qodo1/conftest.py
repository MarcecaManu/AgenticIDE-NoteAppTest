import os
import sys
import pytest
from pathlib import Path

# Add the project root directory to Python path
root_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, root_dir)

@pytest.fixture(scope="session", autouse=True)
def setup_python_path():
    # Ensure backend directory is in Python path
    backend_dir = os.path.join(root_dir, "backend")
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)

@pytest.fixture(autouse=True)
def clean_test_db():
    # Setup: ensure we have a clean database for each test
    db_path = Path(root_dir) / "backend" / "notes.json"
    try:
        if db_path.exists():
            os.remove(db_path)
    except PermissionError:
        # If file is locked, wait a bit and try again
        import time
        time.sleep(0.1)
        if db_path.exists():
            os.remove(db_path)
    
    yield
    
    # Teardown: clean up after tests
    try:
        if db_path.exists():
            os.remove(db_path)
    except PermissionError:
        # If file is locked, wait a bit and try again
        import time
        time.sleep(0.1)
        if db_path.exists():
            os.remove(db_path)
