#!/usr/bin/env python
"""
Convenience script to start the Real-time Chat server
"""
import sys
import os

# Get the directory paths
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(script_dir, 'backend')

# Add backend to path
sys.path.insert(0, backend_dir)

# Change to backend directory so relative imports work
os.chdir(backend_dir)

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("🚀 Starting Real-time Chat Server")
    print("=" * 60)
    print("📍 Server URL: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("💬 Frontend: http://localhost:8000")
    print("=" * 60)
    print("\nPress CTRL+C to stop the server\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

