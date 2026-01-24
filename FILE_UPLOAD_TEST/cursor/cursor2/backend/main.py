from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import uuid
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional
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
UPLOAD_DIR = Path("uploads")
METADATA_FILE = Path("metadata.json")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes

# Allowed file types (MIME types)
ALLOWED_MIME_TYPES = {
    "image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp",
    "application/pdf",
    "text/plain", "text/html", "text/css", "text/javascript", "text/csv"
}

# Allowed file extensions (for additional validation)
ALLOWED_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp",
    ".pdf",
    ".txt", ".html", ".css", ".js", ".csv"
}

# Initialize directories and metadata file
UPLOAD_DIR.mkdir(exist_ok=True)
if not METADATA_FILE.exists():
    with open(METADATA_FILE, "w") as f:
        json.dump({}, f)


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal and remove dangerous characters."""
    # Remove path components
    filename = os.path.basename(filename)
    # Remove or replace dangerous characters
    filename = re.sub(r'[<>:"|?*\x00-\x1f]', '_', filename)
    # Limit length
    filename = filename[:255]
    return filename


def is_allowed_file(filename: str, mime_type: Optional[str] = None) -> bool:
    """Check if file type is allowed."""
    # Check extension
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False
    
    # Check MIME type if provided
    if mime_type:
        # Handle common MIME type variations
        mime_type = mime_type.lower().split(';')[0].strip()
        if mime_type not in ALLOWED_MIME_TYPES:
            # Fallback: check if extension matches known MIME types
            mime_guess = mimetypes.guess_type(filename)[0]
            if mime_guess and mime_guess.lower() not in ALLOWED_MIME_TYPES:
                return False
    
    return True


def load_metadata() -> dict:
    """Load metadata from JSON file."""
    try:
        with open(METADATA_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_metadata(metadata: dict):
    """Save metadata to JSON file."""
    with open(METADATA_FILE, "w") as f:
        json.dump(metadata, f, indent=2, default=str)


@app.post("/api/files/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file and store metadata."""
    # Validate file size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE / (1024*1024)}MB"
        )
    
    # Validate file type
    if not is_allowed_file(file.filename, file.content_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type not allowed. Only images, PDFs, and text files are permitted."
        )
    
    # Sanitize filename
    sanitized_filename = sanitize_filename(file.filename)
    
    # Generate unique file ID and stored filename
    file_id = str(uuid.uuid4())
    file_ext = Path(sanitized_filename).suffix
    stored_filename = f"{file_id}{file_ext}"
    file_path = UPLOAD_DIR / stored_filename
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Create metadata
    metadata_entry = {
        "id": file_id,
        "original_filename": sanitized_filename,
        "stored_filename": stored_filename,
        "file_size": len(contents),
        "mime_type": file.content_type or mimetypes.guess_type(sanitized_filename)[0] or "application/octet-stream",
        "upload_date": datetime.now().isoformat()
    }
    
    # Save metadata
    all_metadata = load_metadata()
    all_metadata[file_id] = metadata_entry
    save_metadata(all_metadata)
    
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=metadata_entry
    )


@app.get("/api/files/")
async def list_files():
    """List all uploaded files with metadata."""
    metadata = load_metadata()
    return {"files": list(metadata.values())}


@app.get("/api/files/{file_id}")
async def download_file(file_id: str):
    """Download a specific file."""
    metadata = load_metadata()
    
    if file_id not in metadata:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    file_info = metadata[file_id]
    file_path = UPLOAD_DIR / file_info["stored_filename"]
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on disk"
        )
    
    return FileResponse(
        path=file_path,
        filename=file_info["original_filename"],
        media_type=file_info["mime_type"]
    )


@app.get("/api/files/{file_id}/info")
async def get_file_info(file_id: str):
    """Get file metadata without downloading."""
    metadata = load_metadata()
    
    if file_id not in metadata:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return metadata[file_id]


@app.delete("/api/files/{file_id}")
async def delete_file(file_id: str):
    """Delete a file and its metadata."""
    metadata = load_metadata()
    
    if file_id not in metadata:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    file_info = metadata[file_id]
    file_path = UPLOAD_DIR / file_info["stored_filename"]
    
    # Delete file from filesystem
    if file_path.exists():
        file_path.unlink()
    
    # Remove from metadata
    del metadata[file_id]
    save_metadata(metadata)
    
    return {"message": "File deleted successfully", "file_id": file_id}


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "File Upload & Management API", "version": "1.0.0"}

