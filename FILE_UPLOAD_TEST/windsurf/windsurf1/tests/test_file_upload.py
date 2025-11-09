import pytest
import asyncio
import os
import json
import tempfile
import shutil
from pathlib import Path
from fastapi.testclient import TestClient
from io import BytesIO

# Import the FastAPI app
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
from main import app, UPLOAD_DIR, METADATA_FILE

client = TestClient(app)

@pytest.fixture(scope="function")
def setup_test_environment():
    """Set up a clean test environment for each test"""
    # Create temporary directories for testing
    test_upload_dir = Path("test_uploads")
    test_metadata_file = Path("test_file_metadata.json")
    
    # Backup original paths
    original_upload_dir = app.state.upload_dir if hasattr(app.state, 'upload_dir') else UPLOAD_DIR
    original_metadata_file = app.state.metadata_file if hasattr(app.state, 'metadata_file') else METADATA_FILE
    
    # Set test paths
    app.state.upload_dir = test_upload_dir
    app.state.metadata_file = test_metadata_file
    
    # Update the module-level variables
    import main
    main.UPLOAD_DIR = test_upload_dir
    main.METADATA_FILE = test_metadata_file
    
    # Create test directories
    test_upload_dir.mkdir(exist_ok=True)
    
    yield
    
    # Cleanup after test
    if test_upload_dir.exists():
        shutil.rmtree(test_upload_dir)
    if test_metadata_file.exists():
        test_metadata_file.unlink()
    
    # Restore original paths
    main.UPLOAD_DIR = original_upload_dir
    main.METADATA_FILE = original_metadata_file

def create_test_file(filename: str, content: bytes, content_type: str):
    """Helper function to create test files"""
    return ("file", (filename, BytesIO(content), content_type))

