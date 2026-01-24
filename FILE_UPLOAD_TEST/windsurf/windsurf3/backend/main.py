from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import uuid
import shutil
from datetime import datetime, timezone
from pathlib import Path
import mimetypes
import re
from typing import List, Dict, Any

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
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.pdf', '.txt', '.md', '.csv'}
ALLOWED_MIME_TYPES = {
    'image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp', 'image/svg+xml',
    'application/pdf', 'text/plain', 'text/markdown', 'text/csv'
}

# Ensure upload directory exists
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
    if not filename:
        return "unnamed_file"
    
    # Remove path components
    filename = os.path.basename(filename)
    # Remove dangerous characters
    filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', filename)
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    # Ensure it's not empty or just dots
    if not filename or filename.strip('.') == '':
        filename = "unnamed_file"
    return filename

def validate_file_type(file: UploadFile) -> bool:
    """Validate file type based on extension and MIME type."""
    if not file.filename:
        return False
        
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        return False
    
    # Check MIME type
    if file.content_type and file.content_type not in ALLOWED_MIME_TYPES:
        return False
    
    return True

@app.post("/api/files/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file and return its metadata."""
    # Check if filename is provided
    if not file.filename:
        raise HTTPException(status_code=422, detail="No filename provided")
    
    # Validate file size
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB")
    
    # Validate file type
    if not validate_file_type(file):
        raise HTTPException(status_code=400, detail="File type not allowed. Only images, PDFs, and text files are permitted.")
    
    # Generate unique file ID and sanitize filename
    file_id = str(uuid.uuid4())
    original_filename = file.filename
    sanitized_filename = sanitize_filename(original_filename)
    
    # Create stored filename with unique ID
    file_ext = Path(sanitized_filename).suffix
    stored_filename = f"{file_id}{file_ext}"
    file_path = UPLOAD_DIR / stored_filename
    
    try:
        # Save file to disk
        with open(file_path, "wb") as buffer:
            content = await file.read()
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(status_code=413, detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB")
            buffer.write(content)
        
        # Get file size and MIME type
        file_size = len(content)
        mime_type = file.content_type or mimetypes.guess_type(sanitized_filename)[0] or "application/octet-stream"
        
        # Create metadata
        metadata = load_metadata()
        file_metadata = {
            "id": file_id,
            "original_filename": original_filename,
            "stored_filename": stored_filename,
            "file_size": file_size,
            "mime_type": mime_type,
            "upload_date": datetime.now(timezone.utc).isoformat()
        }
        
        metadata[file_id] = file_metadata
        save_metadata(metadata)
        
        return file_metadata
        
    except Exception as e:
        # Clean up file if it was created
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

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
    
    # Remove file from disk if it exists
    if file_path.exists():
        try:
            file_path.unlink()
        except OSError as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")
    
    # Remove metadata
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
