#!/usr/bin/env python3
"""
Setup script for the File Upload & Management System
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def main():
    print("🚀 Setting up File Upload & Management System")
    print("=" * 50)
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    backend_dir = script_dir / "backend"
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {python_version.major}.{python_version.minor}")
        return False
    
    print(f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Install backend dependencies
    print(f"\n📦 Installing backend dependencies from {backend_dir}/requirements.txt")
    
    if not (backend_dir / "requirements.txt").exists():
        print("❌ requirements.txt not found in backend directory")
        return False
    
    # Change to backend directory for installation
    original_dir = os.getcwd()
    os.chdir(backend_dir)
    
    success = run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing Python dependencies"
    )
    
    # Return to original directory
    os.chdir(original_dir)
    
    if not success:
        print("\n💡 Try running manually:")
        print(f"   cd {backend_dir}")
        print("   pip install -r requirements.txt")
        return False
    
    # Create uploads directory
    uploads_dir = backend_dir / "uploads"
    uploads_dir.mkdir(exist_ok=True)
    print(f"✅ Created uploads directory: {uploads_dir}")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Start the backend server:")
    print("   python start_backend.py")
    print("\n2. In another terminal, start the frontend:")
    print("   python start_frontend.py")
    print("\n3. Or run tests:")
    print("   python -m pytest tests/ -v")
    
    print("\n🌐 URLs:")
    print("   Frontend: http://localhost:3000")
    print("   Backend API: http://localhost:8000")
    print("   API Docs: http://localhost:8000/docs")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
