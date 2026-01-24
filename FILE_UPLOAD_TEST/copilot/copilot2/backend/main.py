import os
import json
import uuid
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import aiofiles

# Configuration
UPLOAD_DIR = Path("uploads")
METADATA_FILE = Path("file_metadata.json")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_MIME_TYPES = {
    'image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp',
    'application/pdf',
    'text/plain', 'text/csv', 'text/html', 'text/css', 'text/javascript',
    'application/json', 'application/xml'
}
ALLOWED_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp',
    '.pdf',
    '.txt', '.csv', '.html', '.css', '.js', '.json', '.xml'
}

# Create upload directory if it doesn't exist
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(title="File Upload & Management API", version="1.0.0")

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

def load_metadata() -> List[FileMetadata]:
    """Load file metadata from JSON file"""
    if not METADATA_FILE.exists():
        return []
    
    try:
        with open(METADATA_FILE, 'r') as f:
            data = json.load(f)
            return [FileMetadata(**item) for item in data]
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_metadata(metadata_list: List[FileMetadata]):
    """Save file metadata to JSON file"""
    with open(METADATA_FILE, 'w') as f:
        json.dump([item.model_dump() for item in metadata_list], f, indent=2)

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal attacks"""
    # Remove directory paths and dangerous characters
    safe_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_")
    sanitized = "".join(c for c in filename if c in safe_chars)
    
    # Remove leading dots to prevent hidden files
    sanitized = sanitized.lstrip('.')
    
    # Ensure filename is not empty
    if not sanitized:
        sanitized = "unnamed_file"
    
    return sanitized

def validate_file_type(filename: str, content_type: str) -> bool:
    """Validate file type based on extension and MIME type"""
    file_ext = Path(filename).suffix.lower()
    
    # Check extension
    if file_ext not in ALLOWED_EXTENSIONS:
        return False
    
    # Check MIME type
    if content_type not in ALLOWED_MIME_TYPES:
        return False
    
    return True

@app.post("/api/files/upload", response_model=FileMetadata)
async def upload_file(file: UploadFile = File(...)):
    """Upload a file and return its metadata"""
    
    # Validate file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File size exceeds 10MB limit")
    
    # Reset file pointer
    await file.seek(0)
    
    # Validate file type
    if not validate_file_type(file.filename, file.content_type):
        raise HTTPException(
            status_code=400, 
            detail="Invalid file type. Only images, PDFs, and text files are allowed"
        )
    
    # Generate unique file ID and stored filename
    file_id = str(uuid.uuid4())
    original_filename = file.filename or "unnamed_file"
    sanitized_name = sanitize_filename(original_filename)
    
    # Create unique stored filename with file ID
    file_ext = Path(sanitized_name).suffix
    stored_filename = f"{file_id}{file_ext}"
    file_path = UPLOAD_DIR / stored_filename
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)
    
    # Create metadata
    metadata = FileMetadata(
        id=file_id,
        original_filename=original_filename,
        stored_filename=stored_filename,
        file_size=len(content),
        mime_type=file.content_type,
        upload_date=datetime.now().isoformat()
    )
    
    # Load existing metadata, add new file, and save
    metadata_list = load_metadata()
    metadata_list.append(metadata)
    save_metadata(metadata_list)
    
    return metadata

@app.get("/api/files/", response_model=List[FileInfo])
async def list_files():
    """List all uploaded files with metadata"""
    metadata_list = load_metadata()
    return [
        FileInfo(
            id=item.id,
            original_filename=item.original_filename,
            file_size=item.file_size,
            mime_type=item.mime_type,
            upload_date=item.upload_date
        )
        for item in metadata_list
    ]

@app.get("/api/files/{file_id}")
async def download_file(file_id: str):
    """Download a specific file"""
    metadata_list = load_metadata()
    
    # Find file metadata
    file_metadata = None
    for item in metadata_list:
        if item.id == file_id:
            file_metadata = item
            break
    
    if not file_metadata:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = UPLOAD_DIR / file_metadata.stored_filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return FileResponse(
        path=file_path,
        filename=file_metadata.original_filename,
        media_type=file_metadata.mime_type
    )

@app.delete("/api/files/{file_id}")
async def delete_file(file_id: str):
    """Delete a file and its metadata"""
    metadata_list = load_metadata()
    
    # Find and remove file metadata
    file_metadata = None
    updated_metadata = []
    for item in metadata_list:
        if item.id == file_id:
            file_metadata = item
        else:
            updated_metadata.append(item)
    
    if not file_metadata:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Delete file from disk
    file_path = UPLOAD_DIR / file_metadata.stored_filename
    if file_path.exists():
        file_path.unlink()
    
    # Save updated metadata
    save_metadata(updated_metadata)
    
    return {"message": "File deleted successfully"}

@app.get("/api/files/{file_id}/info", response_model=FileInfo)
async def get_file_info(file_id: str):
    """Get file metadata without downloading"""
    metadata_list = load_metadata()
    
    # Find file metadata
    for item in metadata_list:
        if item.id == file_id:
            return FileInfo(
                id=item.id,
                original_filename=item.original_filename,
                file_size=item.file_size,
                mime_type=item.mime_type,
                upload_date=item.upload_date
            )
    
    raise HTTPException(status_code=404, detail="File not found")

@app.get("/")
async def root():
    """API health check"""
    return {"message": "File Upload & Management API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)