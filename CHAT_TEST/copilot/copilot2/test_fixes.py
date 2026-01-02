"""Quick test script to verify the API fixes."""
import httpx
import time

BASE_URL = "http://localhost:8000"

def test_invalid_operations():
    """Test error handling for invalid operations."""
    print("Testing invalid operations...")
    
    # Test 1: GET messages of non-existent room with string ID
    response = httpx.get(f"{BASE_URL}/api/chat/rooms/nonexistent_room_999/messages")
    assert response.status_code in (404, 400), f"Expected 404/400, got {response.status_code}"
    print(f"✓ Invalid room ID (string) handled correctly: {response.status_code}")
    
    # Test 2: DELETE non-existent room with string ID
    response = httpx.delete(f"{BASE_URL}/api/chat/rooms/nonexistent_room_999")
    assert response.status_code in (404, 400), f"Expected 404/400, got {response.status_code}"
    print(f"✓ Invalid DELETE (string ID) handled correctly: {response.status_code}")
    
    # Test 3: GET messages of non-existent room with integer ID
    response = httpx.get(f"{BASE_URL}/api/chat/rooms/999999/messages")
    assert response.status_code in (404, 400), f"Expected 404/400, got {response.status_code}"
    print(f"✓ Invalid room ID (integer) handled correctly: {response.status_code}")
    
    # Test 4: DELETE non-existent room with integer ID
    response = httpx.delete(f"{BASE_URL}/api/chat/rooms/999999")
    assert response.status_code in (404, 400), f"Expected 404/400, got {response.status_code}"
    print(f"✓ Invalid DELETE (integer ID) handled correctly: {response.status_code}")
    
    print("\nAll invalid operation tests passed! ✓")


def test_valid_operations():
    """Test normal operations still work."""
    print("\nTesting valid operations...")
    
    # Create a room
    response = httpx.post(
        f"{BASE_URL}/api/chat/rooms",
        json={"name": f"Test Room {int(time.time())}"}
    )
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    room = response.json()
    room_id = room["id"]
    print(f"✓ Created room: {room['name']} (ID: {room_id})")
    
    # Get messages (should be empty)
    response = httpx.get(f"{BASE_URL}/api/chat/rooms/{room_id}/messages")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    messages = response.json()
    assert len(messages) == 0, f"Expected empty list, got {len(messages)} messages"
    print(f"✓ Retrieved messages (empty list): {len(messages)}")
    
    # List rooms
    response = httpx.get(f"{BASE_URL}/api/chat/rooms")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    rooms = response.json()
    assert len(rooms) > 0, "Expected at least one room"
    print(f"✓ Listed rooms: {len(rooms)} room(s)")
    
    # Delete room
    response = httpx.delete(f"{BASE_URL}/api/chat/rooms/{room_id}")
    assert response.status_code == 204, f"Expected 204, got {response.status_code}"
    print(f"✓ Deleted room: {room_id}")
    
    print("\nAll valid operation tests passed! ✓")


if __name__ == "__main__":
    try:
        print("=" * 60)
        print("Testing API Fixes")
        print("=" * 60)
        
        test_invalid_operations()
        test_valid_operations()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! ✓✓✓")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        exit(1)
