from fastapi import FastAPI, UploadFile, File, HTTPException, Path
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import uuid
from datetime import datetime
from pathlib import Path as PathLib
from typing import Optional
import mimetypes
import re

app = FastAPI(title="File Upload & Management API")

# CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
# Get the directory where this script is located
BACKEND_DIR = PathLib(__file__).parent
UPLOAD_DIR = BACKEND_DIR / "uploads"
METADATA_FILE = BACKEND_DIR / "metadata.json"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Allowed file types
ALLOWED_MIME_TYPES = {
    "image/jpeg", "image/png", "image/gif", "image/webp", "image/bmp",
    "application/pdf",
    "text/plain", "text/html", "text/css", "text/javascript", "text/csv",
    "application/json", "text/xml"
}

ALLOWED_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp",
    ".pdf",
    ".txt", ".html", ".css", ".js", ".csv", ".json", ".xml"
}


def ensure_directories():
    """Ensure upload directory exists"""
    UPLOAD_DIR.mkdir(exist_ok=True)


def load_metadata() -> dict:
    """Load metadata from JSON file"""
    if METADATA_FILE.exists():
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_metadata(metadata: dict):
    """Save metadata to JSON file"""
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal and remove dangerous characters"""
    # Remove path components
    filename = os.path.basename(filename)
    # Remove or replace dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    # Ensure filename is not empty
    if not filename:
        filename = "unnamed_file"
    return filename


def validate_file_type(file: UploadFile) -> bool:
    """Validate that file type is allowed"""
    # Check extension
    original_filename = file.filename or ""
    ext = PathLib(original_filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False
    
    # Check MIME type if available
    if file.content_type:
        if file.content_type not in ALLOWED_MIME_TYPES:
            return False
    
    return True


def get_file_metadata(file_id: str) -> Optional[dict]:
    """Get metadata for a specific file"""
    metadata = load_metadata()
    return metadata.get(file_id)


@app.on_event("startup")
async def startup_event():
    """Initialize directories on startup"""
    ensure_directories()


@app.post("/api/files/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file and return metadata"""
    # Validate file type
    if not validate_file_type(file):
        raise HTTPException(
            status_code=400,
            detail="File type not allowed. Only images, PDFs, and text files are permitted."
        )
    
    # Read file content
    content = await file.read()
    
    # Check file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE / (1024*1024)}MB"
        )
    
    # Sanitize filename
    original_filename = sanitize_filename(file.filename or "unnamed_file")
    
    # Generate unique file ID and stored filename
    file_id = str(uuid.uuid4())
    ext = PathLib(original_filename).suffix
    stored_filename = f"{file_id}{ext}"
    stored_path = UPLOAD_DIR / stored_filename
    
    # Save file
    with open(stored_path, "wb") as f:
        f.write(content)
    
    # Determine MIME type
    mime_type, _ = mimetypes.guess_type(original_filename)
    if not mime_type:
        mime_type = file.content_type or "application/octet-stream"
    
    # Create metadata
    file_metadata = {
        "id": file_id,
        "original_filename": original_filename,
        "stored_filename": stored_filename,
        "file_size": len(content),
        "mime_type": mime_type,
        "upload_date": datetime.utcnow().isoformat()
    }
    
    # Save metadata
    metadata = load_metadata()
    metadata[file_id] = file_metadata
    save_metadata(metadata)
    
    return JSONResponse(content=file_metadata, status_code=201)


@app.get("/api/files/")
async def list_files():
    """List all uploaded files with metadata"""
    metadata = load_metadata()
    files_list = list(metadata.values())
    # Sort by upload date (newest first)
    files_list.sort(key=lambda x: x.get("upload_date", ""), reverse=True)
    return {"files": files_list, "count": len(files_list)}


@app.get("/api/files/{file_id}")
async def download_file(file_id: str = Path(..., description="File ID")):
    """Download a specific file"""
    file_metadata = get_file_metadata(file_id)
    if not file_metadata:
        raise HTTPException(status_code=404, detail="File not found")
    
    stored_path = UPLOAD_DIR / file_metadata["stored_filename"]
    if not stored_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return FileResponse(
        path=stored_path,
        filename=file_metadata["original_filename"],
        media_type=file_metadata["mime_type"]
    )


@app.get("/api/files/{file_id}/info")
async def get_file_info(file_id: str = Path(..., description="File ID")):
    """Get file metadata without downloading"""
    file_metadata = get_file_metadata(file_id)
    if not file_metadata:
        raise HTTPException(status_code=404, detail="File not found")
    
    return file_metadata


@app.delete("/api/files/{file_id}")
async def delete_file(file_id: str = Path(..., description="File ID")):
    """Delete a file and its metadata"""
    file_metadata = get_file_metadata(file_id)
    if not file_metadata:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Delete file from disk
    stored_path = UPLOAD_DIR / file_metadata["stored_filename"]
    if stored_path.exists():
        stored_path.unlink()
    
    # Remove from metadata
    metadata = load_metadata()
    if file_id in metadata:
        del metadata[file_id]
        save_metadata(metadata)
    
    return {"message": "File deleted successfully", "file_id": file_id}


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "File Upload & Management API", "version": "1.0.0"}

