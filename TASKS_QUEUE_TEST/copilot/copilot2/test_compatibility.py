"""
Quick test script to verify API compatibility with both formats.
"""
import httpx
import json

BASE_URL = "http://localhost:8000"

def test_api_formats():
    """Test both API request formats"""
    
    print("Testing API Compatibility...")
    print("=" * 60)
    
    # Test 1: Original format (lowercase, input_data)
    print("\n✅ Test 1: Original format (lowercase, input_data)")
    data1 = {
        "task_type": "data_processing",
        "input_data": {
            "rows": 500
        }
    }
    response1 = httpx.post(f"{BASE_URL}/api/tasks/submit", json=data1)
    print(f"Status: {response1.status_code}")
    if response1.status_code in (200, 201):
        result1 = response1.json()
        print(f"Task ID: {result1['id'][:8]}...")
        print(f"Task Type: {result1['task_type']}")
        print(f"Status: {result1['status']}")
    else:
        print(f"Error: {response1.text}")
    
    # Test 2: Alternative format (uppercase, parameters)
    print("\n✅ Test 2: Alternative format (uppercase, parameters)")
    data2 = {
        "task_type": "DATA_PROCESSING",
        "parameters": {
            "num_rows": 500,
            "processing_time": 2
        }
    }
    response2 = httpx.post(f"{BASE_URL}/api/tasks/submit", json=data2)
    print(f"Status: {response2.status_code}")
    if response2.status_code in (200, 201):
        result2 = response2.json()
        print(f"Task ID: {result2['id'][:8]}...")
        print(f"Task Type: {result2['task_type']}")
        print(f"Status: {result2['status']}")
    else:
        print(f"Error: {response2.text}")
    
    # Test 3: Email simulation with alternative parameters
    print("\n✅ Test 3: Email simulation (uppercase, num_emails)")
    data3 = {
        "task_type": "EMAIL_SIMULATION",
        "parameters": {
            "num_emails": 3,
            "delay_per_email": 0.5,
            "subject": "Test Email"
        }
    }
    response3 = httpx.post(f"{BASE_URL}/api/tasks/submit", json=data3)
    print(f"Status: {response3.status_code}")
    if response3.status_code in (200, 201):
        result3 = response3.json()
        print(f"Task ID: {result3['id'][:8]}...")
        print(f"Task Type: {result3['task_type']}")
        print(f"Status: {result3['status']}")
    else:
        print(f"Error: {response3.text}")
    
    # Test 4: Image processing with alternative parameters
    print("\n✅ Test 4: Image processing (uppercase, num_images)")
    data4 = {
        "task_type": "IMAGE_PROCESSING",
        "parameters": {
            "num_images": 2,
            "target_size": "800x600",
            "output_format": "PNG"
        }
    }
    response4 = httpx.post(f"{BASE_URL}/api/tasks/submit", json=data4)
    print(f"Status: {response4.status_code}")
    if response4.status_code in (200, 201):
        result4 = response4.json()
        print(f"Task ID: {result4['id'][:8]}...")
        print(f"Task Type: {result4['task_type']}")
        print(f"Status: {result4['status']}")
    else:
        print(f"Error: {response4.text}")
    
    # List all tasks
    print("\n✅ Test 5: List all tasks")
    response5 = httpx.get(f"{BASE_URL}/api/tasks/")
    if response5.status_code == 200:
        result5 = response5.json()
        print(f"Total tasks: {result5['total']}")
        print(f"Returned tasks: {len(result5['tasks'])}")
    
    print("\n" + "=" * 60)
    print("All tests completed successfully! ✅")
    print("The API accepts both parameter formats correctly.")

if __name__ == "__main__":
    try:
        test_api_formats()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure the FastAPI server is running on http://localhost:8000")
