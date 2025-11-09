#!/usr/bin/env python3
"""
Startup script for the File Upload & Management System backend
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    backend_dir = script_dir / "backend"
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    print("🚀 Starting File Upload & Management System Backend...")
    print(f"📁 Working directory: {backend_dir}")
    print("🌐 API will be available at: http://localhost:8000")
    print("📚 API documentation at: http://localhost:8000/docs")
    print("🔄 Auto-reload enabled for development")
    print("\n" + "="*50)
    
    try:
        # Run uvicorn with auto-reload for development
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload",
            "--log-level", "info"
        ], check=True)
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error starting server: {e}")
        print("\n💡 Make sure you have installed the requirements:")
        print("   pip install -r requirements.txt")
    except FileNotFoundError:
        print("\n❌ Python or uvicorn not found")
        print("\n💡 Make sure you have Python installed and requirements installed:")
        print("   pip install -r requirements.txt")

if __name__ == "__main__":
    main()
