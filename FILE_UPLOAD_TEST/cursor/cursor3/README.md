# File Upload & Management System

A full-stack file upload and management system built with FastAPI (backend) and vanilla HTML/JavaScript (frontend).

## Features

- ✅ Upload files via drag-and-drop or file picker
- ✅ View list of uploaded files with metadata
- ✅ Download files
- ✅ Delete files
- ✅ File type validation (images, PDFs, text files only)
- ✅ Filename sanitization and path traversal prevention
- ✅ File size limit (10MB)
- ✅ Persistent storage (filesystem + JSON metadata)

## Project Structure

```
.
├── backend/
│   ├── main.py              # FastAPI application
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── index.html          # Main HTML page
│   └── app.js              # Frontend JavaScript
├── tests/
│   ├── test_file_upload.py # Automated tests
│   ├── conftest.py         # Pytest configuration
│   └── __init__.py
└── README.md
```

## Setup Instructions

### Backend Setup

1. Navigate to the project directory:
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

4. Run the server:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Open `frontend/index.html` in a web browser, or
2. Serve it using a simple HTTP server:
   ```bash
   # Python 3
   cd frontend
   python -m http.server 8080
   ```

   Then open `http://localhost:8080` in your browser.

**Note:** If you're serving the frontend from a different port, update the `API_BASE_URL` in `frontend/app.js` to match your backend URL.

### Running Tests

1. Install pytest (if not already installed):
   ```bash
   pip install pytest
   ```

2. Run tests from the project root:
   ```bash
   pytest tests/
   ```

   Or run with verbose output:
   ```bash
   pytest tests/ -v
   ```

## API Endpoints

- `POST /api/files/upload` - Upload a file (max 10MB)
- `GET /api/files/` - List all uploaded files
- `GET /api/files/{file_id}` - Download a specific file
- `GET /api/files/{file_id}/info` - Get file metadata
- `DELETE /api/files/{file_id}` - Delete a file

## Security Features

- **File Type Validation**: Only allows images, PDFs, and text files
- **Filename Sanitization**: Removes dangerous characters and path components
- **Path Traversal Prevention**: Prevents directory traversal attacks
- **File Size Limits**: Maximum 10MB per file

## Allowed File Types

- **Images**: JPEG, PNG, GIF, WebP, BMP
- **Documents**: PDF
- **Text Files**: TXT, HTML, CSS, JavaScript, CSV, JSON, XML

## Storage

- Files are stored in the `backend/uploads/` directory
- Metadata is stored in `backend/metadata.json`
- Both are created automatically on first use

## Testing

The test suite includes:
- File upload functionality
- File listing
- File download
- File deletion
- File info retrieval
- Invalid file type rejection
- File size validation
- Filename sanitization

Run all tests with:
```bash
pytest tests/ -v
```

## License

This project is provided as-is for educational purposes.

