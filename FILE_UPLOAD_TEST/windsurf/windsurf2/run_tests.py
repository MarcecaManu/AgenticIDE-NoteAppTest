#!/usr/bin/env python3
"""
Test runner script for the File Upload & Management system.
This script runs all tests and provides a summary of results.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_tests():
    """Run the test suite and display results."""
    
    print("🧪 Running File Upload & Management System Tests")
    print("=" * 50)
    
    # Change to tests directory
    tests_dir = Path(__file__).parent / "tests"
    
    if not tests_dir.exists():
        print("❌ Tests directory not found!")
        return False
    
    # Install test dependencies
    print("📦 Installing test dependencies...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", 
            str(tests_dir / "requirements.txt")
        ], check=True, capture_output=True)
        print("✅ Test dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install test dependencies: {e}")
        return False
    
    # Run tests
    print("\n🏃 Running tests...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            str(tests_dir / "test_file_api.py"),
            "-v", "--tb=short"
        ], cwd=tests_dir.parent, capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("Warnings/Errors:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("\n✅ All tests passed!")
            return True
        else:
            print(f"\n❌ Tests failed with return code: {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def main():
    """Main function."""
    success = run_tests()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Test suite completed successfully!")
        print("\n📋 Test Coverage Summary:")
        print("  ✅ File upload (valid files)")
        print("  ✅ File upload (invalid files)")
        print("  ✅ File listing")
        print("  ✅ File download")
        print("  ✅ File deletion")
        print("  ✅ File information retrieval")
        print("  ✅ Security validations")
        print("  ✅ Error handling")
    else:
        print("💥 Test suite failed!")
        print("\nPlease check the error messages above and fix any issues.")
        sys.exit(1)

if __name__ == "__main__":
    main()
