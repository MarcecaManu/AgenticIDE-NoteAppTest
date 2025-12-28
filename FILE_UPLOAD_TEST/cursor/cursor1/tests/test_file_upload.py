import pytest
import os
import json
import shutil
from pathlib import Path
from fastapi.testclient import TestClient
from backend.main import app, UPLOAD_DIR, METADATA_FILE

# Setup test client
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Setup and teardown for each test"""
    # Create test upload directory
    UPLOAD_DIR.mkdir(exist_ok=True)
    
    # Clear metadata before each test
    if METADATA_FILE.exists():
        METADATA_FILE.unlink()
    
    yield
    
    # Cleanup after each test
    if UPLOAD_DIR.exists():
        shutil.rmtree(UPLOAD_DIR)
    if METADATA_FILE.exists():
        METADATA_FILE.unlink()


def test_upload_valid_file():
    """Test uploading a valid file (image)"""
    # Create a test image file
    test_file_content = b"fake image content"
    test_file = ("test_image.jpg", test_file_content, "image/jpeg")
    
    response = client.post(
        "/api/files/upload",
        files={"file": test_file}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "id" in data
    assert data["original_filename"] == "test_image.jpg"
    assert data["file_size"] == len(test_file_content)
    assert data["mime_type"] == "image/jpeg"
    assert "upload_date" in data
    
    # Verify file exists on disk
    stored_path = UPLOAD_DIR / data["stored_filename"]
    assert stored_path.exists()
    
    # Verify metadata was saved
    assert METADATA_FILE.exists()
    with open(METADATA_FILE, 'r') as f:
        metadata = json.load(f)
        assert data["id"] in metadata


def test_list_files():
    """Test listing all uploaded files"""
    # Upload two files
    file1 = ("test1.txt", b"content1", "text/plain")
    file2 = ("test2.pdf", b"content2", "application/pdf")
    
    client.post("/api/files/upload", files={"file": file1})
    client.post("/api/files/upload", files={"file": file2})
    
    # List files
    response = client.get("/api/files/")
    
    assert response.status_code == 200
    files = response.json()
    
    assert len(files) == 2
    filenames = [f["original_filename"] for f in files]
    assert "test1.txt" in filenames
    assert "test2.pdf" in filenames


def test_download_file():
    """Test downloading a specific file"""
    # Upload a file
    test_content = b"test file content for download"
    test_file = ("download_test.txt", test_content, "text/plain")
    
    upload_response = client.post("/api/files/upload", files={"file": test_file})
    file_id = upload_response.json()["id"]
    
    # Download the file
    response = client.get(f"/api/files/{file_id}")
    
    assert response.status_code == 200
    assert response.content == test_content
    assert "download_test.txt" in response.headers.get("content-disposition", "")


def test_delete_file():
    """Test deleting a file"""
    # Upload a file
    test_file = ("delete_test.txt", b"content to delete", "text/plain")
    upload_response = client.post("/api/files/upload", files={"file": test_file})
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
    with open(METADATA_FILE, 'r') as f:
        metadata = json.load(f)
        assert file_id not in metadata


def test_reject_invalid_file_type():
    """Test that invalid file types are rejected"""
    # Try to upload an executable file (not allowed)
    test_file = ("malicious.exe", b"executable content", "application/x-msdownload")
    
    response = client.post("/api/files/upload", files={"file": test_file})
    
    assert response.status_code == 400
    data = response.json()
    assert "not allowed" in data["detail"].lower()
    
    # Verify file was not saved
    assert not any(UPLOAD_DIR.iterdir())


def test_file_info_endpoint():
    """Test getting file metadata without downloading"""
    # Upload a file
    test_file = ("info_test.txt", b"test content", "text/plain")
    upload_response = client.post("/api/files/upload", files={"file": test_file})
    file_id = upload_response.json()["id"]
    
    # Get file info
    response = client.get(f"/api/files/{file_id}/info")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == file_id
    assert data["original_filename"] == "info_test.txt"
    assert "file_size" in data
    assert "mime_type" in data
    assert "upload_date" in data


def test_file_size_limit():
    """Test that files exceeding 10MB are rejected"""
    # Create a file larger than 10MB
    large_content = b"x" * (11 * 1024 * 1024)  # 11MB
    test_file = ("large_file.txt", large_content, "text/plain")
    
    response = client.post("/api/files/upload", files={"file": test_file})
    
    assert response.status_code == 400
    data = response.json()
    assert "size" in data["detail"].lower() or "exceed" in data["detail"].lower()


def test_filename_sanitization():
    """Test that dangerous filenames are sanitized"""
    # Try to upload a file with path traversal attempt
    dangerous_filename = "../../../etc/passwd"
    test_file = (dangerous_filename, b"content", "text/plain")
    
    response = client.post("/api/files/upload", files={"file": test_file})
    
    assert response.status_code == 200
    data = response.json()
    
    # Filename should be sanitized (no path components)
    assert ".." not in data["original_filename"]
    assert "/" not in data["original_filename"]
    assert "\\" not in data["original_filename"]


def test_nonexistent_file_download():
    """Test downloading a non-existent file returns 404"""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/files/{fake_id}")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_nonexistent_file_delete():
    """Test deleting a non-existent file returns 404"""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.delete(f"/api/files/{fake_id}")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

