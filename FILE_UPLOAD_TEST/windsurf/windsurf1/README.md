# File Upload & Management System

A full-stack file upload and management system built with FastAPI backend and vanilla HTML/JavaScript frontend.

## Features

### Backend (FastAPI)
- **File Upload**: Upload files up to 10MB with validation
- **File Management**: List, download, delete files with metadata
- **Security**: File type validation, filename sanitization, path traversal prevention
- **Persistence**: Files stored on filesystem, metadata in JSON database
- **REST API**: Clean RESTful endpoints at `/api/files/`

### Frontend (HTML/JavaScript)
- **Drag & Drop**: Modern drag-and-drop file upload interface
- **File Browser**: Browse and select files using native file picker
- **File Management**: View, download, and delete uploaded files
- **Responsive Design**: Mobile-friendly responsive layout
- **Error Handling**: User-friendly error messages and validation

### Security Features
- **File Type Validation**: Only allows images, PDFs, and text files
- **Size Limits**: Maximum file size of 10MB
- **Filename Sanitization**: Prevents dangerous characters and path traversal
- **MIME Type Checking**: Validates both file extension and MIME type

## Project Structure

```
├── backend/
│   ├── main.py              # FastAPI application
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── index.html          # Main HTML page
│   ├── styles.css          # CSS styling
│   └── script.js           # JavaScript functionality
├── tests/
│   └── test_file_upload.py # Comprehensive test suite
└── README.md               # This file
```

## API Endpoints

### POST /api/files/upload
Upload a file and return metadata.

**Request**: Multipart form data with file
**Response**: File metadata including ID, filename, size, type, upload date

### GET /api/files/
List all uploaded files with metadata.

**Response**: Array of file information objects

### GET /api/files/{file_id}
Download a specific file.

**Response**: File content with appropriate headers

### DELETE /api/files/{file_id}
Delete a file and its metadata.

**Response**: Success message

### GET /api/files/{file_id}/info
Get file metadata without downloading.

**Response**: File metadata object

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the FastAPI server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Serve the files using a simple HTTP server:

**Using Python:**
```bash
python -m http.server 3000
```

**Using Node.js (if available):**
```bash
npx serve -p 3000
```

The frontend will be available at `http://localhost:3000`

### Alternative: Serve Frontend through FastAPI

You can also serve the frontend files directly through FastAPI by adding static file serving to the backend.

## Running Tests

1. Navigate to the project root directory
2. Install test dependencies (if not already installed):
```bash
pip install pytest pytest-asyncio httpx
```

3. Run the test suite:
```bash
python -m pytest tests/ -v
```

### Test Coverage

The test suite includes:
- ✅ Valid file upload (images, PDFs, text files)
- ✅ Invalid file type rejection
- ✅ File size limit validation
- ✅ Filename sanitization and security
- ✅ File listing functionality
- ✅ File download functionality
- ✅ File deletion functionality
- ✅ File metadata retrieval
- ✅ Path traversal attack prevention
- ✅ Multiple file management
- ✅ Error handling for non-existent files

## File Storage

- **Files**: Stored in `backend/uploads/` directory
- **Metadata**: Stored in `backend/file_metadata.json`
- **Naming**: Files are renamed with UUID to prevent conflicts

## Supported File Types

### Images
- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- BMP (.bmp)
- WebP (.webp)

### Documents
- PDF (.pdf)

### Text Files
- Plain text (.txt)
- CSV (.csv)
- HTML (.html)
- CSS (.css)
- JavaScript (.js)
- JSON (.json)
- XML (.xml)

## Configuration

### Backend Configuration (main.py)
```python
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
UPLOAD_DIR = Path("uploads")
METADATA_FILE = Path("file_metadata.json")
```

### Frontend Configuration (script.js)
```javascript
const API_BASE_URL = 'http://localhost:8000/api/files';
```

## Security Considerations

1. **File Type Validation**: Both MIME type and file extension are checked
2. **Filename Sanitization**: Dangerous characters are replaced with underscores
3. **Path Traversal Prevention**: Directory traversal sequences are removed
4. **Size Limits**: Files larger than 10MB are rejected
5. **CORS**: Configured for cross-origin requests (adjust for production)

## Production Deployment

### Backend
- Use a production ASGI server like Gunicorn with Uvicorn workers
- Configure proper CORS origins (remove wildcard)
- Set up proper file storage (consider cloud storage for scalability)
- Add authentication and authorization
- Implement rate limiting
- Use environment variables for configuration

### Frontend
- Serve through a web server like Nginx
- Enable HTTPS
- Optimize assets (minification, compression)
- Configure proper caching headers

### Database
- Consider using a proper database (PostgreSQL, MySQL) instead of JSON for metadata
- Implement database migrations
- Add proper indexing for file queries

## Development

### Adding New File Types
1. Update `ALLOWED_MIME_TYPES` in `main.py`
2. Add corresponding file extensions to validation
3. Update frontend file picker accept attribute
4. Add appropriate file icons in `getFileIcon()` function

### Extending API
- Follow RESTful conventions
- Add proper error handling
- Include comprehensive tests
- Update API documentation

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure the frontend is making requests to the correct backend URL
2. **File Upload Fails**: Check file size and type restrictions
3. **Files Not Found**: Verify the uploads directory exists and has proper permissions
4. **Tests Failing**: Ensure no other instance of the app is running on the same port

### Debug Mode
Run the backend with debug logging:
```bash
uvicorn main:app --reload --log-level debug
```

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

For issues and questions, please create an issue in the project repository.
