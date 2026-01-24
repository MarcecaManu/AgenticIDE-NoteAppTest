#!/usr/bin/env python3
"""
Startup script for the Real-time Chat System
Runs the FastAPI server with uvicorn
"""

import uvicorn
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

if __name__ == "__main__":
    print("=" * 60)
    print("Real-time Chat System")
    print("=" * 60)
    print("\nStarting server...")
    print("Server will be available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    print("\nPress CTRL+C to stop the server\n")
    print("=" * 60)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        app_dir="backend"
    )

