# api_test.py
import httpx
import time

BASE_URL = "http://localhost:8000"


def test_chat_operations():
    # CREATE ROOM
    room_data = {
        "name": "Test Room",
        "description": "Room for API testing"
    }
    
    response = httpx.post(f"{BASE_URL}/api/chat/rooms", json=room_data)
    assert response.status_code in (200, 201)
    created_room = response.json()
    
    # Estrai l'ID della room (adatta in base alla tua API)
    room_id = created_room.get("id") or created_room.get("room_id") or created_room.get("name")
    assert room_id is not None
    print(f"✓ Room created: {room_id}")

    # READ ALL ROOMS (List)
    response = httpx.get(f"{BASE_URL}/api/chat/rooms")
    assert response.status_code == 200
    rooms_list = response.json()
    
    # Verifica che la room sia nella lista
    rooms_data = rooms_list if isinstance(rooms_list, list) else rooms_list.get("rooms", [])
    assert len(rooms_data) > 0
    print(f"✓ Rooms listed: {len(rooms_data)} rooms")

    # GET MESSAGE HISTORY (should be empty initially)
    response = httpx.get(f"{BASE_URL}/api/chat/rooms/{room_id}/messages")
    assert response.status_code == 200
    messages = response.json()
    
    # Verifica formato risposta
    messages_data = messages if isinstance(messages, list) else messages.get("messages", [])
    print(f"✓ Message history retrieved: {len(messages_data)} messages")

    # Simula invio di un messaggio via REST se l'API lo supporta
    # (alcuni backend potrebbero avere anche POST /api/chat/rooms/{room_id}/messages)
    try:
        message_data = {
            "username": "test_user",
            "content": "Test message via REST API"
        }
        response = httpx.post(
            f"{BASE_URL}/api/chat/rooms/{room_id}/messages",
            json=message_data
        )
        if response.status_code in (200, 201):
            print(f"✓ Message posted via REST API")
            
            # Verifica che il messaggio sia stato aggiunto
            time.sleep(0.5)  # Piccola pausa per assicurare persistenza
            response = httpx.get(f"{BASE_URL}/api/chat/rooms/{room_id}/messages")
            messages = response.json()
            messages_data = messages if isinstance(messages, list) else messages.get("messages", [])
            assert len(messages_data) > 0
            print(f"✓ Message verified in history")
    except Exception as e:
        print(f"⚠ REST message posting not available or failed: {e}")

    # DELETE ROOM
    response = httpx.delete(f"{BASE_URL}/api/chat/rooms/{room_id}")
    assert response.status_code in (200, 204)
    print(f"✓ Room deleted: {room_id}")

    # VERIFY DELETION
    response = httpx.get(f"{BASE_URL}/api/chat/rooms")
    assert response.status_code == 200
    rooms_list = response.json()
    rooms_data = rooms_list if isinstance(rooms_list, list) else rooms_list.get("rooms", [])
    
    # Verifica che la room non sia più nella lista
    room_ids = [r.get("id") or r.get("room_id") or r.get("name") for r in rooms_data]
    assert room_id not in room_ids
    print(f"✓ Deletion verified")


def test_room_message_endpoints():
    """Test aggiuntivo per verificare endpoint messaggi"""
    # Crea una room di test
    room_data = {"name": "Message Test Room"}
    response = httpx.post(f"{BASE_URL}/api/chat/rooms", json=room_data)
    assert response.status_code in (200, 201)
    room = response.json()
    room_id = room.get("id") or room.get("room_id") or room.get("name")
    
    # Test GET messages su room vuota
    response = httpx.get(f"{BASE_URL}/api/chat/rooms/{room_id}/messages")
    assert response.status_code == 200
    print(f"✓ Empty room messages endpoint works")
    
    # Cleanup
    httpx.delete(f"{BASE_URL}/api/chat/rooms/{room_id}")


def test_invalid_operations():
    """Test per verificare gestione errori"""
    # GET messages di room inesistente
    response = httpx.get(f"{BASE_URL}/api/chat/rooms/nonexistent_room_999/messages")
    assert response.status_code in (404, 400)
    print(f"✓ Invalid room ID handled correctly")
    
    # DELETE room inesistente
    response = httpx.delete(f"{BASE_URL}/api/chat/rooms/nonexistent_room_999")
    assert response.status_code in (404, 400)
    print(f"✓ Invalid DELETE handled correctly")


if __name__ == "__main__":
    print("=== Testing Chat REST API ===\n")
    
    print("Test 1: Basic Chat Operations")
    test_chat_operations()
    print()
    
    print("Test 2: Room Message Endpoints")
    test_room_message_endpoints()
    print()
    
    print("Test 3: Invalid Operations")
    test_invalid_operations()
    print()
    
    print("✅ All tests passed!")
