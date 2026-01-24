#!/usr/bin/env python3
"""
Test runner script for the File Upload & Management System
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    """Run tests with proper path setup"""
    print("🧪 Running File Upload & Management System Tests")
    print("=" * 50)
    
    # Get project directories
    project_root = Path(__file__).parent
    backend_dir = project_root / "backend"
    tests_dir = project_root / "tests"
    
    # Check directories exist
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        return 1
    
    if not tests_dir.exists():
        print("❌ Tests directory not found!")
        return 1
    
    # Add backend to Python path
    backend_path = str(backend_dir.absolute())
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    
    print(f"📁 Backend path: {backend_path}")
    print(f"📁 Tests directory: {tests_dir}")
    
    # Change to tests directory
    os.chdir(tests_dir)
    
    try:
        # Import required modules to verify setup
        sys.path.insert(0, backend_path)
        import main
        print("✅ Backend modules imported successfully")
        
        # Run pytest
        print("🚀 Starting test execution...")
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "test_file_management.py", 
            "-v", 
            "--tb=short"
        ], env={**os.environ, "PYTHONPATH": backend_path})
        
        if result.returncode == 0:
            print("✅ All tests passed!")
        else:
            print("❌ Some tests failed!")
        
        return result.returncode
        
    except ImportError as e:
        print(f"❌ Failed to import backend modules: {e}")
        print("Make sure the backend directory contains main.py")
        return 1
    except KeyboardInterrupt:
        print("\n🛑 Tests stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())