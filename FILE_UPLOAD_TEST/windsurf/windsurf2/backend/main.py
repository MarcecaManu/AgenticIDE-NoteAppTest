from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import uuid
import mimetypes
from datetime import datetime, timezone
from pathlib import Path
import re
from typing import List, Dict, Any
import shutil

app = FastAPI(title="File Upload & Management API", version="1.0.0")

# Enable CORS for frontend communication
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
    "image/jpeg", "image/jpg", "image/png", "image/gif", "image/bmp", 
    "image/webp", "image/svg+xml", "image/tiff",
    # PDFs
    "application/pdf",
    # Text files
    "text/plain", "text/csv", "text/html", "text/css", "text/javascript",
    "application/json", "application/xml", "text/xml"
}

# Create upload directory if it doesn't exist
UPLOAD_DIR.mkdir(exist_ok=True)

def load_metadata() -> Dict[str, Any]:
    """Load file metadata from JSON file."""
    if METADATA_FILE.exists():
        try:
            with open(METADATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}

def save_metadata(metadata: Dict[str, Any]) -> None:
    """Save file metadata to JSON file."""
    try:
        with open(METADATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    except IOError as e:
        raise HTTPException(status_code=500, detail=f"Failed to save metadata: {str(e)}")

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal and other security issues."""
    # Remove path components
    filename = os.path.basename(filename)
    # Remove or replace dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove control characters
    filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    # Ensure it's not empty
    if not filename or filename.startswith('.'):
        filename = f"file_{uuid.uuid4().hex[:8]}" + (os.path.splitext(filename)[1] if filename else ".txt")
    return filename

def validate_file_type(file: UploadFile) -> bool:
    """Validate file type based on MIME type and extension."""
    # Check MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        return False
    
    # Double-check with file extension
    if file.filename:
        guessed_type, _ = mimetypes.guess_type(file.filename)
        if guessed_type and guessed_type not in ALLOWED_MIME_TYPES:
            return False
    
    return True

@app.post("/api/files/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file and return file metadata."""
    # Validate file size
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB")
    
    # Reset file pointer for validation
    await file.seek(0)
    
    # Validate file type
    if not validate_file_type(file):
        raise HTTPException(
            status_code=400, 
            detail=f"File type not allowed. Allowed types: images, PDFs, text files"
        )
    
    # Generate unique file ID and sanitize filename
    file_id = str(uuid.uuid4())
    original_filename = file.filename or "unknown"
    sanitized_filename = sanitize_filename(original_filename)
    stored_filename = f"{file_id}_{sanitized_filename}"
    
    # Save file to disk
    file_path = UPLOAD_DIR / stored_filename
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
    except IOError as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Create metadata
    metadata = {
        "id": file_id,
        "original_filename": original_filename,
        "stored_filename": stored_filename,
        "file_size": len(file_content),
        "mime_type": file.content_type,
        "upload_date": datetime.now(timezone.utc).isoformat()
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
    return {"files": list(metadata.values())}

@app.get("/api/files/{file_id}")
async def download_file(file_id: str):
    """Download a specific file."""
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

@app.delete("/api/files/{file_id}")
async def delete_file(file_id: str):
    """Delete a file and its metadata."""
    metadata = load_metadata()
    
    if file_id not in metadata:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_info = metadata[file_id]
    file_path = UPLOAD_DIR / file_info["stored_filename"]
    
    # Delete file from disk if it exists
    if file_path.exists():
        try:
            file_path.unlink()
        except OSError as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")
    
    # Remove from metadata
    del metadata[file_id]
    save_metadata(metadata)
    
    return {"message": "File deleted successfully", "file_id": file_id}

@app.get("/api/files/{file_id}/info")
async def get_file_info(file_id: str):
    """Get file metadata without downloading."""
    metadata = load_metadata()
    
    if file_id not in metadata:
        raise HTTPException(status_code=404, detail="File not found")
    
    return metadata[file_id]

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "File Upload & Management API",
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
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
