import httpx
import json

try:
    resp = httpx.get('https://zlm-chatbot-production.up.railway.app/api/v1/agents/')
    data = resp.json()
    
    for agent in data:
        if 'billing' in agent['name'].lower() or 'calculator' in agent['name'].lower():
            print(f"ID:{agent['id']} NAME:{agent['name']}")
            
except Exception as e:
    print(f"Error: {e}")
