import pytest
import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi.testclient import TestClient
from backend.main import app, UPLOAD_DIR, METADATA_FILE, load_metadata

# Create a test client
client = TestClient(app)

# Test fixtures
@pytest.fixture
def sample_image_file():
    """Create a sample image file for testing."""
    # Create a minimal PNG file (1x1 pixel)
    png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
    return ("test.png", png_data, "image/png")


@pytest.fixture
def sample_text_file():
    """Create a sample text file for testing."""
    text_data = b"Hello, this is a test file!"
    return ("test.txt", text_data, "text/plain")


@pytest.fixture
def sample_pdf_file():
    """Create a sample PDF file for testing."""
    # Minimal valid PDF
    pdf_data = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"
    return ("test.pdf", pdf_data, "application/pdf")


@pytest.fixture
def sample_invalid_file():
    """Create a sample invalid file (executable) for testing."""
    exe_data = b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00"
    return ("test.exe", exe_data, "application/x-msdownload")


class TestFileUpload:
    """Test file upload functionality."""
    
    def test_upload_valid_image(self, sample_image_file):
        """Test uploading a valid image file."""
        filename, content, mime_type = sample_image_file
        
        response = client.post(
            "/api/files/upload",
            files={"file": (filename, content, mime_type)}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["original_filename"] == filename
        assert data["file_size"] == len(content)
        assert data["mime_type"] == mime_type
        assert "id" in data
        assert "upload_date" in data
        assert "stored_filename" in data
        
        # Verify file exists on disk
        stored_path = UPLOAD_DIR / data["stored_filename"]
        assert stored_path.exists()
        
        # Cleanup
        if stored_path.exists():
            stored_path.unlink()
        metadata = load_metadata()
        if data["id"] in metadata:
            del metadata[data["id"]]
            with open(METADATA_FILE, "w") as f:
                json.dump(metadata, f)
    
    def test_upload_valid_text_file(self, sample_text_file):
        """Test uploading a valid text file."""
        filename, content, mime_type = sample_text_file
        
        response = client.post(
            "/api/files/upload",
            files={"file": (filename, content, mime_type)}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["original_filename"] == filename
        assert data["file_size"] == len(content)
        
        # Cleanup
        stored_path = UPLOAD_DIR / data["stored_filename"]
        if stored_path.exists():
            stored_path.unlink()
        metadata = load_metadata()
        if data["id"] in metadata:
            del metadata[data["id"]]
            with open(METADATA_FILE, "w") as f:
                json.dump(metadata, f)
    
    def test_upload_valid_pdf(self, sample_pdf_file):
        """Test uploading a valid PDF file."""
        filename, content, mime_type = sample_pdf_file
        
        response = client.post(
            "/api/files/upload",
            files={"file": (filename, content, mime_type)}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["original_filename"] == filename
        
        # Cleanup
        stored_path = UPLOAD_DIR / data["stored_filename"]
        if stored_path.exists():
            stored_path.unlink()
        metadata = load_metadata()
        if data["id"] in metadata:
            del metadata[data["id"]]
            with open(METADATA_FILE, "w") as f:
                json.dump(metadata, f)
    
    def test_upload_invalid_file_type(self, sample_invalid_file):
        """Test that invalid file types are rejected."""
        filename, content, mime_type = sample_invalid_file
        
        response = client.post(
            "/api/files/upload",
            files={"file": (filename, content, mime_type)}
        )
        
        assert response.status_code == 400
        assert "not allowed" in response.json()["detail"].lower()
    
    def test_upload_file_too_large(self):
        """Test that files exceeding 10MB are rejected."""
        # Create a file larger than 10MB
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        
        response = client.post(
            "/api/files/upload",
            files={"file": ("large.txt", large_content, "text/plain")}
        )
        
        assert response.status_code == 413
        assert "exceeds" in response.json()["detail"].lower()


class TestFileListing:
    """Test file listing functionality."""
    
    def test_list_files_empty(self):
        """Test listing files when no files are uploaded."""
        # Clear metadata
        with open(METADATA_FILE, "w") as f:
            json.dump({}, f)
        
        response = client.get("/api/files/")
        assert response.status_code == 200
        data = response.json()
        assert "files" in data
        assert isinstance(data["files"], list)
    
    def test_list_files_with_uploads(self, sample_image_file):
        """Test listing files after uploading."""
        filename, content, mime_type = sample_image_file
        
        # Upload a file
        upload_response = client.post(
            "/api/files/upload",
            files={"file": (filename, content, mime_type)}
        )
        assert upload_response.status_code == 201
        uploaded_file_id = upload_response.json()["id"]
        
        # List files
        response = client.get("/api/files/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["files"]) > 0
        assert any(f["id"] == uploaded_file_id for f in data["files"])
        
        # Cleanup
        stored_path = UPLOAD_DIR / upload_response.json()["stored_filename"]
        if stored_path.exists():
            stored_path.unlink()
        metadata = load_metadata()
        if uploaded_file_id in metadata:
            del metadata[uploaded_file_id]
            with open(METADATA_FILE, "w") as f:
                json.dump(metadata, f)


class TestFileDownload:
    """Test file download functionality."""
    
    def test_download_file(self, sample_text_file):
        """Test downloading an uploaded file."""
        filename, content, mime_type = sample_text_file
        
        # Upload a file
        upload_response = client.post(
            "/api/files/upload",
            files={"file": (filename, content, mime_type)}
        )
        assert upload_response.status_code == 201
        file_id = upload_response.json()["id"]
        
        # Download the file
        response = client.get(f"/api/files/{file_id}")
        assert response.status_code == 200
        assert response.content == content
        
        # Cleanup
        stored_path = UPLOAD_DIR / upload_response.json()["stored_filename"]
        if stored_path.exists():
            stored_path.unlink()
        metadata = load_metadata()
        if file_id in metadata:
            del metadata[file_id]
            with open(METADATA_FILE, "w") as f:
                json.dump(metadata, f)
    
    def test_download_nonexistent_file(self):
        """Test downloading a file that doesn't exist."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/files/{fake_id}")
        assert response.status_code == 404


class TestFileDeletion:
    """Test file deletion functionality."""
    
    def test_delete_file(self, sample_image_file):
        """Test deleting an uploaded file."""
        filename, content, mime_type = sample_image_file
        
        # Upload a file
        upload_response = client.post(
            "/api/files/upload",
            files={"file": (filename, content, mime_type)}
        )
        assert upload_response.status_code == 201
        file_id = upload_response.json()["id"]
        stored_filename = upload_response.json()["stored_filename"]
        
        # Verify file exists
        stored_path = UPLOAD_DIR / stored_filename
        assert stored_path.exists()
        
        # Delete the file
        response = client.delete(f"/api/files/{file_id}")
        assert response.status_code == 200
        assert "deleted" in response.json()["message"].lower()
        
        # Verify file is deleted from disk
        assert not stored_path.exists()
        
        # Verify metadata is removed
        metadata = load_metadata()
        assert file_id not in metadata
    
    def test_delete_nonexistent_file(self):
        """Test deleting a file that doesn't exist."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.delete(f"/api/files/{fake_id}")
        assert response.status_code == 404


class TestFileInfo:
    """Test file info endpoint."""
    
    def test_get_file_info(self, sample_text_file):
        """Test getting file metadata without downloading."""
        filename, content, mime_type = sample_text_file
        
        # Upload a file
        upload_response = client.post(
            "/api/files/upload",
            files={"file": (filename, content, mime_type)}
        )
        assert upload_response.status_code == 201
        file_id = upload_response.json()["id"]
        
        # Get file info
        response = client.get(f"/api/files/{file_id}/info")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == file_id
        assert data["original_filename"] == filename
        assert data["file_size"] == len(content)
        assert "upload_date" in data
        
        # Cleanup
        stored_path = UPLOAD_DIR / upload_response.json()["stored_filename"]
        if stored_path.exists():
            stored_path.unlink()
        metadata = load_metadata()
        if file_id in metadata:
            del metadata[file_id]
            with open(METADATA_FILE, "w") as f:
                json.dump(metadata, f)
    
    def test_get_info_nonexistent_file(self):
        """Test getting info for a file that doesn't exist."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/files/{fake_id}/info")
        assert response.status_code == 404


