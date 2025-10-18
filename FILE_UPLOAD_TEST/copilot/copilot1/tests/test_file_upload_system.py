import pytest
import asyncio
import json
import os
import tempfile
import shutil
from pathlib import Path
from fastapi.testclient import TestClient
from io import BytesIO

# Add the backend directory to the path to import main
import sys
import importlib.util
backend_path = str(Path(__file__).parent.parent / "backend")
sys.path.insert(0, backend_path)

# Dynamic import to handle path issues
spec = importlib.util.spec_from_file_location("main", Path(backend_path) / "main.py")
main_module = importlib.util.module_from_spec(spec)
sys.modules["main"] = main_module
spec.loader.exec_module(main_module)

app = main_module.app
UPLOAD_DIR = main_module.UPLOAD_DIR
METADATA_FILE = main_module.METADATA_FILE

class TestFileUploadSystem:
    """Test suite for the File Upload & Management System."""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Set up and tear down test environment."""
        # Create a temporary directory for test uploads
        self.test_upload_dir = Path(tempfile.mkdtemp())
        self.test_metadata_file = self.test_upload_dir / "test_metadata.json"
        
        # Monkey patch the paths in the main module
        self.original_upload_dir = main_module.UPLOAD_DIR
        self.original_metadata_file = main_module.METADATA_FILE
        
        main_module.UPLOAD_DIR = self.test_upload_dir
        main_module.METADATA_FILE = self.test_metadata_file
        
        # Create test client
        self.client = TestClient(app)
        
        yield
        
        # Cleanup
        main_module.UPLOAD_DIR = self.original_upload_dir
        main_module.METADATA_FILE = self.original_metadata_file
        shutil.rmtree(self.test_upload_dir, ignore_errors=True)
    
    def create_test_file(self, filename: str, content: bytes, content_type: str = "text/plain"):
        """Helper to create test files."""
        return ("file", (filename, BytesIO(content), content_type))
    
    def test_upload_valid_text_file(self):
        """Test uploading a valid text file."""
        test_content = b"This is a test file content."
        files = [self.create_test_file("test.txt", test_content, "text/plain")]
        
        response = self.client.post("/api/files/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert data["original_filename"] == "test.txt"
        assert data["file_size"] == len(test_content)
        assert data["mime_type"] == "text/plain"
        assert "upload_date" in data
        assert "stored_filename" in data
        
        # Verify file was saved
        stored_path = self.test_upload_dir / data["stored_filename"]
        assert stored_path.exists()
        assert stored_path.read_bytes() == test_content
    
    def test_upload_valid_pdf_file(self):
        """Test uploading a valid PDF file."""
        # Minimal PDF content (simplified)
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n>>\nendobj\nxref\n0 1\n0000000000 65535 f \ntrailer\n<<\n>>\nstartxref\n9\n%%EOF"
        files = [self.create_test_file("document.pdf", pdf_content, "application/pdf")]
        
        response = self.client.post("/api/files/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["original_filename"] == "document.pdf"
        assert data["mime_type"] == "application/pdf"
    
    def test_upload_valid_image_file(self):
        """Test uploading a valid image file."""
        # Minimal PNG content (1x1 pixel)
        png_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
        files = [self.create_test_file("image.png", png_content, "image/png")]
        
        response = self.client.post("/api/files/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["original_filename"] == "image.png"
        assert data["mime_type"] == "image/png"
    
    def test_upload_invalid_file_type(self):
        """Test uploading an invalid file type (should be rejected)."""
        exe_content = b"MZ\x90\x00"  # Start of executable file
        files = [self.create_test_file("malware.exe", exe_content, "application/x-executable")]
        
        response = self.client.post("/api/files/upload", files=files)
        
        assert response.status_code == 415  # Unsupported Media Type
        assert "File type not allowed" in response.json()["detail"]
    
    def test_upload_file_too_large(self):
        """Test uploading a file that exceeds size limit."""
        # Create content larger than 10MB
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        files = [self.create_test_file("large.txt", large_content, "text/plain")]
        
        response = self.client.post("/api/files/upload", files=files)
        
        assert response.status_code == 413  # Request Entity Too Large
        assert "File size exceeds maximum" in response.json()["detail"]
    
    def test_filename_sanitization(self):
        """Test that dangerous filenames are sanitized."""
        dangerous_content = b"test content"
        files = [self.create_test_file("../../../etc/passwd.txt", dangerous_content, "text/plain")]
        
        response = self.client.post("/api/files/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        
        # Original filename should be preserved
        assert data["original_filename"] == "../../../etc/passwd.txt"
        
        # Stored filename should be sanitized
        stored_filename = data["stored_filename"]
        assert "../" not in stored_filename
        assert "passwd" in stored_filename
        assert stored_filename.startswith(data["id"])
    
    def test_list_files_empty(self):
        """Test listing files when no files are uploaded."""
        response = self.client.get("/api/files/")
        
        assert response.status_code == 200
        assert response.json() == []
    
    def test_list_files_with_uploads(self):
        """Test listing files after uploading some files."""
        # Upload multiple files
        file1_content = b"Content of file 1"
        file2_content = b"Content of file 2"
        
        files1 = [self.create_test_file("file1.txt", file1_content, "text/plain")]
        files2 = [self.create_test_file("file2.md", file2_content, "text/markdown")]
        
        upload1 = self.client.post("/api/files/upload", files=files1)
        upload2 = self.client.post("/api/files/upload", files=files2)
        
        assert upload1.status_code == 200
        assert upload2.status_code == 200
        
        # List files
        response = self.client.get("/api/files/")
        
        assert response.status_code == 200
        files = response.json()
        assert len(files) == 2
        
        filenames = {f["original_filename"] for f in files}
        assert "file1.txt" in filenames
        assert "file2.md" in filenames
    
    def test_download_file(self):
        """Test downloading an uploaded file."""
        test_content = b"This is downloadable content."
        files = [self.create_test_file("download_test.txt", test_content, "text/plain")]
        
        # Upload file
        upload_response = self.client.post("/api/files/upload", files=files)
        assert upload_response.status_code == 200
        
        file_data = upload_response.json()
        file_id = file_data["id"]
        
        # Download file
        download_response = self.client.get(f"/api/files/{file_id}")
        
        assert download_response.status_code == 200
        assert download_response.content == test_content
        assert download_response.headers["content-type"] == "text/plain; charset=utf-8"
    
    def test_download_nonexistent_file(self):
        """Test downloading a file that doesn't exist."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        response = self.client.get(f"/api/files/{fake_id}")
        
        assert response.status_code == 404
        assert "File not found" in response.json()["detail"]
    
    def test_get_file_info(self):
        """Test getting file metadata without downloading."""
        test_content = b"Content for info test."
        files = [self.create_test_file("info_test.json", test_content, "application/json")]
        
        # Upload file
        upload_response = self.client.post("/api/files/upload", files=files)
        assert upload_response.status_code == 200
        
        file_data = upload_response.json()
        file_id = file_data["id"]
        
        # Get file info
        info_response = self.client.get(f"/api/files/{file_id}/info")
        
        assert info_response.status_code == 200
        info_data = info_response.json()
        
        assert info_data["id"] == file_id
        assert info_data["original_filename"] == "info_test.json"
        assert info_data["file_size"] == len(test_content)
        assert info_data["mime_type"] == "application/json"
        assert "upload_date" in info_data
    
    def test_get_info_nonexistent_file(self):
        """Test getting info for a file that doesn't exist."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        response = self.client.get(f"/api/files/{fake_id}/info")
        
        assert response.status_code == 404
        assert "File not found" in response.json()["detail"]
    
    def test_delete_file(self):
        """Test deleting an uploaded file."""
        test_content = b"Content to be deleted."
        files = [self.create_test_file("delete_test.txt", test_content, "text/plain")]
        
        # Upload file
        upload_response = self.client.post("/api/files/upload", files=files)
        assert upload_response.status_code == 200
        
        file_data = upload_response.json()
        file_id = file_data["id"]
        stored_filename = file_data["stored_filename"]
        
        # Verify file exists
        file_path = self.test_upload_dir / stored_filename
        assert file_path.exists()
        
        # Delete file
        delete_response = self.client.delete(f"/api/files/{file_id}")
        
        assert delete_response.status_code == 200
        assert "deleted successfully" in delete_response.json()["message"]
        
        # Verify file is removed from disk
        assert not file_path.exists()
        
        # Verify file is removed from metadata
        info_response = self.client.get(f"/api/files/{file_id}/info")
        assert info_response.status_code == 404
    
    def test_delete_nonexistent_file(self):
        """Test deleting a file that doesn't exist."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        response = self.client.delete(f"/api/files/{fake_id}")
        
        assert response.status_code == 404
        assert "File not found" in response.json()["detail"]
    
    def test_metadata_persistence(self):
        """Test that metadata is properly saved and loaded."""
        test_content = b"Persistence test content."
        files = [self.create_test_file("persistence.txt", test_content, "text/plain")]
        
        # Upload file
        upload_response = self.client.post("/api/files/upload", files=files)
        assert upload_response.status_code == 200
        
        file_data = upload_response.json()
        file_id = file_data["id"]
        
        # Verify metadata file exists and contains data
        assert self.test_metadata_file.exists()
        
        with open(self.test_metadata_file, 'r') as f:
            metadata = json.load(f)
        
        assert file_id in metadata
        assert metadata[file_id]["original_filename"] == "persistence.txt"
        assert metadata[file_id]["file_size"] == len(test_content)
    
    def test_multiple_file_upload_workflow(self):
        """Test a complete workflow with multiple files."""
        # Upload multiple files
        files_to_upload = [
            ("doc.txt", b"Document content", "text/plain"),
            ("data.csv", b"name,age\nJohn,30", "text/csv"),
            ("script.py", b"print('Hello World')", "text/x-python-script")
        ]
        
        uploaded_files = []
        
        for filename, content, content_type in files_to_upload:
            files = [self.create_test_file(filename, content, content_type)]
            response = self.client.post("/api/files/upload", files=files)
            assert response.status_code == 200
            uploaded_files.append(response.json())
        
        # List all files
        list_response = self.client.get("/api/files/")
        assert list_response.status_code == 200
        all_files = list_response.json()
        assert len(all_files) == 3
        
        # Download each file and verify content
        for i, (filename, content, content_type) in enumerate(files_to_upload):
            file_id = uploaded_files[i]["id"]
            
            download_response = self.client.get(f"/api/files/{file_id}")
            assert download_response.status_code == 200
            assert download_response.content == content
            
            info_response = self.client.get(f"/api/files/{file_id}/info")
            assert info_response.status_code == 200
            assert info_response.json()["original_filename"] == filename
        
        # Delete one file
        file_to_delete = uploaded_files[1]["id"]
        delete_response = self.client.delete(f"/api/files/{file_to_delete}")
        assert delete_response.status_code == 200
        
        # Verify list shows remaining files
        list_response = self.client.get("/api/files/")
        assert list_response.status_code == 200
        remaining_files = list_response.json()
        assert len(remaining_files) == 2
        
        remaining_names = {f["original_filename"] for f in remaining_files}
        assert "doc.txt" in remaining_names
        assert "script.py" in remaining_names
        assert "data.csv" not in remaining_names

if __name__ == "__main__":
    pytest.main([__file__, "-v"])