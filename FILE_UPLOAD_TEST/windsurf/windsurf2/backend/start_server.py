#!/usr/bin/env python3
"""
Startup script for the File Upload & Management API server.
This script provides a convenient way to start the server with proper configuration.
"""

import uvicorn
import os
from pathlib import Path

def main():
    """Start the FastAPI server with production-ready configuration."""
    
    # Ensure upload directory exists
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    
    print("🚀 Starting File Upload & Management API Server...")
    print(f"📁 Upload directory: {upload_dir.absolute()}")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📖 API documentation: http://localhost:8000/docs")
    print("🔄 Interactive API: http://localhost:8000/redoc")
    print("\nPress Ctrl+C to stop the server\n")
    
    # Start the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )

if __name__ == "__main__":
    main()
