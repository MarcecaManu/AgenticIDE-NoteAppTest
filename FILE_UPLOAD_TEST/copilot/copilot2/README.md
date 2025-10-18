# File Upload & Management System

A full-stack file upload and management system built with FastAPI backend and vanilla HTML/JavaScript frontend.

## 🌟 Features

### Backend (FastAPI)
- ✅ RESTful API with comprehensive file operations
- ✅ File upload with size validation (10MB max)
- ✅ File type validation (images, PDFs, text files only)
- ✅ Secure filename sanitization
- ✅ Path traversal attack prevention
- ✅ Persistent file storage and metadata management
- ✅ JSON-based metadata storage

### Frontend (HTML/JavaScript)
- ✅ Drag-and-drop file upload interface
- ✅ File picker fallback
- ✅ Real-time file validation
- ✅ File list with metadata display
- ✅ Download and delete operations
- ✅ Responsive design
- ✅ Error handling and user feedback

### Security Features
- ✅ File type validation (whitelist approach)
- ✅ Filename sanitization against path traversal
- ✅ File size limits
- ✅ CORS configuration
- ✅ Input validation and error handling

## 📁 Project Structure

```
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── uploads/            # File storage directory
│   └── file_metadata.json  # Metadata storage (auto-generated)
├── frontend/
│   ├── index.html          # Main UI
│   └── script.js           # JavaScript functionality
├── tests/
│   ├── test_api.py         # Comprehensive API tests
│   └── requirements.txt    # Test dependencies
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Modern web browser

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

The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to the frontend directory:**
```bash
cd frontend
```

2. **Serve the frontend:**

**Option 1: Python HTTP Server**
```bash
python -m http.server 3000
```

**Option 2: Node.js HTTP Server** (if you have Node.js)
```bash
npx http-server -p 3000
```

**Option 3: Live Server** (VS Code extension)
- Install the Live Server extension in VS Code
- Right-click on `index.html` and select "Open with Live Server"

The frontend will be available at `http://localhost:3000`

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
python -m pytest test_api.py -v
```

## 📚 API Documentation

### Base URL
```
http://localhost:8000/api/files/
```

### Endpoints

#### 1. Upload File
**POST** `/api/files/upload`

Upload a file to the server.

**Request:**
- Content-Type: `multipart/form-data`
- Body: File in `file` field

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "original_filename": "document.pdf",
  "stored_filename": "550e8400-e29b-41d4-a716-446655440000.pdf",
  "file_size": 1024000,
  "mime_type": "application/pdf",
  "upload_date": "2023-12-07T10:30:00.000000"
}
```

**Error Responses:**
- `400` - Invalid file type
- `413` - File too large (>10MB)

#### 2. List Files
**GET** `/api/files/`

Get a list of all uploaded files.

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "original_filename": "document.pdf",
    "file_size": 1024000,
    "mime_type": "application/pdf",
    "upload_date": "2023-12-07T10:30:00.000000"
  }
]
```

#### 3. Download File
**GET** `/api/files/{file_id}`

Download a specific file.

**Parameters:**
- `file_id` (string): The unique file identifier

**Response:**
- File content with appropriate headers
- `Content-Disposition` header with original filename

**Error Responses:**
- `404` - File not found

#### 4. Delete File
**DELETE** `/api/files/{file_id}`

Delete a file and its metadata.

**Parameters:**
- `file_id` (string): The unique file identifier

**Response:**
```json
{
  "message": "File deleted successfully"
}
```

**Error Responses:**
- `404` - File not found

#### 5. Get File Info
**GET** `/api/files/{file_id}/info`

Get file metadata without downloading the file.

**Parameters:**
- `file_id` (string): The unique file identifier

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "original_filename": "document.pdf",
  "file_size": 1024000,
  "mime_type": "application/pdf",
  "upload_date": "2023-12-07T10:30:00.000000"
}
```

**Error Responses:**
- `404` - File not found

## 🛡️ Security Features

### File Type Validation
The system only accepts the following file types:

**Images:**
- JPEG (`.jpg`, `.jpeg`)
- PNG (`.png`)
- GIF (`.gif`)
- BMP (`.bmp`)
- WebP (`.webp`)

**Documents:**
- PDF (`.pdf`)

**Text Files:**
- Plain text (`.txt`)
- CSV (`.csv`)
- HTML (`.html`)
- CSS (`.css`)
- JavaScript (`.js`)
- JSON (`.json`)
- XML (`.xml`)

### Security Measures

1. **File Size Limits:** Maximum 10MB per file
2. **Filename Sanitization:** 
   - Removes dangerous characters
   - Prevents path traversal attacks
   - Strips leading dots
3. **Content Type Validation:** Double validation using file extension and MIME type
4. **Unique File Storage:** Files are stored with UUID-based names to prevent conflicts
5. **CORS Configuration:** Properly configured for cross-origin requests

## 🧪 Testing

The test suite includes comprehensive coverage of:

### Test Categories

1. **File Upload Tests:**
   - Valid text file upload
   - Valid image file upload
   - Invalid file type rejection
   - File size limit enforcement
   - Dangerous filename sanitization

2. **File Listing Tests:**
   - Empty file list
   - Multiple file listing
   - Metadata accuracy

3. **File Download Tests:**
   - Successful download
   - Non-existent file handling
   - Content verification

4. **File Deletion Tests:**
   - Successful deletion
   - Non-existent file handling
   - Metadata cleanup

5. **File Info Tests:**
   - Metadata retrieval
   - Non-existent file handling

6. **Security Tests:**
   - Filename sanitization
   - Path traversal prevention
   - File type validation

### Running Specific Tests

```bash
# Run all tests
python -m pytest test_api.py -v

# Run specific test
python -m pytest test_api.py::TestFileUploadAPI::test_upload_valid_text_file -v

# Run with coverage
python -m pytest test_api.py --cov=main --cov-report=html
```

## 🔧 Configuration

### Backend Configuration

Edit `main.py` to modify:

```python
# File size limit (in bytes)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Upload directory
UPLOAD_DIR = Path("uploads")

# Metadata file
METADATA_FILE = Path("file_metadata.json")

# Allowed file types
ALLOWED_MIME_TYPES = {
    'image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp',
    'application/pdf',
    'text/plain', 'text/csv', 'text/html', 'text/css', 'text/javascript',
    'application/json', 'application/xml'
}
```

### Frontend Configuration

Edit `script.js` to modify:

```javascript
// API base URL
this.apiBaseUrl = 'http://localhost:8000/api/files';
```

## 🐛 Troubleshooting

### Common Issues

1. **CORS Errors:**
   - Ensure the backend is running on port 8000
   - Check that the frontend is accessing the correct API URL

2. **File Upload Fails:**
   - Verify file type is supported
   - Check file size is under 10MB
   - Ensure backend uploads directory exists and is writable

3. **Tests Fail:**
   - Ensure all dependencies are installed
   - Check that no backend server is running during tests
   - Verify Python path includes backend directory

### Development Tips

1. **Backend Development:**
   - Use `uvicorn main:app --reload` for auto-reloading during development
   - Check FastAPI automatic documentation at `http://localhost:8000/docs`

2. **Frontend Development:**
   - Use browser developer tools to debug JavaScript issues
   - Check network tab for API request/response details

3. **Testing:**
   - Run tests in isolation to avoid state interference
   - Use temporary directories for test file storage

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the test cases for examples
3. Open an issue with detailed information about your problem