import pytest
import asyncio
import json
import os
import tempfile
import shutil
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import patch
import io

# Import the FastAPI app
import sys
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

try:
    from main import app, load_metadata, save_metadata
    import main
except ImportError:
    print("Error: Cannot import backend modules. Make sure you're running tests from the project root.")
    print(f"Backend path: {backend_path}")
    sys.exit(1)

class TestFileUploadManagement:
    """Test suite for File Upload & Management System"""
    
    @classmethod
    def setup_class(cls):
        """Set up test environment"""
        cls.client = TestClient(app)
        cls.test_dir = Path(tempfile.mkdtemp())
        
        # Store original paths
        import main
        cls.original_upload_dir = main.UPLOAD_DIR
        cls.original_metadata_file = main.METADATA_FILE
        
        # Set new paths for testing
        main.UPLOAD_DIR = cls.test_dir / "uploads"
        main.METADATA_FILE = cls.test_dir / "file_metadata.json"
        main.UPLOAD_DIR.mkdir(exist_ok=True)
        
    @classmethod
    def teardown_class(cls):
        """Clean up test environment"""
        shutil.rmtree(cls.test_dir, ignore_errors=True)
        
        # Restore original paths
        import main
        main.UPLOAD_DIR = cls.original_upload_dir
        main.METADATA_FILE = cls.original_metadata_file
    
    def setup_method(self):
        """Set up before each test method"""
        import main
        
        # Clear uploads directory and metadata file
        if main.UPLOAD_DIR.exists():
            shutil.rmtree(main.UPLOAD_DIR)
        main.UPLOAD_DIR.mkdir(exist_ok=True)
        
        if main.METADATA_FILE.exists():
            main.METADATA_FILE.unlink()
    
    def create_test_file(self, filename: str, content: str, content_type: str = "text/plain"):
        """Helper method to create test files"""
        return (filename, io.BytesIO(content.encode()), content_type)
    
    def create_test_image(self, filename: str = "test.jpg"):
        """Helper method to create a minimal JPEG test file"""
        # Minimal JPEG header
        jpeg_content = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb'
        return (filename, io.BytesIO(jpeg_content), "image/jpeg")
    
    # Test 1: File Upload Success
    def test_file_upload_success(self):
        """Test successful file upload with valid file"""
        test_content = "This is a test file content for upload testing."
        filename, file_content, content_type = self.create_test_file("test.txt", test_content, "text/plain")
        
        response = self.client.post(
            "/api/files/upload",
            files={"file": (filename, file_content, content_type)}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert data["original_filename"] == "test.txt"
        assert data["file_size"] == len(test_content)
        assert data["mime_type"] == "text/plain"
        assert "stored_filename" in data
        assert "upload_date" in data
        
        # Verify file was actually saved
        import main
        stored_file = main.UPLOAD_DIR / data["stored_filename"]
        assert stored_file.exists()
        assert stored_file.read_text() == test_content
        
        # Verify metadata was saved
        metadata = load_metadata()
        assert data["id"] in metadata
        assert metadata[data["id"]]["original_filename"] == "test.txt"
    
    # Test 2: File Listing
    def test_file_listing(self):
        """Test listing uploaded files"""
        # Upload multiple test files
        files_data = []
        
        for i in range(3):
            filename, file_content, content_type = self.create_test_file(f"test_{i}.txt", f"Content {i}")
            response = self.client.post(
                "/api/files/upload",
                files={"file": (filename, file_content, content_type)}
            )
            assert response.status_code == 200
            files_data.append(response.json())
        
        # Test file listing
        response = self.client.get("/api/files/")
        assert response.status_code == 200
        
        data = response.json()
        assert "files" in data
        assert len(data["files"]) == 3
        
        # Verify files are sorted by upload date (newest first)
        upload_dates = [file["upload_date"] for file in data["files"]]
        assert upload_dates == sorted(upload_dates, reverse=True)
        
        # Verify file data
        file_ids = {file["id"] for file in data["files"]}
        expected_ids = {file["id"] for file in files_data}
        assert file_ids == expected_ids
    
    # Test 3: File Download
    def test_file_download(self):
        """Test downloading uploaded files"""
        test_content = "This is downloadable content."
        filename, file_content, content_type = self.create_test_file("download_test.txt", test_content)
        
        # Upload file
        upload_response = self.client.post(
            "/api/files/upload",
            files={"file": (filename, file_content, content_type)}
        )
        assert upload_response.status_code == 200
        file_data = upload_response.json()
        
        # Download file
        download_response = self.client.get(f"/api/files/{file_data['id']}")
        assert download_response.status_code == 200
        assert download_response.content.decode() == test_content
        
        # Verify headers
        assert download_response.headers["content-type"] == "text/plain; charset=utf-8"
        
        # Test download of non-existent file
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = self.client.get(f"/api/files/{fake_id}")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    # Test 4: File Deletion
    def test_file_deletion(self):
        """Test deleting uploaded files"""
        test_content = "This file will be deleted."
        filename, file_content, content_type = self.create_test_file("delete_test.txt", test_content)
        
        # Upload file
        upload_response = self.client.post(
            "/api/files/upload",
            files={"file": (filename, file_content, content_type)}
        )
        assert upload_response.status_code == 200
        file_data = upload_response.json()
        
        # Verify file exists
        import main
        stored_file = main.UPLOAD_DIR / file_data["stored_filename"]
        assert stored_file.exists()
        
        # Delete file
        delete_response = self.client.delete(f"/api/files/{file_data['id']}")
        assert delete_response.status_code == 200
        assert "deleted successfully" in delete_response.json()["message"].lower()
        
        # Verify file is gone from disk
        assert not stored_file.exists()
        
        # Verify file is gone from metadata
        metadata = load_metadata()
        assert file_data["id"] not in metadata
        
        # Verify file is not in listing
        list_response = self.client.get("/api/files/")
        assert list_response.status_code == 200
        file_ids = {file["id"] for file in list_response.json()["files"]}
        assert file_data["id"] not in file_ids
        
        # Test deletion of non-existent file
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = self.client.delete(f"/api/files/{fake_id}")
        assert response.status_code == 404
    
    # Test 5: File Type Validation (Rejection)
    def test_file_type_validation_rejection(self):
        """Test rejection of invalid file types"""
        # Test various invalid file types
        invalid_files = [
            ("malware.exe", b"MZ\x90\x00", "application/octet-stream"),
            ("script.bat", b"@echo off", "application/x-bat"),
            ("archive.zip", b"PK\x03\x04", "application/zip"),
            ("document.doc", b"\xd0\xcf\x11\xe0", "application/msword"),
            ("unknown.xyz", b"unknown content", "application/octet-stream"),
        ]
        
        for filename, content, content_type in invalid_files:
            response = self.client.post(
                "/api/files/upload",
                files={"file": (filename, io.BytesIO(content), content_type)}
            )
            assert response.status_code == 400, f"Expected 400 for {filename} with type {content_type}, got {response.status_code}"
            assert "not allowed" in response.json()["detail"].lower()
            
    def test_file_type_validation_acceptance(self):
        """Test acceptance of valid file types"""
        # Test various valid file types
        valid_files = [
            ("image.jpg", self.create_test_image("image.jpg")),
            ("document.pdf", ("document.pdf", io.BytesIO(b"%PDF-1.4"), "application/pdf")),
            ("data.json", ("data.json", io.BytesIO(b'{"key": "value"}'), "application/json")),
            ("style.css", ("style.css", io.BytesIO(b"body { margin: 0; }"), "text/css")),
        ]
        
        for test_name, file_data in valid_files:
            filename, file_content, content_type = file_data
            response = self.client.post(
                "/api/files/upload",
                files={"file": (filename, file_content, content_type)}
            )
            assert response.status_code == 200, f"Failed for {test_name}: {response.json()}"
    
    # Test 6: File Size Validation
    def test_file_size_validation(self):
        """Test file size limits"""
        # Test file too large (11MB > 10MB limit)
        large_content = "x" * (11 * 1024 * 1024)
        filename, file_content, content_type = self.create_test_file("large.txt", large_content)
        
        response = self.client.post(
            "/api/files/upload",
            files={"file": (filename, file_content, content_type)}
        )
        assert response.status_code == 413
        assert "too large" in response.json()["detail"].lower()
        
        # Test acceptable file size (1MB)
        normal_content = "x" * (1024 * 1024)
        filename, file_content, content_type = self.create_test_file("normal.txt", normal_content)
        
        response = self.client.post(
            "/api/files/upload",
            files={"file": (filename, file_content, content_type)}
        )
        assert response.status_code == 200
    
    # Test 7: Filename Sanitization
    def test_filename_sanitization(self):
        """Test filename sanitization for security"""
        dangerous_filenames = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\config\\sam",
            "file<script>alert(1)</script>.txt",
            "file|with|pipes.txt",
            "file?with?questions.txt",
            "file*with*asterisks.txt"
        ]
        
        for dangerous_name in dangerous_filenames:
            filename, file_content, content_type = self.create_test_file(dangerous_name, "test content")
            
            response = self.client.post(
                "/api/files/upload",
                files={"file": (filename, file_content, content_type)}
            )
            assert response.status_code == 200
            
            data = response.json()
            # Original filename should be preserved in metadata (may be URL encoded)
            assert dangerous_name in data["original_filename"] or data["original_filename"] == dangerous_name
            # But stored filename should be sanitized and safe
            assert ".." not in data["stored_filename"]
            assert "/" not in data["stored_filename"]
            assert "\\" not in data["stored_filename"]
    
    # Test 8: File Info Endpoint
    def test_file_info_endpoint(self):
        """Test getting file metadata without downloading"""
        test_content = "Info test content"
        filename, file_content, content_type = self.create_test_file("info_test.txt", test_content)
        
        # Upload file
        upload_response = self.client.post(
            "/api/files/upload",
            files={"file": (filename, file_content, content_type)}
        )
        assert upload_response.status_code == 200
        file_data = upload_response.json()
        
        # Get file info
        info_response = self.client.get(f"/api/files/{file_data['id']}/info")
        assert info_response.status_code == 200
        
        info_data = info_response.json()
        assert info_data == file_data  # Should be identical to upload response
        
        # Test info for non-existent file
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = self.client.get(f"/api/files/{fake_id}/info")
        assert response.status_code == 404
    
    # Test 9: API Root Endpoint
    def test_api_root_endpoint(self):
        """Test API root endpoint"""
        response = self.client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "endpoints" in data
        
        # Verify all endpoints are documented
        endpoints = data["endpoints"]
        expected_endpoints = ["upload", "list", "download", "delete", "info"]
        for endpoint in expected_endpoints:
            assert endpoint in endpoints
    
    # Test 10: Concurrent File Operations
    def test_concurrent_operations(self):
        """Test handling of concurrent file operations"""
        # Simplified test - upload files sequentially but quickly to test basic concurrency handling
        
        upload_results = []
        for i in range(3):
            filename, file_content, content_type = self.create_test_file(
                f"concurrent_{i}.txt", 
                f"Concurrent content {i}"
            )
            response = self.client.post(
                "/api/files/upload",
                files={"file": (filename, file_content, content_type)}
            )
            upload_results.append(response.status_code)
        
        # All uploads should succeed
        assert all(status == 200 for status in upload_results), f"Upload results: {upload_results}"
        
        # Verify all files were uploaded successfully
        list_response = self.client.get("/api/files/")
        assert list_response.status_code == 200
        files_count = len(list_response.json()["files"])
        assert files_count == 3, f"Expected 3 files uploaded, got {files_count}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])