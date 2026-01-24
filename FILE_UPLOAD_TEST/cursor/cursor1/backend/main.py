from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json
import uuid
import shutil
from datetime import datetime
from typing import List, Optional
import mimetypes
import os

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
# Use absolute paths based on this file's location
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
METADATA_FILE = BASE_DIR / "metadata.json"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Allowed file types
ALLOWED_EXTENSIONS = {
    # Images
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg',
    # PDFs
    '.pdf',
    # Text files
    '.txt', '.md', '.csv', '.json', '.xml', '.html', '.css', '.js', '.log'
}

ALLOWED_MIME_TYPES = {
    'image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp', 'image/svg+xml',
    'application/pdf',
    'text/plain', 'text/markdown', 'text/csv', 'application/json', 'text/xml',
    'text/html', 'text/css', 'application/javascript', 'text/x-log'
}


def ensure_directories():
    """Create necessary directories if they don't exist"""
    UPLOAD_DIR.mkdir(exist_ok=True)


def load_metadata() -> dict:
    """Load metadata from JSON file"""
    if METADATA_FILE.exists():
        try:
            with open(METADATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_metadata(metadata: dict):
    """Save metadata to JSON file"""
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal and other security issues"""
    # Remove path components
    filename = os.path.basename(filename)
    # Remove or replace dangerous characters
    dangerous_chars = ['..', '/', '\\', '\x00']
    for char in dangerous_chars:
        filename = filename.replace(char, '')
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    # If empty after sanitization, use a default name
    if not filename:
        filename = "file"
    return filename


def is_allowed_file(filename: str, content_type: Optional[str] = None) -> bool:
    """Check if file type is allowed"""
    # Check extension
    ext = Path(filename).suffix.lower()
    has_valid_extension = ext in ALLOWED_EXTENSIONS
    
    # Check MIME type if provided
    has_valid_mime = False
    if content_type:
        # Handle MIME type variations
        base_type = content_type.split(';')[0].strip()
        has_valid_mime = base_type in ALLOWED_MIME_TYPES
    
    # Allow if either extension or MIME type is valid
    # (MIME type check handles cases where sanitization removed extension)
    return has_valid_extension or has_valid_mime


@app.on_event("startup")
async def startup_event():
    """Initialize directories on startup"""
    ensure_directories()


@app.post("/api/files/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file and return metadata"""
    # Sanitize filename first to prevent path traversal attacks
    sanitized_filename = sanitize_filename(file.filename)
    
    # Validate file type using sanitized filename
    if not is_allowed_file(sanitized_filename, file.content_type):
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
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE / (1024*1024):.1f}MB"
        )
    
    # Generate unique ID and use sanitized filename
    file_id = str(uuid.uuid4())
    original_filename = sanitized_filename
    stored_filename = f"{file_id}_{original_filename}"
    
    # Save file
    file_path = UPLOAD_DIR / stored_filename
    with open(file_path, 'wb') as f:
        f.write(content)
    
    # Create metadata
    metadata = {
        "id": file_id,
        "original_filename": original_filename,
        "stored_filename": stored_filename,
        "file_size": len(content),
        "mime_type": file.content_type or mimetypes.guess_type(original_filename)[0] or "application/octet-stream",
        "upload_date": datetime.utcnow().isoformat()
    }
    
    # Save metadata
    all_metadata = load_metadata()
    all_metadata[file_id] = metadata
    save_metadata(all_metadata)
    
    return metadata


@app.get("/api/files/")
async def list_files():
    """List all uploaded files with metadata"""
    metadata = load_metadata()
    return list(metadata.values())


@app.get("/api/files/{file_id}")
async def download_file(file_id: str):
    """Download a specific file"""
    metadata = load_metadata()
    
    if file_id not in metadata:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_info = metadata[file_id]
    file_path = UPLOAD_DIR / file_info["stored_filename"]
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return FileResponse(
        path=file_path,
        filename=file_info["original_filename"],
        media_type=file_info["mime_type"]
    )


@app.get("/api/files/{file_id}/info")
async def get_file_info(file_id: str):
    """Get file metadata without downloading"""
    metadata = load_metadata()
    
    if file_id not in metadata:
        raise HTTPException(status_code=404, detail="File not found")
    
    return metadata[file_id]


@app.delete("/api/files/{file_id}")
async def delete_file(file_id: str):
    """Delete a file and its metadata"""
    metadata = load_metadata()
    
    if file_id not in metadata:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_info = metadata[file_id]
    file_path = UPLOAD_DIR / file_info["stored_filename"]
    
    # Delete file from disk
    if file_path.exists():
        file_path.unlink()
    
    # Remove from metadata
    del metadata[file_id]
    save_metadata(metadata)
    
    return {"message": "File deleted successfully", "file_id": file_id}

