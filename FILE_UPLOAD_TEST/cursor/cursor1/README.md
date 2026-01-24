# File Upload & Management System

A full-stack file upload and management system built with FastAPI (backend) and vanilla HTML/JavaScript (frontend).

## Features

- **File Upload**: Drag-and-drop or file picker interface
- **File Management**: List, download, and delete uploaded files
- **Security**: File type validation, filename sanitization, path traversal prevention
- **Metadata**: Track file information (name, size, type, upload date)
- **Persistent Storage**: Files stored on filesystem, metadata in JSON database

## Project Structure

```
.
├── backend/
│   ├── main.py           # FastAPI application
│   └── requirements.txt  # Python dependencies
├── frontend/
│   ├── index.html        # Main HTML page
│   ├── styles.css        # Styling
│   └── app.js            # Frontend JavaScript
├── tests/
│   ├── test_file_upload.py  # Automated tests
│   └── requirements.txt     # Test dependencies
└── README.md
```

## Setup Instructions

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

4. Run the server:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Open `frontend/index.html` in a web browser, or
2. Serve it using a simple HTTP server:
```bash
cd frontend
python -m http.server 8080
```

Then open `http://localhost:8080` in your browser.

**Note**: Make sure the backend is running before using the frontend.

### Running Tests

1. Install test dependencies:
```bash
cd tests
pip install -r requirements.txt
```

2. Run tests:
```bash
pytest test_file_upload.py -v
```

## API Endpoints

- `POST /api/files/upload` - Upload a file (max 10MB)
- `GET /api/files/` - List all uploaded files
- `GET /api/files/{file_id}` - Download a specific file
- `GET /api/files/{file_id}/info` - Get file metadata
- `DELETE /api/files/{file_id}` - Delete a file

## Security Features

- **File Type Validation**: Only allows images, PDFs, and text files
- **Filename Sanitization**: Prevents path traversal attacks
- **File Size Limits**: Maximum 10MB per file
- **MIME Type Checking**: Validates both extension and content type

## Allowed File Types

- **Images**: .jpg, .jpeg, .png, .gif, .bmp, .webp, .svg
- **PDFs**: .pdf
- **Text Files**: .txt, .md, .csv, .json, .xml, .html, .css, .js, .log

## Storage

- Files are stored in the `backend/uploads/` directory
- Metadata is stored in `backend/metadata.json`
- Both are created automatically on first use

