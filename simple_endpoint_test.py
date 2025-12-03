#!/usr/bin/env python3
"""
Simple endpoint test without unicode characters
"""

import requests
import os
from dotenv import load_dotenv

def test_endpoints():
    print("Z.ai API Endpoint Test")
    print("=" * 30)
    
    api_key = os.getenv("ZAI_API_KEY")
    if not api_key:
        print("No API key found")
        return
    
    print(f"Using API key: {api_key[:15]}...")
    
    # Test endpoints
    endpoints = [
        ("Main - Files", "https://api.z.ai/api/paas/v4/files"),
        ("Coding - Files", "https://api.z.ai/api/coding/paas/v4/files"),
    ]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    print("\nTesting file endpoints:")
    
    for name, url in endpoints:
        try:
            # Test POST with file
            content = "test file content"
            files = {
                'file': ('test.txt', content, 'text/plain'),
                'purpose': (None, 'agent')
            }
            
            response = requests.post(url, headers=headers, files=files, timeout=10)
            status = response.status_code
            
            if status == 200:
                print(f"OK: {name} - File upload works")
                result = response.json()
                print(f"   File ID: {result.get('id')}")
                print(f"   Filename: {result.get('filename')}")
            elif status == 404:
                print(f"FAIL: {name} - Endpoint not found ({status})")
            elif status == 401:
                print(f"AUTH: {name} - Unauthorized ({status})")
            elif status == 429:
                print(f"BALANCE: {name} - Insufficient balance ({status})")
            else:
                print(f"ERROR: {name} - {status}")
                print(f"   Response: {response.text[:200]}")
            
        except Exception as e:
            print(f"CRASH: {name} - {str(e)[:50]}")
    
    # Test if we can use main endpoint for files but coding for chat
    print(f"\n" + "=" * 30)
    print("Testing hybrid approach:")
    
    try:
        # Upload file using main endpoint
        print("Step 1: Upload file using main endpoint...")
        
        main_files_url = "https://api.z.ai/api/paas/v4/files"
        content = "Test file for hybrid approach."
        files = {
            'file': ('hybrid_test.txt', content, 'text/plain'),
            'purpose': (None, 'agent')
        }
        
        upload_response = requests.post(main_files_url, headers=headers, files=files)
        
        if upload_response.status_code == 200:
            upload_result = upload_response.json()
            file_id = upload_result.get('id')
            print(f"SUCCESS: File uploaded to main endpoint")
            print(f"File ID: {file_id}")
            
            # Step 2: Try to chat using coding endpoint with file reference
            print("Step 2: Chat using coding endpoint with file reference...")
            
            from openai import OpenAI
            client = OpenAI(api_key=api_key, base_url="https://api.z.ai/api/coding/paas/v4")
            
            chat_response = client.chat.completions.create(
                model="glm-4.6",
                messages=[
                    {"role": "user", "content": f"Based on the uploaded file (ID: {file_id}), what does it contain?"}
                ],
                max_tokens=50
            )
            
            chat_content = chat_response.choices[0].message.content
            print(f"SUCCESS: Chat works with file reference")
            print(f"Response: {chat_content}")
            
            print("\nCONCLUSION: Hybrid approach works!")
            print(" - Upload files to main endpoint")
            print(" - Use files in chat with coding endpoint")
            
        else:
            print(f"File upload failed: {upload_response.status_code}")
            print(f"Response: {upload_response.text}")
            
    except Exception as e:
        print(f"Hybrid test failed: {str(e)}")

if __name__ == "__main__":
    test_endpoints()
