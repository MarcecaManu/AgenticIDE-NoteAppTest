# File Upload & Management System

A full-stack file upload and management system built with FastAPI (backend) and vanilla HTML/JavaScript (frontend).

## Features

- ✅ Upload files via drag-and-drop or file picker
- ✅ View list of uploaded files with metadata
- ✅ Download files
- ✅ Delete files
- ✅ File type validation (images, PDFs, text files only)
- ✅ File size limit (10MB)
- ✅ Filename sanitization
- ✅ Path traversal attack prevention
- ✅ Persistent storage (filesystem + JSON metadata)

## Project Structure

```
.
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── uploads/             # Uploaded files storage (created automatically)
│   └── metadata.json        # File metadata storage (created automatically)
├── frontend/
│   ├── index.html           # Main HTML page
│   └── app.js               # Frontend JavaScript
├── tests/
│   ├── test_file_upload.py  # Automated tests
│   └── requirements.txt     # Test dependencies
└── README.md                # This file
```

## Installation

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Frontend Setup

The frontend requires no installation - it's plain HTML and JavaScript. Just open `frontend/index.html` in a browser or serve it through a web server.

### Test Setup

1. Install test dependencies:
```bash
pip install -r tests/requirements.txt
```

## Running the Application

### Start the Backend Server

From the project root:
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Or from the project root:
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Access the Frontend

1. **Option 1: Direct file access**
   - Open `frontend/index.html` in your browser
   - Note: CORS may need to be configured if accessing directly

2. **Option 2: Serve via HTTP server** (recommended)
   ```bash
   # Using Python
   cd frontend
   python -m http.server 8080
   ```
   Then open `http://localhost:8080` in your browser

3. **Option 3: Serve via FastAPI**
   - The backend can be configured to serve static files (see FastAPI StaticFiles)

## API Endpoints

All endpoints are prefixed with `/api/files/`

### POST /api/files/upload
Upload a file (max 10MB).

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (file upload)

**Response:**
```json
{
  "id": "uuid",
  "original_filename": "example.pdf",
  "stored_filename": "uuid.pdf",
  "file_size": 12345,
  "mime_type": "application/pdf",
  "upload_date": "2024-01-01T12:00:00"
}
```

### GET /api/files/
List all uploaded files with metadata.

**Response:**
```json
{
  "files": [
    {
      "id": "uuid",
      "original_filename": "example.pdf",
      "stored_filename": "uuid.pdf",
      "file_size": 12345,
      "mime_type": "application/pdf",
      "upload_date": "2024-01-01T12:00:00"
    }
  ]
}
```

### GET /api/files/{file_id}
Download a specific file.

**Response:**
- File download with original filename

### GET /api/files/{file_id}/info
Get file metadata without downloading.

**Response:**
```json
{
  "id": "uuid",
  "original_filename": "example.pdf",
  "stored_filename": "uuid.pdf",
  "file_size": 12345,
  "mime_type": "application/pdf",
  "upload_date": "2024-01-01T12:00:00"
}
```

### DELETE /api/files/{file_id}
Delete a file and its metadata.

**Response:**
```json
{
  "message": "File deleted successfully",
  "file_id": "uuid"
}
```

## Running Tests

From the project root:
```bash
pytest tests/
```

Or run specific test classes:
```bash
pytest tests/test_file_upload.py::TestFileUpload
pytest tests/test_file_upload.py::TestFileListing
pytest tests/test_file_upload.py::TestFileDownload
pytest tests/test_file_upload.py::TestFileDeletion
pytest tests/test_file_upload.py::TestFileInfo
```

## Security Features

1. **File Type Validation**: Only allows images (JPEG, PNG, GIF, WebP), PDFs, and text files
2. **Filename Sanitization**: Removes path components and dangerous characters
3. **Path Traversal Prevention**: Uses `os.path.basename()` to prevent directory traversal
4. **File Size Limit**: Enforces 10MB maximum file size
5. **MIME Type Validation**: Validates both file extension and MIME type

## Allowed File Types

- **Images**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`
- **Documents**: `.pdf`
- **Text**: `.txt`, `.html`, `.css`, `.js`, `.csv`

## Notes

- Files are stored in the `backend/uploads/` directory
- Metadata is stored in `backend/metadata.json`
- The system automatically creates necessary directories on startup
- File IDs are UUIDs to ensure uniqueness

## Development

### Adding New File Types

To add new allowed file types, modify `ALLOWED_MIME_TYPES` and `ALLOWED_EXTENSIONS` in `backend/main.py`.

### Changing File Size Limit

Modify `MAX_FILE_SIZE` in `backend/main.py` (value is in bytes).

## License

This project is provided as-is for educational and development purposes.


