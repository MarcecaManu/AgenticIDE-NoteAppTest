"""
Convenience script to run the application
"""
import uvicorn

if __name__ == "__main__":
    print("Starting Task Queue & Background Processing System...")
    print("Server will be available at http://localhost:8000")
    print("Press CTRL+C to stop the server")
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