class TestFileUpload:
    """Test file upload functionality"""
    
    def test_upload_valid_image_file(self, setup_test_environment):
        """Test uploading a valid image file"""
        # Create a small test image (PNG header)
        png_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
        
        files = {"file": ("test_image.png", BytesIO(png_content), "image/png")}
        response = client.post("/api/files/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["original_filename"] == "test_image.png"
        assert data["mime_type"] == "image/png"
        assert data["file_size"] == len(png_content)
        assert "upload_date" in data
    
    def test_upload_valid_pdf_file(self, setup_test_environment):
        """Test uploading a valid PDF file"""
        # Create a minimal PDF content
        pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n174\n%%EOF'
        
        files = {"file": ("test_document.pdf", BytesIO(pdf_content), "application/pdf")}
        response = client.post("/api/files/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["original_filename"] == "test_document.pdf"
        assert data["mime_type"] == "application/pdf"
    
    def test_upload_valid_text_file(self, setup_test_environment):
        """Test uploading a valid text file"""
        text_content = b"This is a test text file content."
        
        files = {"file": ("test_file.txt", BytesIO(text_content), "text/plain")}
        response = client.post("/api/files/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["original_filename"] == "test_file.txt"
        assert data["mime_type"] == "text/plain"
        assert data["file_size"] == len(text_content)
    
    def test_upload_invalid_file_type(self, setup_test_environment):
        """Test uploading an invalid file type (should be rejected)"""
        # Try to upload an executable file
        exe_content = b"MZ\x90\x00"  # PE header for Windows executable
        
        files = {"file": ("malicious.exe", BytesIO(exe_content), "application/octet-stream")}
        response = client.post("/api/files/upload", files=files)
        
        assert response.status_code == 400
        assert "File type not allowed" in response.json()["detail"]
    
    def test_upload_file_too_large(self, setup_test_environment):
        """Test uploading a file that exceeds size limit"""
        # Create a file larger than 10MB
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        
        files = {"file": ("large_file.txt", BytesIO(large_content), "text/plain")}
        response = client.post("/api/files/upload", files=files)
        
        assert response.status_code == 413
        assert "File too large" in response.json()["detail"]
    
    def test_filename_sanitization(self, setup_test_environment):
        """Test that dangerous filenames are sanitized"""
        text_content = b"Test content"
        dangerous_filename = "../../../etc/passwd.txt"
        
        files = {"file": (dangerous_filename, BytesIO(text_content), "text/plain")}
        response = client.post("/api/files/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        # Filename should be sanitized
        assert data["original_filename"] != dangerous_filename
        assert ".." not in data["original_filename"]
        assert "/" not in data["original_filename"]

class TestFileManagement:
    """Test file management operations"""
    
    def test_list_files_empty(self, setup_test_environment):
        """Test listing files when no files are uploaded"""
        response = client.get("/api/files/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_list_files_with_uploads(self, setup_test_environment):
        """Test listing files after uploading some files"""
        # Upload a test file first
        text_content = b"Test file content"
        files = {"file": ("test.txt", BytesIO(text_content), "text/plain")}
        upload_response = client.post("/api/files/upload", files=files)
        assert upload_response.status_code == 200
        
        # List files
        response = client.get("/api/files/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["original_filename"] == "test.txt"
        assert data[0]["mime_type"] == "text/plain"
    
    def test_download_file(self, setup_test_environment):
        """Test downloading an uploaded file"""
        # Upload a test file first
        text_content = b"Test file content for download"
        files = {"file": ("download_test.txt", BytesIO(text_content), "text/plain")}
        upload_response = client.post("/api/files/upload", files=files)
        assert upload_response.status_code == 200
        
        file_id = upload_response.json()["id"]
        
        # Download the file
        response = client.get(f"/api/files/{file_id}")
        
        assert response.status_code == 200
        assert response.content == text_content
        assert response.headers["content-type"] == "text/plain; charset=utf-8"
    
    def test_download_nonexistent_file(self, setup_test_environment):
        """Test downloading a file that doesn't exist"""
        fake_id = "nonexistent-file-id"
        response = client.get(f"/api/files/{fake_id}")
        
        assert response.status_code == 404
        assert "File not found" in response.json()["detail"]
    
    def test_get_file_info(self, setup_test_environment):
        """Test getting file metadata without downloading"""
        # Upload a test file first
        text_content = b"Test file for info"
        files = {"file": ("info_test.txt", BytesIO(text_content), "text/plain")}
        upload_response = client.post("/api/files/upload", files=files)
        assert upload_response.status_code == 200
        
        file_id = upload_response.json()["id"]
        
        # Get file info
        response = client.get(f"/api/files/{file_id}/info")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == file_id
        assert data["original_filename"] == "info_test.txt"
        assert data["mime_type"] == "text/plain"
        assert data["file_size"] == len(text_content)
    
    def test_delete_file(self, setup_test_environment):
        """Test deleting an uploaded file"""
        # Upload a test file first
        text_content = b"Test file to delete"
        files = {"file": ("delete_test.txt", BytesIO(text_content), "text/plain")}
        upload_response = client.post("/api/files/upload", files=files)
        assert upload_response.status_code == 200
        
        file_id = upload_response.json()["id"]
        
        # Delete the file
        response = client.delete(f"/api/files/{file_id}")
        
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]
        
        # Verify file is deleted by trying to download it
        download_response = client.get(f"/api/files/{file_id}")
        assert download_response.status_code == 404
        
        # Verify file is not in the list
        list_response = client.get("/api/files/")
        assert list_response.status_code == 200
        files_list = list_response.json()
        assert len(files_list) == 0
    
    def test_delete_nonexistent_file(self, setup_test_environment):
        """Test deleting a file that doesn't exist"""
        fake_id = "nonexistent-file-id"
        response = client.delete(f"/api/files/{fake_id}")
        
        assert response.status_code == 404
        assert "File not found" in response.json()["detail"]

class TestSecurityValidation:
    """Test security features"""
    
    def test_path_traversal_prevention(self, setup_test_environment):
        """Test that path traversal attacks are prevented"""
        text_content = b"Malicious content"
        malicious_filenames = [
            "../../../etc/passwd.txt",
            "..\\..\\..\\windows\\system32\\config\\sam.txt",
            "....//....//....//etc//passwd.txt",
            "/etc/passwd.txt",
            "C:\\Windows\\System32\\config\\sam.txt"
        ]
        
        for filename in malicious_filenames:
            files = {"file": (filename, BytesIO(text_content), "text/plain")}
            response = client.post("/api/files/upload", files=files)
            
            assert response.status_code == 200
            data = response.json()
            # Ensure the sanitized filename doesn't contain path traversal sequences
            assert ".." not in data["original_filename"]
            assert "/" not in data["original_filename"]
            assert "\\" not in data["original_filename"]
            assert not data["original_filename"].startswith("/")
            assert not data["original_filename"].startswith("C:")
    
    def test_special_characters_in_filename(self, setup_test_environment):
        """Test handling of special characters in filenames"""
        text_content = b"Test content"
        special_filename = 'test<>:"/\\|?*file.txt'
        
        files = {"file": (special_filename, BytesIO(text_content), "text/plain")}
        response = client.post("/api/files/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        # Special characters should be replaced with underscores
        sanitized_name = data["original_filename"]
        dangerous_chars = '<>:"/\\|?*'
        for char in dangerous_chars:
            assert char not in sanitized_name

class TestAPIEndpoints:
    """Test API endpoint functionality"""
    
    def test_root_endpoint(self, setup_test_environment):
        """Test the root endpoint"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "File Upload & Management System" in data["message"]
    
    def test_upload_without_file(self, setup_test_environment):
        """Test upload endpoint without providing a file"""
        response = client.post("/api/files/upload")
        
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_multiple_file_upload_and_management(self, setup_test_environment):
        """Test uploading multiple files and managing them"""
        # Upload multiple files
        files_to_upload = [
            ("file1.txt", b"Content of file 1", "text/plain"),
            ("file2.txt", b"Content of file 2", "text/plain"),
            ("image.png", b'\x89PNG\r\n\x1a\n', "image/png")
        ]
        
        uploaded_ids = []
        
        for filename, content, mime_type in files_to_upload:
            files = {"file": (filename, BytesIO(content), mime_type)}
            response = client.post("/api/files/upload", files=files)
            assert response.status_code == 200
            uploaded_ids.append(response.json()["id"])
        
        # List all files
        response = client.get("/api/files/")
        assert response.status_code == 200
        files_list = response.json()
        assert len(files_list) == 3
        
        # Download each file
        for file_id in uploaded_ids:
            response = client.get(f"/api/files/{file_id}")
            assert response.status_code == 200
        
        # Delete one file
        response = client.delete(f"/api/files/{uploaded_ids[0]}")
        assert response.status_code == 200
        
        # Verify file count decreased
        response = client.get("/api/files/")
        assert response.status_code == 200
        files_list = response.json()
        assert len(files_list) == 2

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
