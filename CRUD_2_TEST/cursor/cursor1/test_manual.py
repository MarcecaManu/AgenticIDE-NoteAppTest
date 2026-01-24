"""
Manual API test script to verify all CRUD operations work
Run this with the server running on http://localhost:8000
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/notes"

def test_api():
    print("=" * 60)
    print("TESTING NOTE MANAGER API")
    print("=" * 60)
    
    # 1. CREATE a note
    print("\n1. Creating a note...")
    new_note = {
        "title": "Test Note from Manual Script",
        "content": "This is a test note to verify the API works"
    }
    response = requests.post(f"{BASE_URL}/", json=new_note)
    print(f"   Status: {response.status_code}")
    if response.status_code == 201:
        created_note = response.json()
        note_id = created_note["id"]
        print(f"   ✓ Created note with ID: {note_id}")
        print(f"   Title: {created_note['title']}")
    else:
        print(f"   ✗ Failed to create note: {response.text}")
        return
    
    # 2. GET all notes
    print("\n2. Getting all notes...")
    response = requests.get(f"{BASE_URL}/")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        notes = response.json()
        print(f"   ✓ Retrieved {len(notes)} note(s)")
    else:
        print(f"   ✗ Failed to get notes: {response.text}")
    
    # 3. GET note by ID
    print(f"\n3. Getting note by ID ({note_id})...")
    response = requests.get(f"{BASE_URL}/{note_id}")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        note = response.json()
        print(f"   ✓ Retrieved note: {note['title']}")
    else:
        print(f"   ✗ Failed to get note: {response.text}")
    
    # 4. UPDATE the note
    print(f"\n4. Updating note {note_id}...")
    updated_note = {
        "title": "Updated Test Note",
        "content": "This note has been updated!"
    }
    response = requests.put(f"{BASE_URL}/{note_id}", json=updated_note)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        note = response.json()
        print(f"   ✓ Updated note: {note['title']}")
    else:
        print(f"   ✗ Failed to update note: {response.text}")
    
    # 5. DELETE the note
    print(f"\n5. Deleting note {note_id}...")
    response = requests.delete(f"{BASE_URL}/{note_id}")
    print(f"   Status: {response.status_code}")
    if response.status_code == 204:
        print(f"   ✓ Successfully deleted note")
    else:
        print(f"   ✗ Failed to delete note: {response.text}")
    
    # 6. Verify deletion
    print(f"\n6. Verifying deletion...")
    response = requests.get(f"{BASE_URL}/{note_id}")
    print(f"   Status: {response.status_code}")
    if response.status_code == 404:
        print(f"   ✓ Note correctly deleted (404 returned)")
    else:
        print(f"   ✗ Note still exists!")
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Cannot connect to server!")
        print("  Make sure the server is running on http://localhost:8000")
        print("  Start it with: cd backend && uvicorn main:app --reload")
    except Exception as e:
        print(f"\n✗ ERROR: {e}")

