#!/usr/bin/env python3
"""
Startup script for the File Upload & Management System
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    """Main startup function"""
    print("🚀 Starting File Upload & Management System")
    print("=" * 50)
    
    # Get the project root directory
    project_root = Path(__file__).parent
    backend_dir = project_root / "backend"
    
    # Check if backend directory exists
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        return 1
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Check if main.py exists
    if not (backend_dir / "main.py").exists():
        print("❌ Backend main.py not found!")
        return 1
    
    print(f"📁 Working directory: {backend_dir}")
    print("🔧 Starting FastAPI server...")
    print("📍 API will be available at: http://127.0.0.1:8000")
    print("📚 API docs will be available at: http://127.0.0.1:8000/docs")
    print("🌐 Open frontend/index.html in your browser to use the web interface")
    print("")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Start the FastAPI server
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting server: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())