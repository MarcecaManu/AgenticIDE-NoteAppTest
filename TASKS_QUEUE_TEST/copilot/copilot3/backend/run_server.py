"""Run the FastAPI server with uvicorn."""
import uvicorn
import os
import sys

# Add parent directory to path so we can import from backend
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("=" * 60)
    print("Starting Task Queue Server")
    print("=" * 60)
    print("Server will be available at: http://localhost:8000")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Set to True for development
        log_level="info"
    )
