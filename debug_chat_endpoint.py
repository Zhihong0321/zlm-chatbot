import requests
import json

BASE_URL = "https://zlm-chatbot-production.up.railway.app/api/v1"

def test_direct_chat_endpoint():
    print("Testing POST /api/v1/chat/chat...")
    
    url = f"{BASE_URL}/chat/chat"
    payload = {
        "message": "Hello",
        "session_id": 1,  # Required by schema if not optional
        "agent_id": 1     # Optional
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 404:
            print("CONFIRMED: Endpoint returned 404")
        elif response.status_code == 405:
            print("Method Not Allowed (Maybe it expects GET?)")
        elif response.status_code == 422:
            print("Validation Error (Endpoint exists but payload wrong)")
        elif response.status_code == 200:
            print("Success!")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_direct_chat_endpoint()
