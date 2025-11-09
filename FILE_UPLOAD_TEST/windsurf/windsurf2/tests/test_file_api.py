import pytest
import os
import json
import tempfile
import shutil
from pathlib import Path
from fastapi.testclient import TestClient
from io import BytesIO
import sys

# Add the backend directory to the path so we can import the main module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app, UPLOAD_DIR, METADATA_FILE

class TestFileAPI:
    @pytest.fixture(scope="function")
    def client(self):
        """Create a test client with temporary directories."""
        # Create temporary directories for testing
        self.temp_dir = tempfile.mkdtemp()
        self.temp_upload_dir = Path(self.temp_dir) / "uploads"
        self.temp_metadata_file = Path(self.temp_dir) / "file_metadata.json"
        
        # Patch the global variables
        import main
        self.original_upload_dir = main.UPLOAD_DIR
        self.original_metadata_file = main.METADATA_FILE
        
        main.UPLOAD_DIR = self.temp_upload_dir
        main.METADATA_FILE = self.temp_metadata_file
        
        # Create upload directory
        self.temp_upload_dir.mkdir(exist_ok=True)
        
        client = TestClient(app)
        yield client
        
        # Cleanup
        main.UPLOAD_DIR = self.original_upload_dir
        main.METADATA_FILE = self.original_metadata_file
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_file(self, filename: str, content: bytes, content_type: str = "text/plain"):
        """Helper method to create test files."""
        return ("file", (filename, BytesIO(content), content_type))

    def test_root_endpoint(self, client):
        """Test the root endpoint returns API information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "endpoints" in data
        assert data["message"] == "File Upload & Management API"

    def test_upload_valid_text_file(self, client):
        """Test uploading a valid text file."""
        test_content = b"This is a test text file content."
        files = {"file": ("test.txt", BytesIO(test_content), "text/plain")}
        
        response = client.post("/api/files/upload", files=files)
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert data["original_filename"] == "test.txt"
        assert data["file_size"] == len(test_content)
        assert data["mime_type"] == "text/plain"
        assert "upload_date" in data

    def test_upload_valid_image_file(self, client):
        """Test uploading a valid image file."""
        # Create a minimal PNG file (1x1 pixel)
        png_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
        files = {"file": ("test.png", BytesIO(png_content), "image/png")}
        
        response = client.post("/api/files/upload", files=files)
        assert response.status_code == 200
        
        data = response.json()
        assert data["original_filename"] == "test.png"
        assert data["mime_type"] == "image/png"

    def test_upload_invalid_file_type(self, client):
        """Test uploading an invalid file type (should be rejected)."""
        test_content = b"This is an executable file."
        files = {"file": ("malware.exe", BytesIO(test_content), "application/x-executable")}
        
        response = client.post("/api/files/upload", files=files)
        assert response.status_code == 400
        assert "File type not allowed" in response.json()["detail"]

    def test_upload_file_too_large(self, client):
        """Test uploading a file that exceeds the size limit."""
        # Create a file larger than 10MB
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        files = {"file": ("large.txt", BytesIO(large_content), "text/plain")}
        
        response = client.post("/api/files/upload", files=files)
        assert response.status_code == 413
        assert "File too large" in response.json()["detail"]

    def test_filename_sanitization(self, client):
        """Test that dangerous filenames are properly sanitized."""
        test_content = b"Test content"
        dangerous_filename = "../../../etc/passwd"
        files = {"file": (dangerous_filename, BytesIO(test_content), "text/plain")}
        
        response = client.post("/api/files/upload", files=files)
        assert response.status_code == 200
        
        data = response.json()
        # The original filename should be preserved, but the stored filename should be safe
        assert data["original_filename"] == dangerous_filename
        assert "../" not in data["stored_filename"]
        assert "passwd" in data["stored_filename"]  # Should keep the base name

    def test_list_files_empty(self, client):
        """Test listing files when no files are uploaded."""
        response = client.get("/api/files/")
        assert response.status_code == 200
        
        data = response.json()
        assert "files" in data
        assert len(data["files"]) == 0

    def test_list_files_with_uploads(self, client):
        """Test listing files after uploading some files."""
        # Upload two test files
        files1 = {"file": ("test1.txt", BytesIO(b"Content 1"), "text/plain")}
        files2 = {"file": ("test2.txt", BytesIO(b"Content 2"), "text/plain")}
        
        response1 = client.post("/api/files/upload", files=files1)
        response2 = client.post("/api/files/upload", files=files2)
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # List files
        response = client.get("/api/files/")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["files"]) == 2
        
        filenames = [f["original_filename"] for f in data["files"]]
        assert "test1.txt" in filenames
        assert "test2.txt" in filenames

    def test_download_file(self, client):
        """Test downloading an uploaded file."""
        test_content = b"This is test content for download."
        files = {"file": ("download_test.txt", BytesIO(test_content), "text/plain")}
        
        # Upload file
        upload_response = client.post("/api/files/upload", files=files)
        assert upload_response.status_code == 200
        
        file_id = upload_response.json()["id"]
        
        # Download file
        download_response = client.get(f"/api/files/{file_id}")
        assert download_response.status_code == 200
        assert download_response.content == test_content
        
        # Check headers
        assert download_response.headers["content-type"] == "text/plain; charset=utf-8"

    def test_download_nonexistent_file(self, client):
        """Test downloading a file that doesn't exist."""
        fake_id = "nonexistent-file-id"
        response = client.get(f"/api/files/{fake_id}")
        assert response.status_code == 404
        assert "File not found" in response.json()["detail"]

    def test_get_file_info(self, client):
        """Test getting file metadata without downloading."""
        test_content = b"Test content for info"
        files = {"file": ("info_test.txt", BytesIO(test_content), "text/plain")}
        
        # Upload file
        upload_response = client.post("/api/files/upload", files=files)
        assert upload_response.status_code == 200
        
        file_id = upload_response.json()["id"]
        
        # Get file info
        info_response = client.get(f"/api/files/{file_id}/info")
        assert info_response.status_code == 200
        
        data = info_response.json()
        assert data["id"] == file_id
        assert data["original_filename"] == "info_test.txt"
        assert data["file_size"] == len(test_content)
        assert data["mime_type"] == "text/plain"

    def test_get_info_nonexistent_file(self, client):
        """Test getting info for a file that doesn't exist."""
        fake_id = "nonexistent-file-id"
        response = client.get(f"/api/files/{fake_id}/info")
        assert response.status_code == 404
        assert "File not found" in response.json()["detail"]

    def test_delete_file(self, client):
        """Test deleting an uploaded file."""
        test_content = b"Content to be deleted"
        files = {"file": ("delete_test.txt", BytesIO(test_content), "text/plain")}
        
        # Upload file
        upload_response = client.post("/api/files/upload", files=files)
        assert upload_response.status_code == 200
        
        file_id = upload_response.json()["id"]
        
        # Verify file exists
        info_response = client.get(f"/api/files/{file_id}/info")
        assert info_response.status_code == 200
        
        # Delete file
        delete_response = client.delete(f"/api/files/{file_id}")
        assert delete_response.status_code == 200
        
        delete_data = delete_response.json()
        assert delete_data["file_id"] == file_id
        assert "deleted successfully" in delete_data["message"]
        
        # Verify file no longer exists
        info_response = client.get(f"/api/files/{file_id}/info")
        assert info_response.status_code == 404

    def test_delete_nonexistent_file(self, client):
        """Test deleting a file that doesn't exist."""
        fake_id = "nonexistent-file-id"
        response = client.delete(f"/api/files/{fake_id}")
        assert response.status_code == 404
        assert "File not found" in response.json()["detail"]

    def test_upload_pdf_file(self, client):
        """Test uploading a PDF file."""
        # Minimal PDF content
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000074 00000 n \n0000000120 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n179\n%%EOF"
        files = {"file": ("test.pdf", BytesIO(pdf_content), "application/pdf")}
        
        response = client.post("/api/files/upload", files=files)
        assert response.status_code == 200
        
        data = response.json()
        assert data["original_filename"] == "test.pdf"
        assert data["mime_type"] == "application/pdf"

    def test_upload_json_file(self, client):
        """Test uploading a JSON file."""
        json_content = b'{"test": "data", "number": 42}'
        files = {"file": ("test.json", BytesIO(json_content), "application/json")}
        
        response = client.post("/api/files/upload", files=files)
        assert response.status_code == 200
        
        data = response.json()
        assert data["original_filename"] == "test.json"
        assert data["mime_type"] == "application/json"

    def test_path_traversal_prevention(self, client):
        """Test that path traversal attacks are prevented."""
        test_content = b"Malicious content"
        malicious_filenames = [
            "../../etc/passwd",
            "..\\..\\windows\\system32\\config\\sam",
            "/etc/shadow",
            "C:\\Windows\\System32\\config\\SAM"
        ]
        
        for filename in malicious_filenames:
            files = {"file": (filename, BytesIO(test_content), "text/plain")}
            response = client.post("/api/files/upload", files=files)
            
            if response.status_code == 200:
                data = response.json()
                stored_filename = data["stored_filename"]
                
                # Ensure the stored filename doesn't contain path traversal sequences
                assert ".." not in stored_filename
                assert "/" not in stored_filename or not stored_filename.startswith("/")
                assert "\\" not in stored_filename or not stored_filename.startswith("\\")

    def test_empty_filename_handling(self, client):
        """Test handling of files with generic or missing filenames."""
        test_content = b"Content with no proper filename"
        # Use a generic filename without extension to test filename handling
        files = {"file": ("unknown_file", BytesIO(test_content), "text/plain")}
        
        response = client.post("/api/files/upload", files=files)
        assert response.status_code == 200
        
        data = response.json()
        # Should generate a proper stored filename
        assert data["stored_filename"] != ""
        assert len(data["stored_filename"]) > 0
        assert data["original_filename"] == "unknown_file"
        # The stored filename should include the UUID prefix
        assert data["id"] in data["stored_filename"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
