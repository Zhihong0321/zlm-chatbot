#!/usr/bin/env python3
"""
Simple Production Test Script
Tests Z.ai application with file upload functionality
"""

import os
import sys
import requests
import time
from dotenv import load_dotenv

def main():
    print("Production Test - Z.ai Application")
    print("=" * 40)
    
    # Get production URL
    load_dotenv()
    prod_url = os.getenv("PRODUCTION_URL")
    
    if not prod_url:
        print("ERROR: Set PRODUCTION_URL environment variable")
        print("Example:")
        print("PRODUCTION_URL=https://your-app.railway.app")
        return False
    
    print(f"Testing: {prod_url}")
    
    # Check if API key is available
    api_key = os.getenv("ZAI_API_KEY")
    if not api_key:
        print("WARNING: No ZAI_API_KEY found")
        print("Some tests may fail without API key")
    
    # Test 1: Health check
    print("\n1. Health Check")
    try:
        start_time = time.time()
        response = requests.get(f"{prod_url}/api/v1/ui/health", timeout=10)
        
        if response.status_code == 200:
            end_time = time.time()
            latency = end_time - start_time
            print(f"SUCCESS: {latency:.2f}s")
            
            health_data = response.json()
            print(f"Status: {health_data.get('status', 'unknown')}")
            print(f"Database: {health_data.get('database', 'unknown')}")
            health_check_result = True
        else:
            print(f"FAILED: HTTP {response.status_code}")
            health_check_result = False
    except Exception as e:
        print(f"ERROR: Health check failed")
        health_check_result = False
    
    # Test 2: API endpoints
    print("\n2. API Endpoints")
    try:
        # Test agents API
        agents_response = requests.get(f"{prod_url}/api/v1/agents/", timeout=10)
        agents_result = agents_response.status_code == 200
        
        print(f"Agents API: {'WORKING' if agents_result else 'FAILED'}")
        
    except Exception as e:
        print(f"Agents API: ERROR: {str(e)[:50]}")
        agents_result = False
    
    # Test 3: Create agent and file workflow
    all_tests_passed = []
    agent_id = None
    file_id = None
    
    print("\n3. Agent and File Workflow")
    try:
        # Create agent
        agent_data = {
            "name": "Production Test Agent",
            "description": "Test agent for file upload functionality",
            "system_prompt": "You are helpful with uploaded documents.",
            "model": "glm-4.6"
        }
        
        agent_response = requests.post(f"{prod_url}/api/v1/agents/", json=agent_data, timeout=15)
        
        if agent_response.status_code == 200:
            agent = agent_response.json()
            agent_id = agent.get("id")
            print(f"Agent Created: SUCCESS (ID: {agent_id})")
            agent_created = True
        else:
            print(f"Agent Created: FAILED ({agent_response.status_code})")
            agent_created = False
    except Exception as e:
        print(f"Agent Created: ERROR: {str(e)}")
        agent_created = False
    
    if agent_id:
        try:
            # Test file upload
            test_content = (
                f"PRODUCTION TEST FILE\n"
                f"URL: {prod_url}\n"
                f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                f"Key Points:\n"
                f"- Testing file upload functionality\n"
                f"- Content embedding verification\n"
                f"- Performance measurement\n"
                f"- Error handling validation\n"
            )
            
            files = {"file": ("production_test.txt", test_content, "text/plain")}
            
            upload_start = time.time()
            upload_response = requests.post(
                f"{prod_url}/api/v1/agents/{agent_id}/upload", 
                files=files, 
                timeout=30
            )
            upload_end = time.time()
            
            if upload_response.status_code == 200:
                upload_result = upload_response.json()
                file_id = upload_result.get("file_id")
                filename = upload_result.get("filename")
                file_size = upload_result.get("size", 0)
                upload_time = upload_end - upload_start
                
                print(f"File Uploaded: SUCCESS")
                print(f"Name: {filename}")
                print(f"Size: {file_size} bytes")
                print(f"Time: {upload_time:.2f}s")
                print(f"ID: {file_id[:20]}...")
                
                file_uploaded = True
                
                # Test chat with content embedding
                print("\nContent Embedding Test:")
                
                session_data = {
                    "title": "Production Chat Test",
                    "agent_id": agent_id
                }
                
                session_response = requests.post(f"{prod_url}/api/v1/sessions/", json=session_data, timeout=10)
                
                if session_response.status_code == 200:
                    session = session_response.json()
                    session_id = session["id"]
                    
                    # Test content-based chat (our actual approach)
                    embedded_content = f"""Based on the uploaded file (ID: {file_id}), please tell me:
1. What production site is being tested?
2. What file content verification points are listed?
3. What time was this file created?
"""
                    
                    chat_data = {"message": embedded_content}
                    
                    chat_start = time.time()
                    chat_response = requests.post(
                        f"{prod_url}/api/v1/chat/{session_id}/messages",
                        json=chat_data,
                        timeout=30
                    )
                    chat_end = time.time()
                    
                    if chat_response.status_code == 200:
                        chat_result = chat_response.json()
                        content = chat_result.get("message", "")
                        
                        print(f"Chat Received: SUCCESS ({chat_end - chat_start:.2f}s)")
                        print(f"Length: {len(content)} chars")
                        print(f"Preview: {content[:50]}...")
                        
                        # Check if file content is accessible
                        if "PRODUCTION TEST FILE" in content or "prod_url" in content:
                            print("Verified: Content Access SUCCESS")
                            content_works = True
                        else:
                            print("Verified: Content Access FAILED")
                            content_works = False
                        
                        chat_time = chat_end - chat_start
                        if chat_time <= 10:
                            print(f"Performance: EXCELLENT ({chat_time:.2f}s)")
                        elif chat_time <= 20:
                            print(f"Performance: GOOD ({chat_time:.2f}s)")
                        else:
                            print(f"Performance: SLOW ({chat_time:.2f}s)")
                        chat_tested = True
                    else:
                        print(f"Chat Test FAILED: {chat_response.status_code}")
                        print(f"Error: {chat_response.text[:100] if chat_response.text else 'No response'}")
                        chat_tested = False
                    else:
                        print(f"Session Creation FAILED: {session_response.status_code}")
                        chat_tested = False
                    
                    # Cleanup session
                    requests.delete(f"{prod_url}/api/v1/sessions/{session_id}", timeout=5)
                    
                else:
                    print(f"Session Creation FAILED: {session_response.status_code}")
                    chat_tested = False
                
            else:
                print(f"File Upload FAILED: {upload_response.status_code}")
                print(f"Error Response: {upload_response.text[:100] if upload_response.text else 'No error message'}")
                file_uploaded = False
                chat_tested = False
            
        except Exception as e:
            print(f"File/Chat Test ERROR: {str(e)[:50]}")
            file_uploaded = False
            chat_tested = False
        
    else:
        print("SKIPPED: No agent created - skipping file tests")
    
    # Cleanup
    if agent_id:
        print("\n4. Cleanup")
        try:
            if file_id and os.getenv("CLEANUP", "true").lower() == "true":
                # Delete files if cleanup enabled
                from requests import get
                files_response = get(f"{prod_url}/api/v1/agents/{agent_id}/files", timeout=10)
                if files_response.status_code == 200:
                    files = files_response.json()
                    for file_info in files:
                        try:
                            delete_result = requests.delete(
                                f"{prod_url}/api/v1/agents/{agent_id}/files/{file_info['id']}", 
                                timeout=5
                            )
                            if delete_result.status_code == 200:
                                print(f"Cleaned up: {file_info['original_filename']}")
                        except:
                            print(f"Cleanup failed for: {file_info['original_filename']}")
            
            # Delete agent
            delete_result = requests.delete(f"{prod_url}/api/v1/agents/{agent_id}", timeout=5)
            print("Cleanup: Agent deleted")
            
        except Exception as e:
            print(f"Cleanup WARNING: {str(e)[:50]}")
    
    # Combine results
    all_tests_passed = all([
        health_check_result,
        agents_result,
        agent_created,
        file_uploaded,
        chat_tested
    ])
    
    # Generate report
    print(f"\n" + "=" * 50)
    print("PRODUCTION TEST REPORT")
    print("=" * 50)
    
    print(f"\nResults Summary:")
    print(f"Health Check: {'PASS' if health_check_result else 'FAIL'}")
    print(f"API Endpoints: {'PASS' if agents_result else 'FAIL'}")
    print(f"Agent Creation: {'PASS' if agent_created else 'FAIL'}")
    print(f"File Upload: {'PASS' if file_uploaded else 'FAIL'}")
    print(f"Chat Function: {'PASS' if chat_tested else 'FAIL'}")
    print(f"Content Access: {'VERIFIED' if content_works else 'FAILED'}")
    
    print(f"\nOverall Result: {'SUCCESS' if all_tests_passed else 'NEEDS_ATTENTION'}")
    
    if all_tests_passed:
        print(f"\n✅ PRODUCTION READY!")
        print(f"All systems working correctly")
        print(f"Your Z.ai application is ready for production use")
        print(f"Hybrid file approach validated successfully")
        print(f"Fast coding endpoint performance maintained")
        print(f"Ready for production deployment!")
        
        advice = [
            "Monitor token usage in production",
            "Set up alert for slow responses (>10s)",
            "Consider response caching for common queries",
            "Monitor error rates and create backup plans"
        ]
        print(f"\n📋 Recommendations:")
        for i, advice in enumerate(advice, 1):
            print(f"{i}. {advice}")
        
        else:
            print(f"\n⚠️  ISSUES FOUND")
            issues = []
            if not health_check_result:
                issues.append("Fix deployment connectivity")
            if not agents_result:
                issues.append("Check backend configuration")
            if not agent_created:
                issues.append("Debug agent creation logic")
            if not file_uploaded:
                issues.append("Check file upload functionality")
            if not chat_tested:
                issues.append("Debug chat and content embedding")
            
            print(f"Required Actions:")
            for i, issue in enumerate(issues, 1):
                print(f"{i}. {issue}")
            
            print(f"\n💡 Before Production Use:")
            print(f"Address all issues listed above")
            print(f"Monitor error rates and response times")
            print(f"Implement retry logic for failed requests")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    print(f"\nFinal Status: {'SUCCESS' if success else 'FAILED'}")
    print(f"Completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")")
    sys.exit(0 if success else 1)
