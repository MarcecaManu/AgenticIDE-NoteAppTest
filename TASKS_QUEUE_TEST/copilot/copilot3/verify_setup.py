"""Quick verification script to test the setup."""
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("=" * 60)
print("Task Queue System - Setup Verification")
print("=" * 60)

# 1. Check imports
print("\n1. Checking imports...")
try:
    from main import app
    from models import Base, Task, TaskStatus
    from database import init_db
    from task_queue import task_queue
    print("   ✓ All imports successful")
except Exception as e:
    print(f"   ✗ Import failed: {e}")
    sys.exit(1)

# 2. Check frontend directory
print("\n2. Checking frontend directory...")
frontend_dir = Path(__file__).parent / "frontend"
index_file = frontend_dir / "index.html"
if frontend_dir.exists() and index_file.exists():
    print(f"   ✓ Frontend directory exists: {frontend_dir}")
    print(f"   ✓ index.html found")
else:
    print(f"   ✗ Frontend directory or index.html missing")
    sys.exit(1)

# 3. Check database initialization
print("\n3. Checking database initialization...")
try:
    init_db()
    print("   ✓ Database initialized successfully")
except Exception as e:
    print(f"   ✗ Database initialization failed: {e}")
    sys.exit(1)

# 4. Check test file
print("\n4. Checking test file...")
test_file = Path(__file__).parent / "tests" / "test_api.py"
if test_file.exists():
    print(f"   ✓ Test file exists: {test_file}")
else:
    print(f"   ✗ Test file missing")
    sys.exit(1)

print("\n" + "=" * 60)
print("All checks passed! ✓")
print("=" * 60)
print("\nTo start the server:")
print("  cd backend")
print("  python main.py")
print("\nTo run tests:")
print("  pytest tests\\test_api.py -v")
print("\nServer will be available at: http://localhost:8000")
print("=" * 60)
