import os
import json
import uuid
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import mimetypes

app = FastAPI(title="File Upload & Management System")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
UPLOAD_DIR = Path("uploads")
METADATA_FILE = Path("file_metadata.json")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {
    # Images
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg',
    # PDFs
    '.pdf',
    # Text files
    '.txt', '.md', '.csv', '.json', '.xml', '.html', '.css', '.js', '.py', '.java', '.cpp', '.c'
}
ALLOWED_MIME_TYPES = {
    # Images
    'image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp', 'image/svg+xml',
    # PDFs
    'application/pdf',
    # Text files
    'text/plain', 'text/markdown', 'text/csv', 'application/json', 'text/xml', 'text/html',
    'text/css', 'text/javascript', 'text/x-python-script', 'text/x-java-source', 
    'text/x-c', 'text/x-c++src'
}

# Ensure upload directory exists
UPLOAD_DIR.mkdir(exist_ok=True)

def load_metadata() -> dict:
    """Load file metadata from JSON file."""
    if METADATA_FILE.exists():
        try:
            with open(METADATA_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    return {}

def save_metadata(metadata: dict):
    """Save file metadata to JSON file."""
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f, indent=2)

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal attacks."""
    # Remove any path separators and dangerous characters
    safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-"
    sanitized = "".join(c for c in filename if c in safe_chars)
    
    # Ensure filename is not empty and doesn't start with dot
    if not sanitized or sanitized.startswith('.'):
        sanitized = "file_" + sanitized
    
    # Limit length
    if len(sanitized) > 255:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:255-len(ext)] + ext
    
    return sanitized

def validate_file_type(filename: str, content_type: str) -> bool:
    """Validate file type based on extension and MIME type."""
    file_ext = Path(filename).suffix.lower()
    
    # Check extension
    if file_ext not in ALLOWED_EXTENSIONS:
        return False
    
    # Check MIME type
    if content_type not in ALLOWED_MIME_TYPES:
        # Also check if mimetypes can guess a valid type
        guessed_type, _ = mimetypes.guess_type(filename)
        if guessed_type not in ALLOWED_MIME_TYPES:
            return False
    
    return True

@app.post("/api/files/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file and return file metadata."""
    
    # Validate file size
    if not file.size or file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE / (1024*1024):.1f}MB"
        )
    
    # Validate file type
    if not validate_file_type(file.filename, file.content_type):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="File type not allowed. Only images, PDFs, and text files are supported."
        )
    
    # Generate unique file ID and sanitize filename
    file_id = str(uuid.uuid4())
    original_filename = file.filename
    sanitized_filename = sanitize_filename(original_filename)
    stored_filename = f"{file_id}_{sanitized_filename}"
    
    # Save file to disk
    file_path = UPLOAD_DIR / stored_filename
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Create metadata
    metadata = {
        "id": file_id,
        "original_filename": original_filename,
        "stored_filename": stored_filename,
        "file_size": file.size,
        "mime_type": file.content_type,
        "upload_date": datetime.now().isoformat()
    }
    
    # Load existing metadata and add new file
    all_metadata = load_metadata()
    all_metadata[file_id] = metadata
    save_metadata(all_metadata)
    
    return metadata

@app.get("/api/files/")
async def list_files():
    """List all uploaded files with metadata."""
    metadata = load_metadata()
    return list(metadata.values())

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
    
    # Delete file from disk
    if file_path.exists():
        try:
            file_path.unlink()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete file: {str(e)}"
            )
    
    # Remove from metadata
    del metadata[file_id]
    save_metadata(metadata)
    
    return {"message": "File deleted successfully"}

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

# Serve frontend static files
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)