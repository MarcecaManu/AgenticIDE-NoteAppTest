# File Upload & Management System

A full-stack file upload and management system built with FastAPI backend and vanilla HTML/JavaScript frontend.

## Features

### Backend (FastAPI)
- **REST API** at `/api/files/` with 5 endpoints
- **File Upload**: POST `/api/files/upload` - Upload files up to 10MB
- **File Listing**: GET `/api/files/` - List all uploaded files with metadata
- **File Download**: GET `/api/files/{file_id}` - Download specific files
- **File Deletion**: DELETE `/api/files/{file_id}` - Delete files and metadata
- **File Info**: GET `/api/files/{file_id}/info` - Get file metadata without downloading

### Frontend (HTML/JavaScript)
- **Drag & Drop Interface** - Modern file upload experience
- **File Browser** - Native file picker support
- **File Management** - View, download, and delete files
- **Responsive Design** - Works on desktop and mobile
- **Real-time Updates** - Automatic refresh after operations
- **Progress Indicators** - Visual feedback during uploads
- **Error Handling** - User-friendly error messages

### Security Features
- **File Type Validation** - Only allows images, PDFs, and text files
- **File Size Limits** - Maximum 10MB per file
- **Filename Sanitization** - Removes dangerous characters
- **Path Traversal Prevention** - Prevents directory traversal attacks
- **MIME Type Validation** - Double-checks file types

### Supported File Types
- **Images**: JPEG, PNG, GIF, BMP, WebP, SVG, TIFF
- **Documents**: PDF
- **Text Files**: TXT, CSV, HTML, CSS, JavaScript, JSON, XML

## Project Structure

```
├── backend/                 # FastAPI backend
│   ├── main.py             # Main application file
│   ├── requirements.txt    # Python dependencies
│   ├── uploads/           # Uploaded files storage (created automatically)
│   └── file_metadata.json # File metadata storage (created automatically)
├── frontend/               # HTML/JavaScript frontend
│   ├── index.html         # Main HTML page
│   ├── styles.css         # CSS styling
│   └── script.js          # JavaScript functionality
└── tests/                  # Test suite
    ├── test_file_api.py   # Comprehensive API tests
    └── requirements.txt   # Test dependencies
```

## Quick Start

### 1. Set Up Backend

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Start the server
python main.py
```

The backend will be available at `http://localhost:8000`

### 2. Set Up Frontend

```bash
# Navigate to frontend directory
cd frontend

# Start a simple HTTP server (Python 3)
python -m http.server 3000

# Or use Node.js
npx http-server -p 3000
```

The frontend will be available at `http://localhost:3000`

### 3. Run Tests

```bash
# Navigate to tests directory
cd tests

# Install test dependencies
pip install -r requirements.txt

# Run tests
pytest test_file_api.py -v
```

## API Documentation

### Upload File
```http
POST /api/files/upload
Content-Type: multipart/form-data

file: <file_data>
```

**Response:**
```json
{
  "id": "uuid-string",
  "original_filename": "example.txt",
  "stored_filename": "uuid_example.txt",
  "file_size": 1024,
  "mime_type": "text/plain",
  "upload_date": "2024-01-01T12:00:00Z"
}
```

### List Files
```http
GET /api/files/
```

**Response:**
```json
{
  "files": [
    {
      "id": "uuid-string",
      "original_filename": "example.txt",
      "stored_filename": "uuid_example.txt",
      "file_size": 1024,
      "mime_type": "text/plain",
      "upload_date": "2024-01-01T12:00:00Z"
    }
  ]
}
```

### Download File
```http
GET /api/files/{file_id}
```

Returns the file with appropriate headers for download.

### Delete File
```http
DELETE /api/files/{file_id}
```

**Response:**
```json
{
  "message": "File deleted successfully",
  "file_id": "uuid-string"
}
```

### Get File Info
```http
GET /api/files/{file_id}/info
```

**Response:**
```json
{
  "id": "uuid-string",
  "original_filename": "example.txt",
  "stored_filename": "uuid_example.txt",
  "file_size": 1024,
  "mime_type": "text/plain",
  "upload_date": "2024-01-01T12:00:00Z"
}
```

## Configuration

### Backend Configuration
Edit `backend/main.py` to modify:
- `MAX_FILE_SIZE`: Maximum file size (default: 10MB)
- `ALLOWED_MIME_TYPES`: Allowed file types
- `UPLOAD_DIR`: Upload directory path
- `METADATA_FILE`: Metadata storage file

### Frontend Configuration
Edit `frontend/script.js` to modify:
- `apiBase`: Backend API URL (default: `http://localhost:8000/api/files`)

## Testing

The test suite includes 15+ comprehensive tests covering:

1. **File Upload Tests**
   - Valid text files
   - Valid image files
   - Valid PDF files
   - Invalid file types (rejected)
   - File size limits
   - Filename sanitization

2. **File Management Tests**
   - Listing files (empty and populated)
   - Downloading files
   - Getting file information
   - Deleting files

3. **Security Tests**
   - Path traversal prevention
   - Filename sanitization
   - File type validation
   - Empty filename handling

4. **Error Handling Tests**
   - Nonexistent file operations
   - Invalid requests
   - Server error scenarios

Run tests with:
```bash
cd tests
pytest test_file_api.py -v
```

## Security Considerations

1. **File Type Validation**: Both MIME type and file extension are checked
2. **Filename Sanitization**: Dangerous characters are removed or replaced
3. **Path Traversal Prevention**: Directory traversal attempts are blocked
4. **File Size Limits**: Prevents DoS attacks via large files
5. **Unique File Storage**: Files are stored with UUID prefixes to prevent conflicts
6. **CORS Configuration**: Properly configured for frontend communication

## Production Deployment

### Backend Deployment
1. Use a production WSGI server like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
   ```

2. Configure environment variables for production settings
3. Set up proper file storage (consider cloud storage for scalability)
4. Implement proper logging and monitoring
5. Configure HTTPS and security headers

### Frontend Deployment
1. Use a web server like Nginx or Apache
2. Configure proper caching headers
3. Minify CSS and JavaScript for production
4. Set up HTTPS

## Dependencies

### Backend
- `fastapi==0.104.1` - Web framework
- `uvicorn[standard]==0.24.0` - ASGI server
- `python-multipart==0.0.6` - File upload support

### Tests
- `pytest==7.4.3` - Testing framework
- `httpx==0.25.2` - HTTP client for testing

## License

This project is open source and available under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## Support

For issues and questions, please open an issue in the project repository.
