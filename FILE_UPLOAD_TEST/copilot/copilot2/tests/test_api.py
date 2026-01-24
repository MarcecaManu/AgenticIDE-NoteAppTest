import pytest
import asyncio
import json
import tempfile
import shutil
from pathlib import Path
from fastapi.testclient import TestClient
from io import BytesIO
import os
import sys

# Add the backend directory to the path so we can import main
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from main import app, UPLOAD_DIR, METADATA_FILE, load_metadata, save_metadata

class TestFileUploadAPI:
    @pytest.fixture(scope="function")
    def setup_test_environment(self):
        """Set up a clean test environment for each test"""
        # Create a temporary directory for test uploads
        self.test_upload_dir = Path(tempfile.mkdtemp())
        self.test_metadata_file = self.test_upload_dir / "test_metadata.json"
        
        # Patch the global variables
        import main
        self.original_upload_dir = main.UPLOAD_DIR
        self.original_metadata_file = main.METADATA_FILE
        
        main.UPLOAD_DIR = self.test_upload_dir
        main.METADATA_FILE = self.test_metadata_file
        
        # Create test client
        self.client = TestClient(app)
        
        yield
        
        # Cleanup after test
        main.UPLOAD_DIR = self.original_upload_dir
        main.METADATA_FILE = self.original_metadata_file
        
        if self.test_upload_dir.exists():
            shutil.rmtree(self.test_upload_dir)

    def create_test_file(self, filename: str, content: bytes, mime_type: str = "text/plain"):
        """Helper method to create test files"""
        return ("file", (filename, BytesIO(content), mime_type))

    def test_upload_valid_text_file(self, setup_test_environment):
        """Test uploading a valid text file"""
        test_content = b"This is a test text file content."
        files = [self.create_test_file("test.txt", test_content, "text/plain")]
        
        response = self.client.post("/api/files/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert data["original_filename"] == "test.txt"
        assert data["file_size"] == len(test_content)
        assert data["mime_type"] == "text/plain"
        assert "upload_date" in data
        assert "stored_filename" in data

    def test_upload_valid_image_file(self, setup_test_environment):
        """Test uploading a valid image file"""
        # Create a minimal valid JPEG header (simplified for testing)
        jpeg_content = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00"
        files = [self.create_test_file("test.jpg", jpeg_content, "image/jpeg")]
        
        response = self.client.post("/api/files/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["original_filename"] == "test.jpg"
        assert data["mime_type"] == "image/jpeg"

    def test_upload_invalid_file_type(self, setup_test_environment):
        """Test uploading an invalid file type (executable)"""
        test_content = b"MZ\x90\x00"  # PE executable header
        files = [self.create_test_file("malware.exe", test_content, "application/x-executable")]
        
        response = self.client.post("/api/files/upload", files=files)
        
        assert response.status_code == 400
        assert "Invalid file type" in response.json()["detail"]

    def test_upload_file_too_large(self, setup_test_environment):
        """Test uploading a file that's too large"""
        # Create a file larger than 10MB
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        files = [self.create_test_file("large.txt", large_content, "text/plain")]
        
        response = self.client.post("/api/files/upload", files=files)
        
        assert response.status_code == 413
        assert "File size exceeds 10MB limit" in response.json()["detail"]

    def test_upload_dangerous_filename(self, setup_test_environment):
        """Test uploading a file with a dangerous filename"""
        test_content = b"malicious content"
        files = [self.create_test_file("../../../etc/passwd.txt", test_content, "text/plain")]
        
        response = self.client.post("/api/files/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        
        # The filename should be sanitized
        assert "../" not in data["stored_filename"]
        assert "passwd.txt" in data["original_filename"]  # Original name preserved
        
    def test_list_files_empty(self, setup_test_environment):
        """Test listing files when no files are uploaded"""
        response = self.client.get("/api/files/")
        
        assert response.status_code == 200
        assert response.json() == []

    def test_list_files_with_uploads(self, setup_test_environment):
        """Test listing files after uploading some files"""
        # Upload two test files
        files1 = [self.create_test_file("test1.txt", b"content1", "text/plain")]
        files2 = [self.create_test_file("test2.txt", b"content2", "text/plain")]
        
        self.client.post("/api/files/upload", files=files1)
        self.client.post("/api/files/upload", files=files2)
        
        response = self.client.get("/api/files/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) == 2
        filenames = [f["original_filename"] for f in data]
        assert "test1.txt" in filenames
        assert "test2.txt" in filenames

    def test_download_file(self, setup_test_environment):
        """Test downloading a file"""
        # Upload a test file
        test_content = b"Download test content"
        files = [self.create_test_file("download_test.txt", test_content, "text/plain")]
        
        upload_response = self.client.post("/api/files/upload", files=files)
        file_id = upload_response.json()["id"]
        
        # Download the file
        download_response = self.client.get(f"/api/files/{file_id}")
        
        assert download_response.status_code == 200
        assert download_response.content == test_content
        assert "download_test.txt" in download_response.headers.get("content-disposition", "")

    def test_download_nonexistent_file(self, setup_test_environment):
        """Test downloading a file that doesn't exist"""
        fake_id = "nonexistent-file-id"
        
        response = self.client.get(f"/api/files/{fake_id}")
        
        assert response.status_code == 404
        assert "File not found" in response.json()["detail"]

    def test_delete_file(self, setup_test_environment):
        """Test deleting a file"""
        # Upload a test file
        test_content = b"Delete test content"
        files = [self.create_test_file("delete_test.txt", test_content, "text/plain")]
        
        upload_response = self.client.post("/api/files/upload", files=files)
        file_id = upload_response.json()["id"]
        
        # Verify file exists
        list_response = self.client.get("/api/files/")
        assert len(list_response.json()) == 1
        
        # Delete the file
        delete_response = self.client.delete(f"/api/files/{file_id}")
        
        assert delete_response.status_code == 200
        assert "deleted successfully" in delete_response.json()["message"]
        
        # Verify file is gone from list
        list_response = self.client.get("/api/files/")
        assert len(list_response.json()) == 0
        
        # Verify file can't be downloaded
        download_response = self.client.get(f"/api/files/{file_id}")
        assert download_response.status_code == 404

    def test_delete_nonexistent_file(self, setup_test_environment):
        """Test deleting a file that doesn't exist"""
        fake_id = "nonexistent-file-id"
        
        response = self.client.delete(f"/api/files/{fake_id}")
        
        assert response.status_code == 404
        assert "File not found" in response.json()["detail"]

    def test_get_file_info(self, setup_test_environment):
        """Test getting file metadata without downloading"""
        # Upload a test file
        test_content = b"Info test content"
        files = [self.create_test_file("info_test.txt", test_content, "text/plain")]
        
        upload_response = self.client.post("/api/files/upload", files=files)
        file_data = upload_response.json()
        file_id = file_data["id"]
        
        # Get file info
        info_response = self.client.get(f"/api/files/{file_id}/info")
        
        assert info_response.status_code == 200
        info_data = info_response.json()
        
        assert info_data["id"] == file_id
        assert info_data["original_filename"] == "info_test.txt"
        assert info_data["file_size"] == len(test_content)
        assert info_data["mime_type"] == "text/plain"
        assert "upload_date" in info_data

    def test_get_info_nonexistent_file(self, setup_test_environment):
        """Test getting info for a file that doesn't exist"""
        fake_id = "nonexistent-file-id"
        
        response = self.client.get(f"/api/files/{fake_id}/info")
        
        assert response.status_code == 404
        assert "File not found" in response.json()["detail"]

    def test_filename_sanitization(self, setup_test_environment):
        """Test that filenames are properly sanitized"""
        dangerous_names = [
            "../../../etc/passwd.txt",
            "file<script>alert('xss')</script>.txt",
            "file\x00null.txt",
            "CON.txt",  # Windows reserved name
            "file|pipe.txt"
        ]
        
        for dangerous_name in dangerous_names:
            test_content = b"test content"
            files = [self.create_test_file(dangerous_name, test_content, "text/plain")]
            
            response = self.client.post("/api/files/upload", files=files)
            
            assert response.status_code == 200
            data = response.json()
            
            # Check that stored filename is safe
            stored_name = data["stored_filename"]
            assert "../" not in stored_name
            assert "<" not in stored_name
            assert ">" not in stored_name
            assert "\x00" not in stored_name
            assert "|" not in stored_name

    def test_api_health_check(self, setup_test_environment):
        """Test the root endpoint for API health"""
        response = self.client.get("/")
        
        assert response.status_code == 200
        assert "File Upload & Management API is running" in response.json()["message"]

    def test_multiple_files_persistence(self, setup_test_environment):
        """Test that metadata persistence works correctly with multiple operations"""
        # Upload multiple files
        files_data = []
        for i in range(3):
            content = f"Content for file {i}".encode()
            files = [self.create_test_file(f"test_{i}.txt", content, "text/plain")]
            
            response = self.client.post("/api/files/upload", files=files)
            assert response.status_code == 200
            files_data.append(response.json())
        
        # Verify all files are listed
        list_response = self.client.get("/api/files/")
        assert len(list_response.json()) == 3
        
        # Delete middle file
        delete_response = self.client.delete(f"/api/files/{files_data[1]['id']}")
        assert delete_response.status_code == 200
        
        # Verify correct files remain
        list_response = self.client.get("/api/files/")
        remaining_files = list_response.json()
        assert len(remaining_files) == 2
        
        remaining_ids = [f["id"] for f in remaining_files]
        assert files_data[0]["id"] in remaining_ids
        assert files_data[2]["id"] in remaining_ids
        assert files_data[1]["id"] not in remaining_ids

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])