import pytest
import os
import json
import tempfile
import shutil
from pathlib import Path
from fastapi.testclient import TestClient
from io import BytesIO
import sys

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app, UPLOAD_DIR, METADATA_FILE

class TestFileAPI:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and teardown for each test."""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.original_upload_dir = UPLOAD_DIR
        self.original_metadata_file = METADATA_FILE
        
        # Override the upload directory and metadata file for testing
        import main
        main.UPLOAD_DIR = Path(self.test_dir) / "uploads"
        main.METADATA_FILE = Path(self.test_dir) / "file_metadata.json"
        main.UPLOAD_DIR.mkdir(exist_ok=True)
        
        self.client = TestClient(app)
        
        yield
        
        # Cleanup
        shutil.rmtree(self.test_dir, ignore_errors=True)
        main.UPLOAD_DIR = self.original_upload_dir
        main.METADATA_FILE = self.original_metadata_file

    def create_test_file(self, filename: str, content: bytes, content_type: str = "text/plain"):
        """Helper method to create a test file for upload."""
        return ("file", (filename, BytesIO(content), content_type))

    def test_upload_valid_text_file(self):
        """Test uploading a valid text file."""
        test_content = b"This is a test file content."
        files = {"file": ("test.txt", BytesIO(test_content), "text/plain")}
        
        response = self.client.post("/api/files/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert data["original_filename"] == "test.txt"
        assert data["file_size"] == len(test_content)
        assert data["mime_type"] == "text/plain"
        assert "upload_date" in data
        assert "stored_filename" in data

    def test_upload_valid_image_file(self):
        """Test uploading a valid image file."""
        # Create a minimal PNG file (1x1 pixel)
        png_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
        files = {"file": ("test.png", BytesIO(png_content), "image/png")}
        
        response = self.client.post("/api/files/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["original_filename"] == "test.png"
        assert data["mime_type"] == "image/png"

    def test_upload_invalid_file_type(self):
        """Test uploading an invalid file type (should be rejected)."""
        test_content = b"This is an executable file."
        files = {"file": ("malware.exe", BytesIO(test_content), "application/x-executable")}
        
        response = self.client.post("/api/files/upload", files=files)
        
        assert response.status_code == 400
        assert "File type not allowed" in response.json()["detail"]

    def test_upload_file_too_large(self):
        """Test uploading a file that exceeds the size limit."""
        # Create a file larger than 10MB
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        files = {"file": ("large.txt", BytesIO(large_content), "text/plain")}
        
        response = self.client.post("/api/files/upload", files=files)
        
        assert response.status_code == 413
        assert "File too large" in response.json()["detail"]

    def test_filename_sanitization(self):
        """Test that dangerous filenames are properly sanitized."""
        dangerous_filename = "../../../etc/passwd.txt"  # Need .txt extension for validation
        test_content = b"malicious content"
        files = {"file": (dangerous_filename, BytesIO(test_content), "text/plain")}
        
        response = self.client.post("/api/files/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        # The original filename should be preserved in metadata
        assert data["original_filename"] == dangerous_filename
        # But the stored filename should be sanitized (UUID-based)
        assert not data["stored_filename"].startswith("../")
        assert data["stored_filename"].endswith(".txt")  # Should preserve extension

    def test_list_files_empty(self):
        """Test listing files when no files are uploaded."""
        response = self.client.get("/api/files/")
        
        assert response.status_code == 200
        data = response.json()
        assert "files" in data
        assert len(data["files"]) == 0

    def test_list_files_with_uploads(self):
        """Test listing files after uploading some files."""
        # Upload two test files
        files1 = {"file": ("test1.txt", BytesIO(b"content1"), "text/plain")}
        files2 = {"file": ("test2.txt", BytesIO(b"content2"), "text/plain")}
        
        response1 = self.client.post("/api/files/upload", files=files1)
        response2 = self.client.post("/api/files/upload", files=files2)
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # List files
        response = self.client.get("/api/files/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["files"]) == 2
        
        filenames = [f["original_filename"] for f in data["files"]]
        assert "test1.txt" in filenames
        assert "test2.txt" in filenames

    def test_download_file(self):
        """Test downloading an uploaded file."""
        test_content = b"This is test content for download."
        files = {"file": ("download_test.txt", BytesIO(test_content), "text/plain")}
        
        # Upload file
        upload_response = self.client.post("/api/files/upload", files=files)
        assert upload_response.status_code == 200
        file_id = upload_response.json()["id"]
        
        # Download file
        download_response = self.client.get(f"/api/files/{file_id}")
        
        assert download_response.status_code == 200
        assert download_response.content == test_content
        assert download_response.headers["content-type"] == "text/plain; charset=utf-8"

    def test_download_nonexistent_file(self):
        """Test downloading a file that doesn't exist."""
        fake_id = "nonexistent-file-id"
        response = self.client.get(f"/api/files/{fake_id}")
        
        assert response.status_code == 404
        assert "File not found" in response.json()["detail"]

    def test_delete_file(self):
        """Test deleting an uploaded file."""
        test_content = b"This file will be deleted."
        files = {"file": ("delete_test.txt", BytesIO(test_content), "text/plain")}
        
        # Upload file
        upload_response = self.client.post("/api/files/upload", files=files)
        assert upload_response.status_code == 200
        file_id = upload_response.json()["id"]
        
        # Verify file exists
        list_response = self.client.get("/api/files/")
        assert len(list_response.json()["files"]) == 1
        
        # Delete file
        delete_response = self.client.delete(f"/api/files/{file_id}")
        
        assert delete_response.status_code == 200
        assert delete_response.json()["file_id"] == file_id
        
        # Verify file is gone
        list_response = self.client.get("/api/files/")
        assert len(list_response.json()["files"]) == 0
        
        # Verify download fails
        download_response = self.client.get(f"/api/files/{file_id}")
        assert download_response.status_code == 404

    def test_delete_nonexistent_file(self):
        """Test deleting a file that doesn't exist."""
        fake_id = "nonexistent-file-id"
        response = self.client.delete(f"/api/files/{fake_id}")
        
        assert response.status_code == 404
        assert "File not found" in response.json()["detail"]

    def test_get_file_info(self):
        """Test getting file metadata without downloading."""
        test_content = b"This is test content for info."
        files = {"file": ("info_test.txt", BytesIO(test_content), "text/plain")}
        
        # Upload file
        upload_response = self.client.post("/api/files/upload", files=files)
        assert upload_response.status_code == 200
        file_id = upload_response.json()["id"]
        
        # Get file info
        info_response = self.client.get(f"/api/files/{file_id}/info")
        
        assert info_response.status_code == 200
        data = info_response.json()
        
        assert data["id"] == file_id
        assert data["original_filename"] == "info_test.txt"
        assert data["file_size"] == len(test_content)
        assert data["mime_type"] == "text/plain"
        assert "upload_date" in data

    def test_get_info_nonexistent_file(self):
        """Test getting info for a file that doesn't exist."""
        fake_id = "nonexistent-file-id"
        response = self.client.get(f"/api/files/{fake_id}/info")
        
        assert response.status_code == 404
        assert "File not found" in response.json()["detail"]

    def test_root_endpoint(self):
        """Test the root endpoint returns API information."""
        response = self.client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "endpoints" in data
        assert "upload" in data["endpoints"]

    def test_path_traversal_prevention(self):
        """Test that path traversal attacks are prevented."""
        malicious_filenames = [
            "../../etc/passwd.txt",
            "..\\..\\windows\\system32\\config\\sam.txt",
            "/etc/shadow.txt",
            "C:\\Windows\\System32\\config\\SAM.txt"
        ]
        
        for filename in malicious_filenames:
            test_content = b"malicious content"
            files = {"file": (filename, BytesIO(test_content), "text/plain")}
            
            response = self.client.post("/api/files/upload", files=files)
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify the stored filename doesn't contain path traversal
            stored_filename = data["stored_filename"]
            assert not stored_filename.startswith("../")
            assert not stored_filename.startswith("..\\")
            assert not stored_filename.startswith("/")
            assert ":" not in stored_filename or stored_filename.count(":") == 0  # No drive letters

    def test_special_characters_in_filename(self):
        """Test handling of special characters in filenames."""
        special_filename = 'test<>:"/\\|?*file.txt'
        test_content = b"content with special chars in filename"
        files = {"file": (special_filename, BytesIO(test_content), "text/plain")}
        
        response = self.client.post("/api/files/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        
        # Original filename should be preserved (may have URL encoding)
        assert 'test' in data["original_filename"]
        assert 'file.txt' in data["original_filename"]
        # Stored filename should be UUID-based and sanitized
        stored_filename = data["stored_filename"]
        assert stored_filename.endswith(".txt")
        # Should not contain dangerous characters in the UUID part
        dangerous_chars = '<>|?*'
        for char in dangerous_chars:
            assert char not in stored_filename

    def test_empty_filename(self):
        """Test handling of empty or invalid filenames."""
        test_content = b"content with no filename"
        files = {"file": ("", BytesIO(test_content), "text/plain")}
        
        response = self.client.post("/api/files/upload", files=files)
        
        # Empty filename should be rejected
        assert response.status_code == 422
        # FastAPI validation error format
        error_data = response.json()
        assert "detail" in error_data

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
