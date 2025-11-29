import requests
import os

BASE_URL = "https://zlm-chatbot-production.up.railway.app/api/v1"

def debug_agents_list():
    print("DEBUG: Testing agents list endpoint...")
    try:
        res = requests.get(f"{BASE_URL}/agents")
        print(f"Status Code: {res.status_code}")
        print(f"Response Headers: {res.headers}")
        print(f"Response Body: {res.text[:500]}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    debug_agents_list()
