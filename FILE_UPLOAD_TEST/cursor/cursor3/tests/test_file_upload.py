import pytest
import os
import json
import shutil
from pathlib import Path
import asyncio
from backend.main import app, UPLOAD_DIR, METADATA_FILE

# Use httpx with AsyncClient and run synchronously
import httpx
from httpx import ASGITransport


class TestClient:
    """Synchronous test client wrapper for ASGI apps"""
    def __init__(self, app):
        self.app = app
        self.transport = ASGITransport(app=app)
        self._loop = None
    
    def _get_loop(self):
        """Get or create event loop"""
        try:
            return asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop
    
    def _run_async(self, coro):
        """Run async coroutine synchronously"""
        loop = self._get_loop()
        return loop.run_until_complete(coro)
    
    def _make_request(self, method, url, **kwargs):
        """Make an async request synchronously"""
        async def _request():
            async with httpx.AsyncClient(transport=self.transport, base_url="http://test") as client:
                return await client.request(method, url, **kwargs)
        return self._run_async(_request())
    
    def get(self, url, **kwargs):
        return self._make_request("GET", url, **kwargs)
    
    def post(self, url, **kwargs):
        return self._make_request("POST", url, **kwargs)
    
    def delete(self, url, **kwargs):
        return self._make_request("DELETE", url, **kwargs)
    
    def put(self, url, **kwargs):
        return self._make_request("PUT", url, **kwargs)
    
    def patch(self, url, **kwargs):
        return self._make_request("PATCH", url, **kwargs)


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Setup and teardown for each test"""
    # Clean up before test
    if UPLOAD_DIR.exists():
        shutil.rmtree(UPLOAD_DIR)
    if METADATA_FILE.exists():
        METADATA_FILE.unlink()
    
    # Create upload directory
    UPLOAD_DIR.mkdir(exist_ok=True)
    
    yield
    
    # Clean up after test
    if UPLOAD_DIR.exists():
        shutil.rmtree(UPLOAD_DIR)
    if METADATA_FILE.exists():
        METADATA_FILE.unlink()


def test_upload_valid_file(client):
    """Test uploading a valid file"""
    # Create a test file
    test_content = b"This is a test text file"
    files = {"file": ("test.txt", test_content, "text/plain")}
    
    response = client.post("/api/files/upload", files=files)
    
    assert response.status_code == 201
    data = response.json()
    
    # Check metadata structure
    assert "id" in data
    assert data["original_filename"] == "test.txt"
    assert data["file_size"] == len(test_content)
    assert data["mime_type"] == "text/plain"
    assert "upload_date" in data
    
    # Check file exists on disk
    stored_path = UPLOAD_DIR / data["stored_filename"]
    assert stored_path.exists()
    assert stored_path.read_bytes() == test_content
    
    # Check metadata file
    metadata = json.loads(METADATA_FILE.read_text())
    assert data["id"] in metadata


def test_list_files(client):
    """Test listing all uploaded files"""
    # Upload two files
    files1 = {"file": ("file1.txt", b"Content 1", "text/plain")}
    files2 = {"file": ("file2.txt", b"Content 2", "text/plain")}
    
    client.post("/api/files/upload", files=files1)
    client.post("/api/files/upload", files=files2)
    
    response = client.get("/api/files/")
    assert response.status_code == 200
    data = response.json()
    
    assert "files" in data
    assert "count" in data
    assert data["count"] == 2
    assert len(data["files"]) == 2


def test_download_file(client):
    """Test downloading a specific file"""
    # Upload a file
    test_content = b"Download test content"
    files = {"file": ("download_test.txt", test_content, "text/plain")}
    
    upload_response = client.post("/api/files/upload", files=files)
    file_id = upload_response.json()["id"]
    
    # Download the file
    response = client.get(f"/api/files/{file_id}")
    
    assert response.status_code == 200
    assert response.content == test_content
    assert "download_test.txt" in response.headers.get("content-disposition", "")


def test_delete_file(client):
    """Test deleting a file"""
    # Upload a file
    test_content = b"Delete test content"
    files = {"file": ("delete_test.txt", test_content, "text/plain")}
    
    upload_response = client.post("/api/files/upload", files=files)
    file_id = upload_response.json()["id"]
    stored_filename = upload_response.json()["stored_filename"]
    
    # Verify file exists
    stored_path = UPLOAD_DIR / stored_filename
    assert stored_path.exists()
    
    # Delete the file
    response = client.delete(f"/api/files/{file_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "File deleted successfully"
    assert data["file_id"] == file_id
    
    # Verify file is deleted from disk
    assert not stored_path.exists()
    
    # Verify metadata is removed
    metadata = json.loads(METADATA_FILE.read_text())
    assert file_id not in metadata


def test_get_file_info(client):
    """Test getting file metadata without downloading"""
    # Upload a file
    files = {"file": ("info_test.txt", b"Info test", "text/plain")}
    
    upload_response = client.post("/api/files/upload", files=files)
    file_id = upload_response.json()["id"]
    original_metadata = upload_response.json()
    
    # Get file info
    response = client.get(f"/api/files/{file_id}/info")
    
    assert response.status_code == 200
    data = response.json()
    
    # Compare metadata
    assert data["id"] == original_metadata["id"]
    assert data["original_filename"] == original_metadata["original_filename"]
    assert data["file_size"] == original_metadata["file_size"]
    assert data["mime_type"] == original_metadata["mime_type"]


def test_upload_invalid_file_type(client):
    """Test uploading an invalid file type (should be rejected)"""
    # Try to upload an executable file (not allowed)
    files = {"file": ("malicious.exe", b"executable content", "application/x-msdownload")}
    
    response = client.post("/api/files/upload", files=files)
    
    assert response.status_code == 400
    assert "not allowed" in response.json()["detail"].lower()


def test_upload_file_too_large(client):
    """Test uploading a file that exceeds size limit"""
    # Create a file larger than 10MB
    large_content = b"x" * (11 * 1024 * 1024)  # 11MB
    files = {"file": ("large.txt", large_content, "text/plain")}
    
    response = client.post("/api/files/upload", files=files)
    
    assert response.status_code == 400
    assert "size" in response.json()["detail"].lower()


def test_download_nonexistent_file(client):
    """Test downloading a file that doesn't exist"""
    response = client.get("/api/files/nonexistent-id")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_delete_nonexistent_file(client):
    """Test deleting a file that doesn't exist"""
    response = client.delete("/api/files/nonexistent-id")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_filename_sanitization(client):
    """Test that dangerous filenames are sanitized"""
    # Try to upload a file with path traversal
    files = {"file": ("../../../etc/passwd", b"content", "text/plain")}
    
    response = client.post("/api/files/upload", files=files)
    
    assert response.status_code == 201
    data = response.json()
    # Filename should be sanitized
    assert ".." not in data["original_filename"]
    assert "/" not in data["original_filename"]


def test_upload_image_file(client):
    """Test uploading an image file (allowed type)"""
    # Create a fake PNG file
    png_content = b'\x89PNG\r\n\x1a\n' + b'x' * 100
    files = {"file": ("test.png", png_content, "image/png")}
    
    response = client.post("/api/files/upload", files=files)
    
    assert response.status_code == 201
    data = response.json()
    assert data["mime_type"] in ["image/png", "application/octet-stream"]


def test_upload_pdf_file(client):
    """Test uploading a PDF file (allowed type)"""
    # Create a fake PDF file
    pdf_content = b'%PDF-1.4\n' + b'x' * 100
    files = {"file": ("test.pdf", pdf_content, "application/pdf")}
    
    response = client.post("/api/files/upload", files=files)
    
    assert response.status_code == 201
    data = response.json()
    assert "pdf" in data["mime_type"].lower()

