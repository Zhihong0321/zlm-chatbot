import httpx
import json

try:
    resp = httpx.get('https://zlm-chatbot-production.up.railway.app/api/v1/agents/')
    data = resp.json()
    
    found = False
    for agent in data:
        if 'billing' in agent['name'].lower() or 'calculator' in agent['name'].lower():
            print(f"FOUND AGENT: {agent['name']} (ID: {agent['id']})")
            print(f"Current System Prompt: {agent['system_prompt']}")
            print("-" * 20)
            found = True
            
    if not found:
        print("No billing agent found. Listing all names:")
        for agent in data:
            print(f"- {agent['name']} (ID: {agent['id']})")

except Exception as e:
    print(f"Error: {e}")
