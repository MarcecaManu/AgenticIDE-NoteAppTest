# File Upload & Management System

A complete full-stack file upload and management system built with FastAPI backend and vanilla HTML/JavaScript frontend.

## Features

### Backend (FastAPI)
- **REST API** at `/api/files/` with 5 endpoints
- **File Upload**: POST `/api/files/upload` - Upload files up to 10MB
- **File Listing**: GET `/api/files/` - List all uploaded files with metadata
- **File Download**: GET `/api/files/{file_id}` - Download specific files
- **File Deletion**: DELETE `/api/files/{file_id}` - Delete files and metadata
- **File Info**: GET `/api/files/{file_id}/info` - Get file metadata without downloading

### Frontend (HTML/JavaScript)
- **Modern UI** with drag-and-drop file upload interface
- **File Browser** with native file picker support
- **Responsive Design** with beautiful gradients and animations
- **Real-time Management** - view, download, and delete files
- **Progress Indicators** and user-friendly error messages
- **CORS-enabled** communication with backend

### Security Features
- **File Type Validation** - Only allows images, PDFs, and text files
- **File Size Limits** - Maximum 10MB per file
- **Filename Sanitization** - Removes dangerous characters
- **Path Traversal Prevention** - Prevents directory traversal attacks
- **MIME Type Validation** - Validates both extension and MIME type

### Supported File Types
- **Images**: JPG, JPEG, PNG, GIF, BMP, WebP, SVG
- **Documents**: PDF
- **Text Files**: TXT, MD, CSV

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
│   ├── __init__.py
│   └── test_file_api.py    # Comprehensive test suite
└── README.md               # This file
```

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the FastAPI server:**
   ```bash
   python main.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Serve the frontend files:**
   
   **Option 1: Using Python's built-in server:**
   ```bash
   python -m http.server 3000
   ```
   
   **Option 2: Using Node.js (if available):**
   ```bash
   npx serve -s . -l 3000
   ```
   
   **Option 3: Open directly in browser:**
   Simply open `index.html` in your web browser.

The frontend will be available at `http://localhost:3000`

## API Documentation

Once the backend is running, you can access:
- **Interactive API docs**: `http://localhost:8000/docs`
- **Alternative API docs**: `http://localhost:8000/redoc`

### API Endpoints

#### Upload File
```http
POST /api/files/upload
Content-Type: multipart/form-data

file: [binary file data]
```

**Response:**
```json
{
  "id": "uuid-string",
  "original_filename": "example.txt",
  "stored_filename": "uuid.txt",
  "file_size": 1024,
  "mime_type": "text/plain",
  "upload_date": "2024-01-01T12:00:00Z"
}
```

#### List Files
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
      "stored_filename": "uuid.txt",
      "file_size": 1024,
      "mime_type": "text/plain",
      "upload_date": "2024-01-01T12:00:00Z"
    }
  ]
}
```

#### Download File
```http
GET /api/files/{file_id}
```

Returns the file as a binary download with appropriate headers.

#### Delete File
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

#### Get File Info
```http
GET /api/files/{file_id}/info
```

**Response:**
```json
{
  "id": "uuid-string",
  "original_filename": "example.txt",
  "stored_filename": "uuid.txt",
  "file_size": 1024,
  "mime_type": "text/plain",
  "upload_date": "2024-01-01T12:00:00Z"
}
```

## Running Tests

The project includes a comprehensive test suite with 15+ test cases covering:
- Valid file uploads (text and image files)
- Invalid file type rejection
- File size limit enforcement
- Security features (filename sanitization, path traversal prevention)
- File management operations (list, download, delete)
- Edge cases and error handling

### Run Tests

1. **Navigate to the project root:**
   ```bash
   cd /path/to/project
   ```

2. **Install test dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Run the test suite:**
   ```bash
   python -m pytest tests/ -v
   ```

### Test Coverage
- ✅ File upload with valid types
- ✅ File upload rejection for invalid types
- ✅ File size limit enforcement
- ✅ Filename sanitization
- ✅ Path traversal attack prevention
- ✅ File listing functionality
- ✅ File download functionality
- ✅ File deletion functionality
- ✅ File metadata retrieval
- ✅ Error handling for non-existent files
- ✅ Special character handling in filenames
- ✅ Empty filename handling

## File Storage

- **Files** are stored in the `backend/uploads/` directory
- **Metadata** is stored in `backend/file_metadata.json`
- **Filenames** are sanitized and made unique using UUIDs
- **Original filenames** are preserved in metadata

## Security Considerations

1. **File Type Validation**: Both extension and MIME type are checked
2. **File Size Limits**: Prevents DoS attacks via large files
3. **Filename Sanitization**: Removes dangerous characters and path components
4. **Path Traversal Prevention**: Prevents access to files outside upload directory
5. **UUID-based Storage**: Prevents filename conflicts and guessing attacks

## Development

### Adding New File Types

To add support for new file types, update these constants in `backend/main.py`:

```python
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.pdf', '.txt', '.md', '.csv', '.new_extension'}
ALLOWED_MIME_TYPES = {
    'image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp', 'image/svg+xml',
    'application/pdf', 'text/plain', 'text/markdown', 'text/csv', 'new/mime-type'
}
```

### Customizing File Size Limits

Update the `MAX_FILE_SIZE` constant in `backend/main.py`:

```python
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
```

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure the backend is running and CORS is properly configured
2. **File Upload Fails**: Check file size and type restrictions
3. **Files Not Appearing**: Verify the uploads directory exists and has proper permissions
4. **Tests Failing**: Ensure all dependencies are installed and the backend code is accessible

### Logs and Debugging

- Backend logs are displayed in the terminal where you run the FastAPI server
- Frontend errors can be viewed in the browser's developer console
- Test output provides detailed information about failures

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
