#!/usr/bin/env python3
"""
Discover which endpoints are available on coding vs main Z.ai API
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_endpoint_availability():
    print("Z.ai API Endpoint Discovery Test")
    print("=" * 40)
    
    api_key = os.getenv("ZAI_API_KEY")
    if not api_key:
        print("No API key found")
        return
    
    print(f"Using API key: {api_key[:15]}...")
    
    # Test different endpoints
    endpoints = [
        ("Main - Chat", "https://api.z.ai/api/paas/v4/chat/completions"),
        ("Coding - Chat", "https://api.z.ai/api/coding/paas/v4/chat/completions"),
        ("Main - Files", "https://api.z.ai/api/paas/v4/files"),
        ("Coding - Files", "https://api.z.ai/api/coding/paas/v4/files"),
        ("Main - Models", "https://api.z.ai/api/paas/v4/models"),
        ("Coding - Models", "https://api.z.ai/api/coding/paas/v4/models"),
    ]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print("\nTesting endpoint availability:")
    
    for name, url in endpoints:
        try:
            if "files" in url:
                # Test with multipart/form-data for files
                content = "test file content"
                file_headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Accept": "application/json"
                }
                files = {
                    'file': ('test.txt', content, 'text/plain'),
                    'purpose': (None, 'agent')
                }
                
                response = requests.post(url, headers=file_headers, files=files, timeout=5)
                method = "POST"
            else:
                # Test GET for models, POST for chat
                if "models" in url:
                    response = requests.get(url, headers=headers, timeout=5)
                    method = "GET"
                else:
                    # Test chat endpoint
                    chat_data = {
                        "model": "glm-4.6",
                        "messages": [{"role": "user", "content": "test"}],
                        "max_tokens": 1
                    }
                    response = requests.post(url, headers=headers, json=chat_data, timeout=5)
                    method = "POST"
            
            status = response.status_code
            if status == 200:
                print(f"✅ {name}: {method} - AVAILABLE ({status})")
            elif status == 404:
                print(f"❌ {name}: {method} - NOT FOUND ({status})")
            elif status == 401:
                print(f"🔒 {name}: {method} - UNAUTHORIZED ({status})")
            elif status == 429:
                print(f"💰 {name}: {method} - INSUFFICIENT BALANCE ({status})")
            else:
                print(f"⚠️  {name}: {method} - ERROR ({status})")
                print(f"    Response: {response.text[:100]}...")
            
        except requests.exceptions.Timeout:
            print(f"⏰ {name}: {method} - TIMEOUT")
        except requests.exceptions.ConnectionError:
            print(f"🔌 {name}: {method} - CONNECTION FAILED")
        except Exception as e:
            print(f"💥 {name}: {method} - CRASH - {str(e)[:50]}")
    
    print(f"\n" + "=" * 40)
    print("Key Findings:")
    
    # Test if coding endpoint has file upload
    print("Checking file upload endpoints...")
    
    coding_files_url = "https://api.z.ai/api/coding/paas/v4/files"
    main_files_url = "https://api.z.ai/api/paas/v4/files"
    
    # Try to get file upload API docs/info
    try:
        # Test if files endpoint exists on coding
        files_headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json"
        }
        
        resp = requests.get(coding_files_url, headers=files_headers, timeout=5)
        print(f"Coding files GET: {resp.status_code}")
        
        resp2 = requests.get(main_files_url, headers=files_headers, timeout=5)
        print(f"Main files GET: {resp2.status_code}")
        
    except Exception as e:
        print(f"File endpoint check failed: {e}")
    
    print("\nNext steps:")
    print("• If coding files endpoint is 404, files only work on main endpoint")
    print("• Need to check Z.ai documentation or support")
    print("• May need alternative approach for file management")

if __name__ == "__main__":
    test_endpoint_availability()
