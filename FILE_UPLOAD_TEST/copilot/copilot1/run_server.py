#!/usr/bin/env python3
"""
Simple script to run the File Upload & Management System server.
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

# Change to backend directory
os.chdir(backend_dir)

if __name__ == "__main__":
    try:
        import uvicorn
        from main import app
        
        print("🚀 Starting File Upload & Management System...")
        print("📁 Backend running on: http://localhost:8000")
        print("🌐 Frontend available at: http://localhost:8000")
        print("📚 API docs at: http://localhost:8000/docs")
        print("\nPress Ctrl+C to stop the server\n")
        
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000, 
            reload=True,
            log_level="info"
        )
        
    except ImportError:
        print("❌ Error: Required dependencies not installed.")
        print("Please run: pip install -r backend/requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)