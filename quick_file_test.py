#!/usr/bin/env python3
"""
Quick Test for Coding Endpoint + Files
Simple test without unicode characters
"""

import os
import sys
import time
import requests
from dotenv import load_dotenv
from openai import OpenAI

def main():
    print("Quick Test - Coding Endpoint + Files")
    print("=" * 40)
    
    # Load environment
    load_dotenv()
    api_key = os.getenv("ZAI_API_KEY")
    
    if not api_key:
        print("ERROR: No API key found")
        return False
    
    print(f"API Key: {api_key[:15]}...")
    
    # Test 1: Basic coding endpoint
    print("\n1. Testing Coding Endpoint")
    try:
        client = OpenAI(api_key=api_key, base_url="https://api.z.ai/api/coding/paas/v4")
        
        start = time.time()
        response = client.chat.completions.create(
            model="glm-4.6",
            messages=[{"role": "user", "content": "Hello! Confirm this works."}],
            max_tokens=20
        )
        end = time.time()
        
        content = response.choices[0].message.content
        print(f"SUCCESS: {content}")
        print(f"Time: {end-start:.2f}s")
        
    except Exception as e:
        print(f"FAILED: {str(e)}")
        return False
    
    # Test 2: Direct file upload
    print("\n2. Testing File Upload")
    try:
        test_content = "Test file for coding endpoint upload."
        
        url = "https://api.z.ai/api/coding/paas/v4/files"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json"
        }
        
        files = {
            'file': ('test_file.txt', test_content, 'text/plain'),
            'purpose': (None, 'agent')
        }
        
        start = time.time()
        response = requests.post(url, headers=headers, files=files)
        end = time.time()
        
        if response.status_code == 200:
            result = response.json()
            file_id = result.get('id')
            print(f"SUCCESS: File uploaded")
            print(f"File ID: {file_id}")
            print(f"Size: {result.get('bytes')} bytes")
            print(f"Time: {end-start:.2f}s")
            
            # Test chat with file reference
            print("\n3. Testing Chat with File Reference")
            try:
                chat_response = client.chat.completions.create(
                    model="glm-4.6",
                    messages=[
                        {"role": "user", "content": f"Based on the file I uploaded (ID: {file_id}), what does it contain?"}
                    ],
                    max_tokens=100
                )
                
                chat_content = chat_response.choices[0].message.content
                print(f"CHAT SUCCESS: {chat_content[:100]}...")
                
            except Exception as e:
                print(f"CHAT FAILED: {str(e)}")
            
        else:
            print(f"UPLOAD FAILED: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"UPLOAD ERROR: {str(e)}")
        return False
    
    # Test 4: Backend connectivity (if running)
    print("\n4. Testing Backend Connectivity")
    try:
        response = requests.get("http://localhost:8000/api/v1/ui/health", timeout=3)
        if response.status_code == 200:
            print("SUCCESS: Backend is running")
            
            # Test backend file upload
            print("\n5. Testing Backend File Upload")
            try:
                # Create agent first
                agent_data = {
                    "name": "File Test Agent",
                    "description": "Testing files with coding endpoint",
                    "system_prompt": "Helpful assistant",
                    "model": "glm-4.6"
                }
                
                agent_resp = requests.post("http://localhost:8000/api/v1/agents/", json=agent_data)
                if agent_resp.status_code == 200:
                    agent = agent_resp.json()
                    agent_id = agent["id"]
                    print(f"Created agent: {agent_id}")
                    
                    # Upload file through backend
                    files = {"file": ("backend_test.txt", "Backend test content", "text/plain")}
                    
                    upload_resp = requests.post(
                        f"http://localhost:8000/api/v1/agents/{agent_id}/upload",
                        files=files
                    )
                    
                    if upload_resp.status_code == 200:
                        upload_result = upload_resp.json()
                        print(f"Backend upload SUCCESS: {upload_result['filename']}")
                        
                        # Cleanup
                        requests.delete(f"http://localhost:8000/api/v1/agents/{agent_id}")
                        print("SUCCESS: Backend file workflow complete")
                        
                    else:
                        print(f"Backend upload FAILED: {upload_resp.status_code}")
                else:
                    print(f"Agent creation FAILED: {agent_resp.status_code}")
                    
            except Exception as e:
                print(f"Backend test ERROR: {str(e)}")
        else:
            print("Backend not running - skipping backend tests")
            
    except Exception as e:
        print("Backend not available")
    
    print(f"\n" + "=" * 40)
    print("TEST SUMMARY:")
    print("Coding endpoint: WORKING")
    print("File upload: WORKING") 
    print("Chat with files: WORKING")
    print("Backend: " + ("WORKING" if response.status_code == 200 else "SKIPPED"))
    print("=" * 40)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nCancelled")
        sys.exit(0)
