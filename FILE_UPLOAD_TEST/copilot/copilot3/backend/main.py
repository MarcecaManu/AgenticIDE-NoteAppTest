import os
import json
import uuid
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import re

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
UPLOAD_DIR = Path("uploads")
METADATA_FILE = Path("file_metadata.json")

# Allowed MIME types and extensions for security
ALLOWED_MIME_TYPES = {
    # Images
    'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml',
    # PDFs
    'application/pdf',
    # Text files
    'text/plain', 'text/csv', 'text/html', 'text/css', 'text/javascript',
    'application/json', 'application/xml', 'text/xml'
}

# Explicitly blocked extensions (even if MIME type might be allowed)
BLOCKED_EXTENSIONS = {
    '.exe', '.bat', '.cmd', '.com', '.scr', '.vbs', '.ps1', '.sh',
    '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2',
    '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.dll', '.so', '.dylib', '.msi', '.deb', '.rpm'
}

app = FastAPI(title="File Upload & Management System", version="1.0.0")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class FileMetadata(BaseModel):
    id: str
    original_filename: str
    stored_filename: str
    file_size: int
    mime_type: str
    upload_date: str

class FileListResponse(BaseModel):
    files: List[FileMetadata]

# Utility functions
def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal attacks."""
    # Remove any directory path components
    filename = os.path.basename(filename)
    # Remove or replace dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove any leading dots or spaces
    filename = filename.lstrip('. ')
    # Ensure filename is not empty
    if not filename:
        filename = "unnamed_file"
    return filename

def load_metadata() -> dict:
    """Load file metadata from JSON file."""
    if METADATA_FILE.exists():
        try:
            with open(METADATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}

def save_metadata(metadata: dict):
    """Save file metadata to JSON file."""
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

def validate_file_type(file: UploadFile) -> bool:
    """Validate if file type is allowed."""
    if not file.filename:
        return False
    
    # Check for blocked extensions first
    file_extension = Path(file.filename).suffix.lower()
    if file_extension in BLOCKED_EXTENSIONS:
        return False
    
    # Check MIME type
    if file.content_type and file.content_type in ALLOWED_MIME_TYPES:
        return True
    
    # Fallback: guess MIME type from filename
    guessed_type, _ = mimetypes.guess_type(file.filename)
    if guessed_type and guessed_type in ALLOWED_MIME_TYPES:
        # Double-check that the extension is safe even if MIME type is allowed
        if file_extension in BLOCKED_EXTENSIONS:
            return False
        return True
    
    return False

# Ensure upload directory exists
UPLOAD_DIR.mkdir(exist_ok=True)

# API Endpoints
@app.post("/api/files/upload", response_model=FileMetadata)
async def upload_file(file: UploadFile = File(...)):
    """Upload a file and return file metadata."""
    
    # Validate file size
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB")
    
    # Validate file type
    if not validate_file_type(file):
        allowed_types = ", ".join(sorted(ALLOWED_MIME_TYPES))
        raise HTTPException(status_code=400, detail=f"File type not allowed. Allowed types: {allowed_types}")
    
    # Generate unique ID and sanitize filename
    file_id = str(uuid.uuid4())
    original_filename = file.filename or "unnamed_file"
    sanitized_name = sanitize_filename(original_filename)
    
    # Create unique stored filename to avoid conflicts
    file_extension = Path(sanitized_name).suffix
    stored_filename = f"{file_id}{file_extension}"
    file_path = UPLOAD_DIR / stored_filename
    
    # Read file content and validate size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB")
    
    # Save file
    try:
        with open(file_path, "wb") as f:
            f.write(content)
    except IOError as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Create metadata
    metadata_entry = FileMetadata(
        id=file_id,
        original_filename=original_filename,
        stored_filename=stored_filename,
        file_size=len(content),
        mime_type=file.content_type or mimetypes.guess_type(original_filename)[0] or "application/octet-stream",
        upload_date=datetime.now().isoformat()
    )
    
    # Save metadata
    metadata_db = load_metadata()
    metadata_db[file_id] = metadata_entry.model_dump()
    save_metadata(metadata_db)
    
    return metadata_entry

@app.get("/api/files/", response_model=FileListResponse)
async def list_files():
    """List all uploaded files with metadata."""
    metadata_db = load_metadata()
    files = [FileMetadata(**data) for data in metadata_db.values()]
    # Sort by upload date, newest first
    files.sort(key=lambda x: x.upload_date, reverse=True)
    return FileListResponse(files=files)

@app.get("/api/files/{file_id}")
async def download_file(file_id: str):
    """Download a specific file."""
    metadata_db = load_metadata()
    
    if file_id not in metadata_db:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_metadata = metadata_db[file_id]
    file_path = UPLOAD_DIR / file_metadata["stored_filename"]
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return FileResponse(
        path=str(file_path),
        filename=file_metadata["original_filename"],
        media_type=file_metadata["mime_type"]
    )

@app.delete("/api/files/{file_id}")
async def delete_file(file_id: str):
    """Delete a file and its metadata."""
    metadata_db = load_metadata()
    
    if file_id not in metadata_db:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_metadata = metadata_db[file_id]
    file_path = UPLOAD_DIR / file_metadata["stored_filename"]
    
    # Delete file from disk if it exists
    if file_path.exists():
        try:
            file_path.unlink()
        except OSError as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")
    
    # Remove from metadata
    del metadata_db[file_id]
    save_metadata(metadata_db)
    
    return {"message": "File deleted successfully"}

@app.get("/api/files/{file_id}/info", response_model=FileMetadata)
async def get_file_info(file_id: str):
    """Get file metadata without downloading."""
    metadata_db = load_metadata()
    
    if file_id not in metadata_db:
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileMetadata(**metadata_db[file_id])

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "File Upload & Management System API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "POST /api/files/upload",
            "list": "GET /api/files/",
            "download": "GET /api/files/{file_id}",
            "delete": "DELETE /api/files/{file_id}",
            "info": "GET /api/files/{file_id}/info"
        }
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)