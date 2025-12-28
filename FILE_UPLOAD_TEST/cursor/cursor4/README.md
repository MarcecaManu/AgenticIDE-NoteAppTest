# File Upload & Management System

A full-stack file upload and management system built with FastAPI (backend) and vanilla HTML/JavaScript (frontend).

## Features

- **File Upload**: Drag-and-drop or file picker interface
- **File Management**: List, download, and delete uploaded files
- **Security**: File type validation, filename sanitization, path traversal prevention
- **Metadata**: Track file information including size, MIME type, and upload date
- **RESTful API**: Clean REST API design with proper HTTP status codes

## Project Structure

```
.
├── backend/
│   └── main.py          # FastAPI backend application
├── frontend/
│   ├── index.html       # Frontend HTML
│   └── app.js          # Frontend JavaScript
├── tests/
│   └── test_file_upload.py  # Automated tests
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the backend server:**
   ```bash
   cd backend
   python main.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Open the frontend:**
   - Open `frontend/index.html` in your web browser
   - Or serve it using a local web server:
     ```bash
     # Using Python
     cd frontend
     python -m http.server 8080
     ```
     Then navigate to `http://localhost:8080`

## API Endpoints

### POST `/api/files/upload`
Upload a file (max 10MB).

**Request:** Multipart form data with `file` field

**Response:** JSON with file metadata
```json
{
  "id": "uuid",
  "original_filename": "example.jpg",
  "stored_filename": "uuid.jpg",
  "file_size": 12345,
  "mime_type": "image/jpeg",
  "upload_date": "2024-01-01T12:00:00"
}
```

### GET `/api/files/`
List all uploaded files.

**Response:**
```json
{
  "files": [...],
  "count": 5
}
```

### GET `/api/files/{file_id}`
Download a specific file.

**Response:** File download

### GET `/api/files/{file_id}/info`
Get file metadata without downloading.

**Response:** JSON with file metadata

### DELETE `/api/files/{file_id}`
Delete a file and its metadata.

**Response:**
```json
{
  "message": "File deleted successfully",
  "file_id": "uuid"
}
```

## Security Features

- **File Type Validation**: Only allows images, PDFs, and text files
- **Filename Sanitization**: Removes path components and dangerous characters
- **Path Traversal Prevention**: Validates file paths before operations
- **File Size Limit**: Maximum 10MB per file

## Allowed File Types

- **Images**: JPEG, PNG, GIF, WebP, BMP
- **Documents**: PDF
- **Text Files**: TXT, HTML, CSS, JavaScript, CSV, JSON, XML

## Testing

Run the automated tests:

```bash
pytest tests/test_file_upload.py -v
```

The test suite includes:
- File upload validation
- File type rejection
- File listing
- File download
- File deletion
- File metadata retrieval
- File size limit enforcement
- Path traversal prevention

## Data Storage

- **Files**: Stored in `backend/uploads/` directory
- **Metadata**: Stored in `backend/metadata.json` file

## Development

### Backend Development
The backend uses FastAPI with automatic API documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Frontend Development
The frontend is a single-page application using vanilla JavaScript. No build process required.

## License

This project is provided as-is for educational purposes.

