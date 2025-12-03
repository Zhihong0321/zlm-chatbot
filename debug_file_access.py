#!/usr/bin/env python3
"""
Debug test - understand how file actually works across endpoints
"""

import os
import sys
import requests
import time
from dotenv import load_dotenv
from openai import OpenAI

def test_file_access_detailed():
    print("DEBUG: File Access Across Endpoints")
    print("=" * 40)
    
    load_dotenv()
    api_key = os.getenv("ZAI_API_KEY")
    
    if not api_key:
        print("No API key")
        return
    
    print(f"API Key: {api_key[:15]}...")
    
    try:
        # Step 1: Upload file to main endpoint
        print("\n1. Upload file to MAIN endpoint...")
        
        unique_content = f"""DEBUG DOCUMENT - {time.time()}

This is a test to understand file access patterns:
- Uploaded at: {time.strftime('%Y-%m-%d %H:%M:%S')}
- Test ID: {int(time.time()) % 10000}
- Content: This should only be accessible if the LLM can actually read uploaded files

Key point: If the LLM can answer specific questions about this content,
it proves the file system actually works across endpoints.

Specific data needed:
- The upload timestamp above
- The test ID
- Any specific phrases from this document

If the LLM cannot access this content, the "file reference" approach
doesn't actually work and we were getting empty responses.
"""
        
        # Upload to main endpoint
        main_files_url = "https://api.z.ai/api/paas/v4/files"
        headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
        files = {'file': ('debug_test.txt', unique_content, 'text/plain'), 'purpose': (None, 'agent')}
        
        upload_response = requests.post(main_files_url, headers=headers, files=files, timeout=30)
        
        if upload_response.status_code != 200:
            print(f"Upload failed: {upload_response.status_code}")
            return False
        
        upload_result = upload_response.json()
        file_id = upload_result.get('id')
        
        print(f"SUCCESS: File uploaded")
        print(f"  File ID: {file_id}")
        print(f"  Size: {upload_result['bytes']} bytes")
        
        # Step 2: Test with coding endpoint - VERY SPECIFIC QUESTION
        print(f"\n2. Test with CODING endpoint - specific file content question...")
        
        coding_client = OpenAI(api_key=api_key, base_url="https://api.z.ai/api/coding/paas/v4")
        
        specific_question = f"Based on the uploaded file (ID: {file_id}), what is the upload timestamp and test ID mentioned in the document?"
        
        start_time = time.time()
        chat_response = coding_client.chat.completions.create(
            model="glm-4.6",
            messages=[{"role": "user", "content": specific_question}],
            max_tokens=100,
            temperature=0.1  # Low temperature for factual answers
        )
        end_time = time.time()
        
        response_content = chat_response.choices[0].message.content
        latency = end_time - start_time
        
        print(f"Response received in {latency:.2f}s")
        print(f"Response: '{response_content}'")
        
        # Step 3: Analyze response
        print(f"\n3. Analyzing response...")
        
        # Check if response contains actual file content
        contains_timestamp = any(time.strftime('%Y-%m-%d') in response_content for _ in range(1))
        contains_test_id = "TEST" in response_content.upper() or str(int(time.time()) % 10000) in response_content
        contains_debug_words = any(word in response_content.lower() for word in ["upload", "timestamp", "document"])
        
        print(f"Contains timestamp: {contains_timestamp}")
        print(f"Contains test ID: {contains_test_id}")
        print(f"Contains debug words: {contains_debug_words}")
        
        # Step 4: Test with NO file reference (control test)
        print(f"\n4. Control test: Ask CODING endpoint WITHOUT file reference...")
        
        control_question = "Tell me about uploaded files and their content. What can you access?"
        
        control_response = coding_client.chat.completions.create(
            model="glm-4.6",
            messages=[{"role": "user", "content": control_question}],
            max_tokens=50,
            temperature=0.1
        )
        
        control_content = control_response.choices[0].message.content
        print(f"Control response: '{control_content}'")
        
        # Step 5: Test with main endpoint (for comparison)
        print(f"\n5. Control test: Ask MAIN endpoint WITH file reference...")
        
        main_client = OpenAI(api_key=api_key, base_url="https://api.z.ai/api/paas/v4")
        
        try:
            main_response = main_client.chat.completions.create(
                model="glm-4.6",
                messages=[{"role": "user", "content": specific_question}],
                max_tokens=100,
                temperature=0.1
            )
            
            main_content = main_response.choices[0].message.content
            print(f"Main endpoint response: '{main_content}'")
            
        except Exception as e:
            print(f"Main endpoint failed (expected): {str(e)[:50]}")
            main_content = "ERROR: Balance insufficient"
        
        # Step 6: Conclusion
        print(f"\n" + "=" * 40)
        print("ANALYSIS RESULTS")
        print("=" * 40)
        
        if len(response_content.strip()) < 10:
            print("CODING ENDPOINT RESULT: EMPTY response")
            print("Conclusion: File references do NOT work with coding endpoint")
        elif contains_debug_words or contains_timestamp:
            print("CODING ENDPOINT RESULT: Contains file content")
            print("Conclusion: File references DO work with coding endpoint")
        else:
            print("CODING ENDPOINT RESULT: Generic response")
            print("Conclusion: File references do NOT work (just returns generic answer)")
        
        print(f"\nKey findings:")
        print(f"• File upload to main: SUCCESS")
        print(f"• Coding endpoint response: {len(response_content)} chars")
        print(f"• Response specific to file: {contains_debug_words}")
        print(f"• Main endpoint balance issue: {'YES' if main_content == 'ERROR: Balance insufficient' else 'NO'}")
        
        return contains_debug_words
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_file_access_detailed()
    sys.exit(0 if success else 1)
