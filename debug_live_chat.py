import requests
import json
import sys

BASE_URL = "https://zlm-chatbot-production.up.railway.app/api/v1"

def debug_chat():
    print("--- 1. Listing Agents ---")
    try:
        res = requests.get(f"{BASE_URL}/agents/")
        if res.status_code != 200:
            print(f"FAILED to list agents: {res.status_code} {res.text}")
            return
        
        agents = res.json()
        print(f"Found {len(agents)} agents:")
        for a in agents:
            print(f"  [{a['id']}] {a['name']} (Model: {a['model']})")
            
        if not agents:
            print("No agents found. Create one first.")
            return

        agent_id = agents[0]['id']
        print(f"\n--- 2. Using Agent ID: {agent_id} ---")
        
        print("\n--- 3. Creating Session ---")
        session_payload = {
            "title": "Debug Chat Session",
            "agent_id": agent_id
        }
        res = requests.post(f"{BASE_URL}/sessions/", json=session_payload)
        if res.status_code != 200:
            print(f"FAILED to create session: {res.status_code} {res.text}")
            return
            
        session = res.json()
        session_id = session['id']
        print(f"Session Created: {session_id}")
        
        print("\n--- 4. Sending Message 'Hello' ---")
        msg_payload = {"message": "Hello"}
        # Note: Using the standard chat endpoint used by UI
        chat_url = f"{BASE_URL}/chat/{session_id}/messages"
        print(f"POST {chat_url}")
        
        res = requests.post(chat_url, json=msg_payload, timeout=60)
        
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            print("Response Content:")
            # Safely print content encoding weird chars if necessary
            content = data.get('content', 'No content')
            try:
                # Python win32 console encoding fix
                sys.stdout.reconfigure(encoding='utf-8')
                print(content)
            except:
                print(str(content).encode('ascii', 'ignore').decode('ascii'))
                
            if data.get('reasoning_content'):
                print("Reasoning:", data.get('reasoning_content'))
        else:
            print("Error Response:", res.text)
            
    except Exception as e:
        print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    debug_chat()
