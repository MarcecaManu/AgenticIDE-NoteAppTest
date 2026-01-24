"""
FastAPI Real-time Chat System
Main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os
from pathlib import Path

from database import init_db
from routes import chat_router, websocket_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    init_db()
    yield


app = FastAPI(
    title="Real-time Chat API",
    description="WebSocket-based chat system with room management",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
app.include_router(websocket_router, tags=["websocket"])


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Get the absolute path to the frontend directory
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

# Mount static files (frontend) - must be last
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
    
    @app.get("/")
    async def serve_frontend():
        """Serve the main frontend HTML page"""
        index_path = FRONTEND_DIR / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        return {"error": "Frontend not found"}
else:
    @app.get("/")
    async def no_frontend():
        """Frontend directory not found"""
        return {"error": "Frontend directory not found", "path": str(FRONTEND_DIR)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

