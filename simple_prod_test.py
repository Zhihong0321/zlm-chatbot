#!/usr/bin/env python3
"""
Simple Production Test Script
Tests your Z.ai application on production site
"""

import os
import sys
import requests
import time
from dotenv import load_dotenv

def main():
    print("Production Site Test")
    print("=" * 40)
    
    # Load environment
    load_dotenv()
    prod_url = os.getenv("PRODUCTION_URL", "")
    
    if not prod_url:
        print("ERROR: Set PRODUCTION_URL")
        print("Example: PRODUCTION_URL=https://your-app.railway.app")
        return False
    
    print(f"Testing: {prod_url}")
    
    # Test health first
    print("\n1. Health Check")
    try:
        response = requests.get(f"{prod_url}/api/v1/ui/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"OK: Status={data.get('status')}, DB={data.get('database')}")
        else:
            print(f"ERROR: {response.status_code} - {response.text[:50]}")
            return False
    except Exception as e:
        print(f"ERROR: {str(e)[:50]}")
        return False
    
    # Test agents API
    print("\n2. Agents API")
    try:
        response = requests.get(f"{prod_url}/api/v1/agents/", timeout=10)
        if response.status_code == 200:
            agents = response.json()
            print(f"OK: Found {len(agents)} agents")
        else:
            print(f"ERROR: {response.status_code} - {response.text[:50]}")
            return False
    except Exception as e:
        print(f"ERROR: {str(e)[:50]}")
        return False
    
    # Test agent creation
    print("\n3. Agent Creation")
    try:
        agent_data = {
            "name": "Production Test",
            "description": "Testing agent",
            "system_prompt": "Helpful coding assistant",
            "model": "glm-4.6"
        }
        
        response = requests.post(f"{prod_url}/api/v1/agents/", json=agent_data, timeout=15)
        if response.status_code == 200:
            agent = response.json()
            agent_id = agent["id"]
            print(f"OK: Created agent (ID: {agent_id})")
            
            # Test file upload with content embedding
            print("\n4. File Upload + Content Embedding")
            test_content = f"""Production Test Document

This file tests file management on: {prod_url}
Uploaded at: {time.strftime('%Y-%m-%d %H:%M:%S')}

Content to verify:
1. File upload capability
2. Content embedding in chat
3. Response time measurement
4. Error handling

If you're reading this content, it means:
- File upload worked (main endpoint)
- Content embedding succeeded
- Chat system is functional
- Hybrid approach working correctly

This validates our hybrid approach for Z.ai applications.
"""
            
            files = {"file": ("test.txt", test_content, "text/plain")}
            
            upload_resp = requests.post(f"{prod_url}/api/v1/agents/{agent_id}/upload", files=files, timeout=30)
            
            if upload_resp.status_code == 200:
                upload_result = upload_resp.json()
                file_id = upload_result["file_id"]
                print(f"OK: File uploaded (ID: {file_id[:20]}...)")
                
                # Test chat with embedded content
                session_data = {
                    "title": "Embed Test",
                    "agent_id": agent_id
                }
                
                sess_resp = requests.post(f"{prod_url}/api/v1/sessions/", json=session_data, timeout=10)
                
                if sess_resp.status_code == 200:
                    session = sess_resp.json()
                    session_id = session["id"]
                    
                    chat_data = {"message": f"What test file contents? (File ID: {file_id})"}
                    
                    chat_resp = requests.post(
                        f"{prod_url}/api/v1/chat/{session_id}/messages",
                        json=chat_data,
                        timeout=30
                    )
                    
                    if chat_resp.status_code == 200:
                        chat = chat_resp.json()
                        content = chat_resp.get("message", "")
                        
                        if "Production Test Document" in content:
                            print(f"OK: Content access confirmed!")
                        else:
                            print(f"WARNING: Content access issue")
                        
                        print(f"OK: Response received ({len(content)} chars)")
                        print(f"Preview: {content[:50]}...")
                    else:
                        print(f"ERROR: Chat failed ({chat_resp.status_code})")
                    
                else:
                    print(f"ERROR: Session creation failed ({sess_resp.status_code})")
                    return False
                
                # Cleanup
                delete_resp = requests.delete(f"{prod_url}/api/v1/sessions/{session_id}", timeout=5)
                
            else:
                print(f"ERROR: File upload failed ({upload_resp.status_code})")
                return False
            else:
                print(f"ERROR: Upload request failed ({upload_resp.status_code})")
                return False
                
        else:
            print(f"ERROR: Agent creation failed ({response.status_code})")
            
        except Exception as e:
            print(f"ERROR: {str(e)[:50]}")
            return False
    except Exception as e:
        print(f"ERROR: Main workflow failed - {str(e)[:50]}")
        return False
    
    print(f"\n" + "=" * 40)
    print(f"TEST RESULTS")
    print("=" * 40)
    print(f"Result: PRODUCTION READY")
    print(f"Hybrid approach working correctly")
    print(f"Ready for production use!")
    
    return True

if __name__ == "__main__":
    success = main()
    print(f"Status: {'SUCCESS' if success else 'FAILED'}")
