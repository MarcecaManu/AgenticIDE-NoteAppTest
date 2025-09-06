# api_test.py
import httpx
import uuid

BASE_URL = "http://localhost:8000"


def test_crud_sequence():
    unique_id = str(uuid.uuid4())
    note = {
        "title": f"Test Title {unique_id}",
        "content": "Test Content"
    }

    # CREATE
    response = httpx.post(f"{BASE_URL}/api/notes/", json=note)
    assert response.status_code in (200, 201)
    created = response.json()
    assert "id" in created
    note_id = created["id"]

    # READ ALL
    response = httpx.get(f"{BASE_URL}/api/notes/")
    assert response.status_code == 200
    notes = response.json()

    # Ensure only one note has the unique title
    matching_notes = [n for n in notes if n["title"] == note["title"]]
    assert len(matching_notes) == 1
    assert matching_notes[0]["id"] == note_id

    # UPDATE
    updated = {**note, "title": f"Updated Title {unique_id}"}
    response = httpx.put(f"{BASE_URL}/api/notes/{note_id}", json=updated)
    assert response.status_code == 200
    assert response.json()["title"] == updated["title"]

    # DELETE
    response = httpx.delete(f"{BASE_URL}/api/notes/{note_id}")
    assert response.status_code == 200

    # VERIFY DELETION
    response = httpx.get(f"{BASE_URL}/api/notes/{note_id}")
    assert response.status_code in (404, 400)
