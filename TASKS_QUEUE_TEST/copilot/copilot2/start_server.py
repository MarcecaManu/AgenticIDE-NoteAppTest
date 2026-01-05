"""
Script to start the FastAPI server.
Usage: python start_server.py
"""

import uvicorn
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

if __name__ == "__main__":
    print("🚀 Starting FastAPI Task Queue Server...")
    print("📡 API will be available at: http://localhost:8000")
    print("📚 API docs at: http://localhost:8000/docs")
    print("\n⚠️  Make sure Redis is running!")
    print("⚠️  Start Celery worker in another terminal with:")
    print("   cd backend && celery -A celery_app.celery_app worker --loglevel=info --pool=solo\n")
    
    # Change to backend directory
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    os.chdir(backend_dir)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
