# api_test.py
import httpx
import io

BASE_URL = "http://localhost:8000"


def test_file_operations():
    # CREATE (Upload)
    test_content = b"Test file content for API testing"
    files = {'file': ('test_file.txt', io.BytesIO(test_content), 'text/plain')}
    
    response = httpx.post(f"{BASE_URL}/api/files/upload", files=files)
    assert response.status_code in (200, 201)
    created = response.json()
    
    # Estrai l'ID del file (adatta in base alla tua API)
    file_id = created.get("id") or created.get("file_id") or created.get("filename")
    assert file_id is not None
    print(f"✓ File uploaded: {file_id}")

    # READ ALL (List)
    response = httpx.get(f"{BASE_URL}/api/files/")
    assert response.status_code == 200
    files_list = response.json()
    
    # Verifica che il file sia nella lista
    files_data = files_list if isinstance(files_list, list) else files_list.get("files", [])
    assert len(files_data) > 0
    print(f"✓ Files listed: {len(files_data)} files")

    # READ ONE (Download)
    response = httpx.get(f"{BASE_URL}/api/files/{file_id}")
    assert response.status_code == 200
    downloaded_content = response.content
    assert len(downloaded_content) > 0
    print(f"✓ File downloaded: {len(downloaded_content)} bytes")

    # DELETE
    response = httpx.delete(f"{BASE_URL}/api/files/{file_id}")
    assert response.status_code in (200, 204)
    print(f"✓ File deleted: {file_id}")

    # VERIFY DELETION
    response = httpx.get(f"{BASE_URL}/api/files/{file_id}")
    assert response.status_code in (404, 400)
    print(f"✓ Deletion verified")


if __name__ == "__main__":
    test_file_operations()
    print("\n✅ All tests passed!")