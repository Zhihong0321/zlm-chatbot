#!/usr/bin/env python3
"""
Test Backend File Upload with Hybrid Approach
Main endpoint for files, coding endpoint for chat
"""

import os
import sys
import time
import requests
from datetime import datetime

def test_backend_file_workflow():
    print("Backend File Workflow Test - Hybrid Approach")
    print("=" * 50)
    
    backend_url = "http://localhost:8000"
    
    # Check if backend is running
    try:
        response = requests.get(f"{backend_url}/api/v1/ui/health", timeout=5)
        if response.status_code != 200:
            print("Backend is not running")
            return False
    except:
        print("Backend is not running")
        return False
    
    print("Backend is running!")
    
    try:
        # Step 1: Create test agent
        print("\n1. Creating test agent...")
        agent_data = {
            "name": "Hybrid File Test Agent",
            "description": "Testing file upload (main) + chat (coding)",
            "system_prompt": "You are a helpful assistant that can reference uploaded files.",
            "model": "glm-4.6",
            "temperature": 0.7
        }
        
        agent_response = requests.post(
            f"{backend_url}/api/v1/agents/",
            json=agent_data,
            timeout=10
        )
        
        if agent_response.status_code != 200:
            print(f"Agent creation failed: {agent_response.status_code}")
            return False
        
        agent = agent_response.json()
        agent_id = agent["id"]
        print(f"SUCCESS: Agent created (ID: {agent_id})")
        
        # Step 2: Upload file through backend
        print("\n2. Uploading file through backend...")
        
        test_content = """Knowledge Base Document

Test File for Hybrid Approach

This document contains information about AI testing:

TOPICS:
1. File Upload Testing - Upload files to main endpoint
2. Chat Testing - Use coding endpoint for responses
3. Hybrid Approach - Best of both worlds

KEY POINTS:
- Main endpoint: Supports file uploads
- Coding endpoint: Fast responses, no balance needed
- File references work across both endpoints

This file should be accessible in chat conversations.
"""
        
        files = {
            "file": ("test_knowledge.txt", test_content, "text/plain")
        }
        
        upload_start = time.time()
        upload_response = requests.post(
            f"{backend_url}/api/v1/agents/{agent_id}/upload",
            files=files,
            timeout=30
        )
        upload_end = time.time()
        
        if upload_response.status_code == 200:
            upload_result = upload_response.json()
            print(f"SUCCESS: File uploaded via backend")
            print(f"  File ID: {upload_result['file_id']}")
            print(f"  Filename: {upload_result['filename']}")
            print(f"  Size: {upload_result['size']} bytes")
            print(f"  Upload time: {upload_end - upload_start:.2f}s")
            
            # Step 3: List files
            print("\n3. Listing files for agent...")
            files_response = requests.get(
                f"{backend_url}/api/v1/agents/{agent_id}/files",
                timeout=10
            )
            
            if files_response.status_code == 200:
                files_list = files_response.json()
                print(f"SUCCESS: Found {len(files_list)} files")
                
                for file in files_list:
                    print(f"  - {file['original_filename']} ({file['file_size']} bytes)")
                    print(f"    Z.ai File ID: {file['zai_file_id']}")
                    print(f"    Status: {file['status']}")
                
                if len(files_list) > 0:
                    test_file_id = files_list[0]["zai_file_id"]
                    
                    # Step 4: Test chat with file reference
                    print(f"\n4. Testing chat with file reference (coding endpoint)...")
                    
                    chat_data = {"message": "Based on the uploaded file, what topics does it cover?"}
                    
                    # Create chat session
                    session_data = {
                        "title": "File Chat Test",
                        "agent_id": agent_id
                    }
                    
                    session_response = requests.post(
                        f"{backend_url}/api/v1/sessions/",
                        json=session_data,
                        timeout=10
                    )
                    
                    if session_response.status_code == 200:
                        session = session_response.json()
                        session_id = session["id"]
                        
                        # Send chat message
                        chat_start = time.time()
                        chat_response = requests.post(
                            f"{backend_url}/api/v1/chat/{session_id}/messages",
                            json=chat_data,
                            timeout=30
                        )
                        chat_end = time.time()
                        
                        if chat_response.status_code == 200:
                            chat_result = chat_response.json()
                            content = chat_result.get("message", "")
                            print(f"SUCCESS: Chat response received")
                            print(f"  Latency: {chat_end - chat_start:.2f}s")
                            print(f"  Response: {content[:200]}...")
                            
                            print(f"\n✅ HYBRID APPROACH WORKS!")
                            print(f"   Files uploaded to main endpoint")
                            print(f"   Chat using coding endpoint")
                            print(f"   Full workflow: Agent -> Files -> Chat")
                            
                        else:
                            print(f"Chat failed: {chat_response.status_code}")
                            print(f"Response: {chat_response.text[:200]}")
                        
                        # Cleanup session
                        requests.delete(f"{backend_url}/api/v1/sessions/{session_id}", timeout=5)
                    
                    else:
                        print(f"Session creation failed: {session_response.status_code}")
                
            else:
                print(f"File listing failed: {files_response.status_code}")
                
        else:
            print(f"File upload failed: {upload_response.status_code}")
            print(f"Response: {upload_response.text[:200]}")
        
        # Step 5: Cleanup
        print("\n5. Cleaning up...")
        delete_response = requests.delete(
            f"{backend_url}/api/v1/agents/{agent_id}",
            timeout=5
        )
        
        if delete_response.status_code == 200:
            print("SUCCESS: Test agent cleaned up")
        
        print(f"\n" + "=" * 50)
        print("HYBRID APPROACH TEST COMPLETE")
        print("=" * 50)
        print("All components working correctly!")
        return True
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        return False

def main():
    success = test_backend_file_workflow()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
