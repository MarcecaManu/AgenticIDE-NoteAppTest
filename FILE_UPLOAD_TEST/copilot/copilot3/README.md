# File Upload & Management System

A full-stack file upload and management system built with FastAPI (backend) and vanilla HTML/JavaScript (frontend). This system provides secure file upload, storage, and management capabilities with a user-friendly web interface.

## Features

### Backend (FastAPI)
- **RESTful API** with complete CRUD operations for files
- **File Upload** with drag-and-drop support (max 10MB per file)
- **File Type Validation** - supports images, PDFs, and text files only
- **Security Features**:
  - Filename sanitization to prevent path traversal attacks
  - MIME type validation
  - File size limits
  - CORS support for frontend integration
- **Persistent Storage** using filesystem + JSON metadata
- **Comprehensive Error Handling** with appropriate HTTP status codes

### Frontend (HTML/JavaScript)
- **Modern UI** with responsive design
- **Drag & Drop** file upload interface
- **File Management** - view, download, and delete uploaded files
- **Real-time Feedback** with progress indicators and alerts
- **Mobile-friendly** responsive design
- **Error Handling** with user-friendly error messages

### Security Features
- ✅ File type validation (only images, PDFs, text files allowed)
- ✅ Filename sanitization (removes dangerous characters)
- ✅ Path traversal protection
- ✅ File size limits (10MB maximum)
- ✅ MIME type validation
- ✅ Unique file naming to prevent conflicts

## Project Structure

```
copilot3/
├── backend/
│   ├── main.py              # FastAPI application with all endpoints
│   ├── uploads/             # Directory for uploaded files
│   └── file_metadata.json   # JSON database for file metadata
├── frontend/
│   └── index.html           # Complete web interface
├── tests/
│   └── test_file_management.py  # Comprehensive test suite (10+ tests)
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## API Endpoints

The backend exposes a REST API at `/api/files/` with the following endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/files/upload` | Upload a file and return metadata |
| `GET` | `/api/files/` | List all uploaded files with metadata |
| `GET` | `/api/files/{file_id}` | Download a specific file |
| `DELETE` | `/api/files/{file_id}` | Delete a file and its metadata |
| `GET` | `/api/files/{file_id}/info` | Get file metadata without downloading |

### File Metadata Structure

```json
{
  "id": "uuid4-string",
  "original_filename": "user_uploaded_name.txt",
  "stored_filename": "uuid4_with_extension.txt",
  "file_size": 1024,
  "mime_type": "text/plain",
  "upload_date": "2024-01-01T12:00:00.000000"
}
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

2. **Install Python dependencies:**
   ```bash
   pip install -r ../requirements.txt
   ```

3. **Start the FastAPI server:**
   ```bash
   python main.py
   ```
   
   The API will be available at: `http://127.0.0.1:8000`
   
   API documentation (Swagger UI): `http://127.0.0.1:8000/docs`

### Frontend Setup

1. **Open the frontend file:**
   - Navigate to the `frontend/` directory
   - Open `index.html` in a web browser
   - Or serve it using a simple HTTP server:
   
   ```bash
   # Using Python (recommended)
   cd frontend
   python -m http.server 3000
   # Then open http://localhost:3000 in your browser
   
   # Using Node.js (if available)
   npx serve . -p 3000
   ```

## Usage

### Web Interface
1. Open the frontend in your web browser
2. **Upload files:**
   - Drag and drop files onto the upload area, or
   - Click "Choose Files" to select files
3. **Manage files:**
   - View all uploaded files in the list below
   - Download files by clicking the "Download" button
   - Delete files by clicking the "Delete" button
   - View file metadata (size, type, upload date)

### API Usage Examples

**Upload a file:**
```bash
curl -X POST "http://127.0.0.1:8000/api/files/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@example.txt"
```

**List files:**
```bash
curl -X GET "http://127.0.0.1:8000/api/files/"
```

**Download a file:**
```bash
curl -X GET "http://127.0.0.1:8000/api/files/{file_id}" \
     --output downloaded_file.txt
```

**Delete a file:**
```bash
curl -X DELETE "http://127.0.0.1:8000/api/files/{file_id}"
```

**Get file info:**
```bash
curl -X GET "http://127.0.0.1:8000/api/files/{file_id}/info"
```

## Supported File Types

### Images
- JPEG (`.jpg`, `.jpeg`)
- PNG (`.png`)
- GIF (`.gif`)
- WebP (`.webp`)
- SVG (`.svg`)

### Documents
- PDF (`.pdf`)

### Text Files
- Plain text (`.txt`)
- CSV (`.csv`)
- HTML (`.html`)
- CSS (`.css`)
- JavaScript (`.js`)
- JSON (`.json`)
- XML (`.xml`)

## Running Tests

The project includes a comprehensive test suite covering all major functionality:

```bash
# Install test dependencies (if not already installed)
pip install -r requirements.txt

# Run all tests
cd tests
python -m pytest test_file_management.py -v

# Run specific test categories
python -m pytest test_file_management.py::TestFileUploadManagement::test_file_upload_success -v
```

### Test Coverage
The test suite includes 10+ tests covering:
- ✅ File upload success scenarios
- ✅ File listing and sorting
- ✅ File download functionality
- ✅ File deletion operations
- ✅ File type validation (acceptance and rejection)
- ✅ File size validation
- ✅ Filename sanitization for security
- ✅ File info endpoint
- ✅ API root endpoint
- ✅ Concurrent operations handling

## Configuration

### File Size Limit
Default maximum file size is 10MB. To change this, modify `MAX_FILE_SIZE` in `backend/main.py`:

```python
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
```

### Allowed File Types
To add or remove allowed file types, modify `ALLOWED_MIME_TYPES` in `backend/main.py`:

```python
ALLOWED_MIME_TYPES = {
    'image/jpeg', 'image/png',  # Images
    'application/pdf',          # PDFs
    'text/plain',              # Text files
    # Add more MIME types as needed
}
```

### Storage Location
By default, files are stored in `backend/uploads/` and metadata in `backend/file_metadata.json`. To change this, modify the paths in `backend/main.py`:

```python
UPLOAD_DIR = Path("custom_uploads_folder")
METADATA_FILE = Path("custom_metadata.json")
```

## Security Considerations

This system implements several security measures:

1. **File Type Validation**: Only allows safe file types (images, PDFs, text files)
2. **Filename Sanitization**: Removes dangerous characters and path components
3. **File Size Limits**: Prevents large file uploads that could exhaust storage
4. **Path Traversal Protection**: Ensures files are stored only in the designated directory
5. **MIME Type Validation**: Validates both declared and detected MIME types
6. **Unique File Names**: Prevents file name conflicts and overwrites

## Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Change the port in main.py or kill the process using the port
uvicorn.run(app, host="127.0.0.1", port=8001, reload=True)  # Use different port
```

**CORS errors in browser:**
- Ensure the backend is running
- Check that the frontend is accessing the correct API URL
- CORS is configured to allow all origins in development

**File upload fails:**
- Check file size (must be < 10MB)
- Verify file type is supported
- Ensure backend `uploads/` directory exists and is writable

**Tests failing:**
- Ensure you're in the correct directory when running tests
- Check that all dependencies are installed
- Verify Python path includes the backend directory

## Development

### Adding New Features

1. **New API endpoints**: Add to `backend/main.py`
2. **Frontend features**: Modify `frontend/index.html`
3. **Tests**: Add to `tests/test_file_management.py`

### Code Quality
- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings to functions
- Include error handling
- Write tests for new features

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

For issues, questions, or contributions, please refer to the project documentation or create an issue in the repository.