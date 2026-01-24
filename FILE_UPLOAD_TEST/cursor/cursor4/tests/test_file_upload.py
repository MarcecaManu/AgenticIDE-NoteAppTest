import pytest
import os
import json
import tempfile
import shutil
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.main import app, UPLOAD_DIR, METADATA_FILE

# Create a test client
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup and teardown test environment"""
    # Create temporary directories
    original_upload_dir = UPLOAD_DIR
    original_metadata_file = METADATA_FILE
    
    # Use temporary directory for tests
    temp_dir = tempfile.mkdtemp()
    test_upload_dir = Path(temp_dir) / "uploads"
    test_metadata_file = Path(temp_dir) / "metadata.json"
    
    # Monkey patch the paths
    import backend.main
    backend.main.UPLOAD_DIR = test_upload_dir
    backend.main.METADATA_FILE = test_metadata_file
    
    # Create upload directory
    test_upload_dir.mkdir(exist_ok=True)
    
    yield
    
    # Cleanup
    shutil.rmtree(temp_dir)
    backend.main.UPLOAD_DIR = original_upload_dir
    backend.main.METADATA_FILE = original_metadata_file


def test_upload_valid_file():
    """Test uploading a valid file (image)"""
    # Create a test image file
    test_file_content = b"fake image content"
    files = {"file": ("test_image.jpg", test_file_content, "image/jpeg")}
    
    response = client.post("/api/files/upload", files=files)
    
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["original_filename"] == "test_image.jpg"
    assert data["file_size"] == len(test_file_content)
    assert data["mime_type"] in ["image/jpeg", "image/jpg"]
    assert "upload_date" in data
    assert "stored_filename" in data


def test_upload_rejected_file_type():
    """Test that invalid file types are rejected"""
    # Try to upload an executable file
    test_file_content = b"executable content"
    files = {"file": ("malicious.exe", test_file_content, "application/x-msdownload")}
    
    response = client.post("/api/files/upload", files=files)
    
    assert response.status_code == 400
    data = response.json()
    assert "not allowed" in data["detail"].lower()


def test_list_files():
    """Test listing all uploaded files"""
    # Upload a file first
    test_file_content = b"test content"
    files = {"file": ("test.txt", test_file_content, "text/plain")}
    upload_response = client.post("/api/files/upload", files=files)
    assert upload_response.status_code == 201
    
    # List files
    response = client.get("/api/files/")
    
    assert response.status_code == 200
    data = response.json()
    assert "files" in data
    assert "count" in data
    assert data["count"] >= 1
    assert len(data["files"]) >= 1
    
    # Check that our uploaded file is in the list
    file_ids = [f["id"] for f in data["files"]]
    uploaded_file_id = upload_response.json()["id"]
    assert uploaded_file_id in file_ids


def test_download_file():
    """Test downloading a specific file"""
    # Upload a file first
    test_file_content = b"download test content"
    files = {"file": ("download_test.txt", test_file_content, "text/plain")}
    upload_response = client.post("/api/files/upload", files=files)
    assert upload_response.status_code == 201
    
    file_id = upload_response.json()["id"]
    
    # Download the file
    response = client.get(f"/api/files/{file_id}")
    
    assert response.status_code == 200
    assert response.content == test_file_content
    assert "download_test.txt" in response.headers.get("content-disposition", "")


def test_delete_file():
    """Test deleting a file"""
    # Upload a file first
    test_file_content = b"delete test content"
    files = {"file": ("delete_test.txt", test_file_content, "text/plain")}
    upload_response = client.post("/api/files/upload", files=files)
    assert upload_response.status_code == 201
    
    file_id = upload_response.json()["id"]
    
    # Verify file exists
    info_response = client.get(f"/api/files/{file_id}/info")
    assert info_response.status_code == 200
    
    # Delete the file
    delete_response = client.delete(f"/api/files/{file_id}")
    
    assert delete_response.status_code == 200
    data = delete_response.json()
    assert data["file_id"] == file_id
    assert "deleted successfully" in data["message"].lower()
    
    # Verify file is deleted
    info_response_after = client.get(f"/api/files/{file_id}/info")
    assert info_response_after.status_code == 404


def test_get_file_info():
    """Test getting file metadata without downloading"""
    # Upload a file first
    test_file_content = b"info test content"
    files = {"file": ("info_test.pdf", test_file_content, "application/pdf")}
    upload_response = client.post("/api/files/upload", files=files)
    assert upload_response.status_code == 201
    
    file_id = upload_response.json()["id"]
    
    # Get file info
    response = client.get(f"/api/files/{file_id}/info")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == file_id
    assert data["original_filename"] == "info_test.pdf"
    assert data["file_size"] == len(test_file_content)
    assert "mime_type" in data
    assert "upload_date" in data


def test_file_size_limit():
    """Test that files exceeding 10MB are rejected"""
    # Create a file larger than 10MB
    large_content = b"x" * (11 * 1024 * 1024)  # 11MB
    files = {"file": ("large_file.txt", large_content, "text/plain")}
    
    response = client.post("/api/files/upload", files=files)
    
    assert response.status_code == 413
    data = response.json()
    assert "exceeds maximum" in data["detail"].lower()


def test_path_traversal_prevention():
    """Test that path traversal attacks are prevented"""
    # Try to upload a file with path traversal in filename
    test_file_content = b"malicious content"
    files = {"file": ("../../../etc/passwd", test_file_content, "text/plain")}
    
    response = client.post("/api/files/upload", files=files)
    
    # Should sanitize the filename
    assert response.status_code == 201
    data = response.json()
    # Filename should be sanitized (no path components)
    assert ".." not in data["original_filename"]
    assert "/" not in data["original_filename"]
    assert "\\" not in data["original_filename"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

