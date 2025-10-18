# File Upload & Management System

A full-stack file upload and management system built with FastAPI backend and vanilla HTML/JavaScript frontend.

## Features

### Backend (FastAPI)
- **REST API** at `/api/files/` with complete CRUD operations
- **File Upload** with drag-and-drop support (max 10MB)
- **File Type Validation** - only allows images, PDFs, and text files
- **Security Features**:
  - Filename sanitization to prevent path traversal attacks
  - File type validation by extension and MIME type
  - File size limits
- **Persistent Storage** using filesystem + JSON metadata
- **CORS enabled** for frontend integration

### Frontend (HTML/JavaScript)
- **Modern UI** with responsive design and animations
- **Drag & Drop** file upload with visual feedback
- **File Browser** with file picker fallback
- **File Management**:
  - View uploaded files with metadata
  - Download files
  - Delete files
  - Get detailed file information
- **Progress Indicators** and error handling
- **Mobile-friendly** responsive design

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/files/upload` | Upload a file and return metadata |
| GET | `/api/files/` | List all uploaded files with metadata |
| GET | `/api/files/{file_id}` | Download a specific file |
| DELETE | `/api/files/{file_id}` | Delete a file and its metadata |
| GET | `/api/files/{file_id}/info` | Get file metadata without downloading |

### File Metadata Structure
```json
{
  "id": "uuid4-string",
  "original_filename": "document.pdf",
  "stored_filename": "uuid4_sanitized_filename.pdf",
  "file_size": 1024576,
  "mime_type": "application/pdf",
  "upload_date": "2025-10-12T14:30:00.000000"
}
```

## Project Structure

```
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── uploads/            # File storage directory
│   └── file_metadata.json  # Metadata storage (created automatically)
├── frontend/
│   └── index.html          # Complete frontend application
├── tests/
│   ├── test_file_upload_system.py  # Comprehensive test suite
│   ├── requirements.txt             # Test dependencies
│   └── pytest.ini                  # Test configuration
└── README.md               # This file
```

## Setup and Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the server:**
   ```bash
   python main.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

The backend server will start on `http://localhost:8000`

### Frontend Access

Once the backend is running, you can access the frontend at:
```
http://localhost:8000
```

The backend serves the frontend static files automatically.

### Running Tests

1. **Navigate to the tests directory:**
   ```bash
   cd tests
   ```

2. **Install test dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the test suite:**
   ```bash
   pytest
   ```

   For verbose output:
   ```bash
   pytest -v
   ```

   For coverage report:
   ```bash
   pytest --cov=../backend
   ```

## Supported File Types

### Images
- JPEG/JPG (`.jpg`, `.jpeg`)
- PNG (`.png`)
- GIF (`.gif`)
- BMP (`.bmp`)
- WebP (`.webp`)
- SVG (`.svg`)

### Documents
- PDF (`.pdf`)

### Text Files
- Plain text (`.txt`)
- Markdown (`.md`)
- CSV (`.csv`)
- JSON (`.json`)
- XML (`.xml`)
- HTML (`.html`)
- CSS (`.css`)
- JavaScript (`.js`)
- Python (`.py`)
- Java (`.java`)
- C/C++ (`.c`, `.cpp`)

## Security Features

1. **File Type Validation**: Both extension and MIME type checking
2. **Filename Sanitization**: Removes dangerous characters and prevents path traversal
3. **File Size Limits**: Maximum 10MB per file
4. **Secure Storage**: Files stored with UUID-based names to prevent conflicts
5. **CORS Configuration**: Properly configured for frontend access

## API Usage Examples

### Upload a File
```bash
curl -X POST "http://localhost:8000/api/files/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@document.pdf"
```

### List All Files
```bash
curl -X GET "http://localhost:8000/api/files/" \
     -H "accept: application/json"
```

### Download a File
```bash
curl -X GET "http://localhost:8000/api/files/{file_id}" \
     --output downloaded_file.pdf
```

### Get File Info
```bash
curl -X GET "http://localhost:8000/api/files/{file_id}/info" \
     -H "accept: application/json"
```

### Delete a File
```bash
curl -X DELETE "http://localhost:8000/api/files/{file_id}" \
     -H "accept: application/json"
```

## Test Coverage

The test suite includes comprehensive coverage for:

1. **File Upload Tests**:
   - Valid file types (text, PDF, images)
   - Invalid file types (rejected)
   - File size validation
   - Filename sanitization

2. **File Management Tests**:
   - Listing files (empty and with content)
   - Downloading files
   - Getting file information
   - File deletion

3. **Security Tests**:
   - Path traversal prevention
   - File type validation
   - Size limit enforcement

4. **Integration Tests**:
   - Complete workflow testing
   - Metadata persistence
   - Multiple file operations

## Development

### Adding New File Types

To add support for new file types, update the following in `backend/main.py`:

1. Add extensions to `ALLOWED_EXTENSIONS`
2. Add MIME types to `ALLOWED_MIME_TYPES`

### Customizing File Size Limits

Change the `MAX_FILE_SIZE` constant in `backend/main.py`:
```python
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
```

### Frontend Customization

The frontend is a single HTML file (`frontend/index.html`) with embedded CSS and JavaScript. You can:
- Modify the styling in the `<style>` section
- Update the JavaScript functionality
- Add new features to the interface

## Troubleshooting

### Common Issues

1. **Import errors in tests**: Ensure you're running tests from the `tests/` directory
2. **CORS errors**: Make sure the backend is running when accessing the frontend
3. **File upload fails**: Check file size and type restrictions
4. **Permission errors**: Ensure the backend has write permissions to the `uploads/` directory

### Error Codes

- `413`: File too large (exceeds 10MB limit)
- `415`: Unsupported file type
- `404`: File not found
- `500`: Server error (check logs)

## License

This project is open source and available under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Contact

For questions or support, please create an issue in the project repository.