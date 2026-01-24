from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import json
import uuid
import mimetypes
import re
from datetime import datetime, timezone
from pathlib import Path
import aiofiles

app = FastAPI(title="File Upload & Management System", version="1.0.0")

# CORS middleware for frontend communication
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
ALLOWED_MIME_TYPES = {
    # Images
    "image/jpeg", "image/jpg", "image/png", "image/gif", "image/bmp", "image/webp",
    # PDFs
    "application/pdf",
    # Text files
    "text/plain", "text/csv", "text/html", "text/css", "text/javascript",
    "application/json", "application/xml"
}

# Ensure upload directory exists
UPLOAD_DIR.mkdir(exist_ok=True)

# Pydantic models
class FileMetadata(BaseModel):
    id: str
    original_filename: str
    stored_filename: str
    file_size: int
    mime_type: str
    upload_date: str

class FileInfo(BaseModel):
    id: str
    original_filename: str
    file_size: int
    mime_type: str
    upload_date: str

# Utility functions
def load_metadata() -> dict:
    """Load file metadata from JSON file"""
    if METADATA_FILE.exists():
        try:
            with open(METADATA_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    return {}

def save_metadata(metadata: dict):
    """Save file metadata to JSON file"""
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f, indent=2)

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal and other security issues"""
    # Remove path separators and dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove path traversal sequences (..)
    filename = filename.replace('..', '_')
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    # Ensure filename is not empty
    if not filename:
        filename = "unnamed_file"
    return filename

def validate_file_type(content_type: str, filename: str) -> bool:
    """Validate file type based on MIME type and extension"""
    if content_type not in ALLOWED_MIME_TYPES:
        return False
    
    # Additional validation based on file extension
    _, ext = os.path.splitext(filename.lower())
    allowed_extensions = {
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp',  # Images
        '.pdf',  # PDF
        '.txt', '.csv', '.html', '.css', '.js', '.json', '.xml'  # Text files
    }
    
    return ext in allowed_extensions

# API Endpoints
@app.post("/api/files/upload", response_model=FileMetadata)
async def upload_file(file: UploadFile = File(...)):
    """Upload a file and return metadata"""
    
    # Validate file size
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB")
    
    # Validate file type
    if not validate_file_type(file.content_type, file.filename):
        raise HTTPException(
            status_code=400, 
            detail=f"File type not allowed. Allowed types: images, PDFs, text files"
        )
    
    # Generate unique file ID and sanitize filename
    file_id = str(uuid.uuid4())
    original_filename = sanitize_filename(file.filename)
    file_extension = os.path.splitext(original_filename)[1]
    stored_filename = f"{file_id}{file_extension}"
    
    # Save file to disk
    file_path = UPLOAD_DIR / stored_filename
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
            file_size = len(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Create metadata
    metadata = FileMetadata(
        id=file_id,
        original_filename=original_filename,
        stored_filename=stored_filename,
        file_size=file_size,
        mime_type=file.content_type,
        upload_date=datetime.now(timezone.utc).isoformat()
    )
    
    # Save metadata
    all_metadata = load_metadata()
    all_metadata[file_id] = metadata.model_dump()
    save_metadata(all_metadata)
    
    return metadata

@app.get("/api/files/", response_model=List[FileInfo])
async def list_files():
    """List all uploaded files with metadata"""
    metadata = load_metadata()
    files = []
    
    for file_id, file_data in metadata.items():
        files.append(FileInfo(
            id=file_id,
            original_filename=file_data["original_filename"],
            file_size=file_data["file_size"],
            mime_type=file_data["mime_type"],
            upload_date=file_data["upload_date"]
        ))
    
    return sorted(files, key=lambda x: x.upload_date, reverse=True)

@app.get("/api/files/{file_id}")
async def download_file(file_id: str):
    """Download a specific file"""
    metadata = load_metadata()
    
    if file_id not in metadata:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_data = metadata[file_id]
    file_path = UPLOAD_DIR / file_data["stored_filename"]
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return FileResponse(
        path=file_path,
        filename=file_data["original_filename"],
        media_type=file_data["mime_type"]
    )

@app.delete("/api/files/{file_id}")
async def delete_file(file_id: str):
    """Delete a file and its metadata"""
    metadata = load_metadata()
    
    if file_id not in metadata:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_data = metadata[file_id]
    file_path = UPLOAD_DIR / file_data["stored_filename"]
    
    # Delete file from disk
    if file_path.exists():
        try:
            file_path.unlink()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")
    
    # Remove metadata
    del metadata[file_id]
    save_metadata(metadata)
    
    return {"message": "File deleted successfully"}

@app.get("/api/files/{file_id}/info", response_model=FileInfo)
async def get_file_info(file_id: str):
    """Get file metadata without downloading"""
    metadata = load_metadata()
    
    if file_id not in metadata:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_data = metadata[file_id]
    return FileInfo(
        id=file_id,
        original_filename=file_data["original_filename"],
        file_size=file_data["file_size"],
        mime_type=file_data["mime_type"],
        upload_date=file_data["upload_date"]
    )

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "File Upload & Management System API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
