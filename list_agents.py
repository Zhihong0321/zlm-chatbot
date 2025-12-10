import httpx
import json

try:
    resp = httpx.get('https://zlm-chatbot-production.up.railway.app/api/v1/agents/')
    data = resp.json()
    print(json.dumps(data, indent=2))
except Exception as e:
    print(f"Error: {e}")
