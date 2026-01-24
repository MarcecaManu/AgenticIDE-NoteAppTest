from fastapi import FastAPI, UploadFile, File, HTTPException, Path
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import json
import uuid
import shutil
from datetime import datetime, timezone
from pathlib import Path as PathLib
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
UPLOAD_DIR = PathLib("uploads")
METADATA_FILE = PathLib("metadata.json")
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
    """Sanitize filename to prevent path traversal and other attacks"""
    # Remove path components
    filename = os.path.basename(filename)
    # Remove any remaining path separators
    filename = filename.replace("/", "").replace("\\", "")
    # Remove or replace dangerous characters
    filename = re.sub(r'[<>:"|?*]', "_", filename)
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:250] + ext
    return filename


def is_allowed_file(filename: str, content_type: Optional[str] = None) -> bool:
    """Check if file type is allowed"""
    # Check extension
    ext = os.path.splitext(filename)[1].lower()
    has_valid_extension = ext in ALLOWED_EXTENSIONS
    
    # Check MIME type if provided
    has_valid_mime_type = False
    if content_type:
        # Handle MIME type variations
        base_type = content_type.split(";")[0].strip().lower()
        if base_type in ALLOWED_MIME_TYPES:
            has_valid_mime_type = True
        else:
            # Fallback: check if extension matches common MIME types
            mime_type, _ = mimetypes.guess_type(filename)
            if mime_type and mime_type.lower() in ALLOWED_MIME_TYPES:
                has_valid_mime_type = True
    
    # Accept if either extension or MIME type is valid
    # This handles cases where sanitization might remove the extension
    return has_valid_extension or has_valid_mime_type


@app.on_event("startup")
async def startup_event():
    """Initialize directories on startup"""
    ensure_directories()


@app.post("/api/files/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file and store metadata"""
    try:
        # Validate file size
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE / (1024*1024)}MB"
            )
        
        # Sanitize filename first to prevent path traversal
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="Filename is required"
            )
        
        original_filename = sanitize_filename(file.filename)
        
        # Ensure filename is not empty after sanitization
        if not original_filename or not original_filename.strip():
            raise HTTPException(
                status_code=400,
                detail="Invalid filename after sanitization"
            )
        
        # Validate file type using sanitized filename
        if not is_allowed_file(original_filename, file.content_type):
            raise HTTPException(
                status_code=400,
                detail="File type not allowed. Only images, PDFs, and text files are permitted."
            )
        
        # Generate unique file ID and stored filename
        file_id = str(uuid.uuid4())
        ext = os.path.splitext(original_filename)[1]
        stored_filename = f"{file_id}{ext}"
        file_path = UPLOAD_DIR / stored_filename
        
        # Detect MIME type
        mime_type, _ = mimetypes.guess_type(original_filename)
        if not mime_type:
            mime_type = file.content_type or "application/octet-stream"
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Create metadata
        metadata = {
            "id": file_id,
            "original_filename": original_filename,
            "stored_filename": stored_filename,
            "file_size": len(contents),
            "mime_type": mime_type,
            "upload_date": datetime.now(timezone.utc).isoformat()
        }
        
        # Save metadata
        all_metadata = load_metadata()
        all_metadata[file_id] = metadata
        save_metadata(all_metadata)
        
        return JSONResponse(content=metadata, status_code=201)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


@app.get("/api/files/")
async def list_files():
    """List all uploaded files with metadata"""
    try:
        metadata = load_metadata()
        # Convert dict to list of metadata objects
        files_list = list(metadata.values())
        # Sort by upload date (newest first)
        files_list.sort(key=lambda x: x.get("upload_date", ""), reverse=True)
        return {"files": files_list, "count": len(files_list)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")


@app.get("/api/files/{file_id}")
async def download_file(file_id: str = Path(..., description="File ID")):
    """Download a specific file"""
    try:
        metadata = load_metadata()
        
        if file_id not in metadata:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_info = metadata[file_id]
        file_path = UPLOAD_DIR / file_info["stored_filename"]
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found on disk")
        
        # Prevent path traversal
        if not file_path.resolve().is_relative_to(UPLOAD_DIR.resolve()):
            raise HTTPException(status_code=403, detail="Invalid file path")
        
        return FileResponse(
            path=str(file_path),
            filename=file_info["original_filename"],
            media_type=file_info["mime_type"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")


@app.get("/api/files/{file_id}/info")
async def get_file_info(file_id: str = Path(..., description="File ID")):
    """Get file metadata without downloading"""
    try:
        metadata = load_metadata()
        
        if file_id not in metadata:
            raise HTTPException(status_code=404, detail="File not found")
        
        return metadata[file_id]
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving file info: {str(e)}")


@app.delete("/api/files/{file_id}")
async def delete_file(file_id: str = Path(..., description="File ID")):
    """Delete a file and its metadata"""
    try:
        metadata = load_metadata()
        
        if file_id not in metadata:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_info = metadata[file_id]
        file_path = UPLOAD_DIR / file_info["stored_filename"]
        
        # Delete file from filesystem
        if file_path.exists():
            # Prevent path traversal
            if not file_path.resolve().is_relative_to(UPLOAD_DIR.resolve()):
                raise HTTPException(status_code=403, detail="Invalid file path")
            file_path.unlink()
        
        # Remove metadata
        del metadata[file_id]
        save_metadata(metadata)
        
        return {"message": "File deleted successfully", "file_id": file_id}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

