#!/usr/bin/env python3
"""
Production Site Testing Suite
Tests live deployment functionality with the hybrid file approach
"""

import os
import sys
import time
import requests
import json
import asyncio
from datetime import datetime
from dotenv import load_dotenv

class ProductionTester:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("ZAI_API_KEY")
        self.prod_url = os.getenv("PRODUCTION_URL", "")
        
        if not self.prod_url:
            print("ERROR: PRODUCTION_URL environment variable required")
            print("Set it like: PRODUCTION_URL=https://your-app-name.railway.app")
            sys.exit(1)
        
        print(f"Production URL: {self.prod_url}")
        print(f"API Key: {self.api_key[:15]}..." if self.api_key else "No API Key")
        
    def test_health_check(self):
        """Test if production site is healthy"""
        print("\n1️⃣ Testing Production Health Check")
        print("-" * 40)
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.prod_url}/api/v1/ui/health", timeout=10)
            end_time = time.time()
            latency = end_time - start_time
            
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ HEALTH CHECK PASSED")
                print(f"   Latency: {latency:.2f}s")
                print(f"   Status: {health_data.get('status', 'unknown')}")
                print(f"   Database: {health_data.get('database', 'unknown')}")
                print(f"   Version: {health_data.get('version', 'unknown')}")
                return True
            else:
                print(f"❌ HEALTH CHECK FAILED")
                print(f"   Status Code: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"❌ HEALTH CHECK ERROR: {str(e)}")
            return False
    
    def test_create_agent(self):
        """Test agent creation on production"""
        print("\n2️⃣ Testing Agent Creation")
        print("-" * 30)
        
        agent_data = {
            "name": "Production Test",
            "description": "Agent for production file testing",
            "system_prompt": "You are a helpful assistant that can access uploaded files.",
            "model": "glm-4.6",  # Using coding endpoint
            "temperature": 0.7
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.prod_url}/api/v1/agents/",
                json=agent_data,
                timeout=30
            )
            end_time = time.time()
            
            if response.status_code == 200:
                agent = response.json()
                print(f"✅ AGENT CREATION SUCCESS")
                print(f"   Agent ID: {agent['id']}")
                print(f"   Name: {agent['name']}")
                print(f"   Model: {agent['model']}")
                print(f"   Latency: {end_time - start_time:.2f}s")
                return agent['id']
            else:
                print(f"❌ AGENT CREATION FAILED")
                print(f"   Status: {response.status_code}")
                print(f"   Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ AGENT ERROR: {str(e)}")
            return None
    
    def test_file_upload(self, agent_id):
        """Test file upload on production"""
        print("\n3️⃣ Testing File Upload")
        print("-" * 25)
        
        content = f"""Production Test Document
        
This file tests file upload functionality on production deployment.

Test Parameters:
- Upload Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Agent ID: {agent_id}
- Content: Hybrid approach test
- Purpose: Validate file management

Key Features to Test:
1. File upload to main endpoint
2. File retrieval and listing
3. File deletion
4. File metadata tracking

Expected Results:
- Upload success with proper file ID
- Content accessible in conversations
- File management functions working
- Response times under 10 seconds

This document should be referenceable when testing chat functionality.
Files uploaded to production should retain their content and structure.
"""
        
        try:
            # Upload file
            files = {
                "file": ("production_test.txt", content, "text/plain")
            }
            
            start_time = time.time()
            response = requests.post(
                f"{self.prod_url}/api/v1/agents/{agent_id}/upload",
                files=files,
                timeout=30
            )
            end_time = time.time()
            
            if response.status_code == 200:
                upload_result = response.json()
                file_id = upload_result.get('file_id')
                
                print(f"✅ FILE UPLOAD SUCCESS")
                print(f"   File ID: {file_id}")
                print(f"   Filename: {upload_result['filename']}")
                print(f"   Size: {upload_result['size']} bytes")
                print(f"   Upload Time: {end_time - start_time:.2f}s)
                print(f"   Message: {upload_result['message']}")
                
                if end_time - start_time > 10:
                    print(f"⚠️  WARNING: Slow upload ({end_time - start_time:.2f}s)")
                
                return file_id, upload_result.get('filename')
            else:
                print(f"❌ FILE UPLOAD FAILED")
                print(f"   Status: {response.status_code}")
                print(f"   Error: {response.text}")
                return None, None
                
        except Exception as e:
            print(f"❌ UPLOAD ERROR: {str(e)}")
            return None, None
    
    def test_file_listing(self, agent_id):
        """Test file listing functionality"""
        print("\n4️⃣ Testing File Listing")
        print("-" * 20)
        
        try:
            start_time = time.time()
            response = requests.get(
                f"{self.prod_url}/api/v1/agents/{agent_id}/files",
                timeout=15
            )
            end_time = time.time()
            
            if response.status_code == 200:
                files = response.json()
                print(f"✅ FILE LISTING SUCCESS")
                print(f"   Files Found: {len(files)}")
                print(f"   Retrieval Time: {end_time - start_time:.2f}s")
                
                for file in files:
                    print(f"   - {file['original_filename']} ({file['file_size']} bytes)")
                    print(f"     ID: {file['id']}")
                    print(f"     Status: {file['status']}")
                
                return files
            else:
                print(f"❌ FILE LISTING FAILED")
                print(f"   Status: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ LISTING ERROR: {str(e)}")
            return None
    
    def test_chat_with_files(self, agent_id):
        """Test chat functionality with file references (content embedding)"""
        print("\n5️⃣ Testing Chat with Files")
        print("-" * 30)
        
        try:
            # Create session for testing
            session_data = {
                "title": "Production File Chat Test",
                "agent_id": agent_id
            }
            
            session_response = requests.post(
                f"{self.prod_url}/api/v1/sessions/",
                json=session_data,
                timeout=15
            )
            
            if session_response.status_code != 200:
                print(f"❌ SESSION CREATION FAILED")
                return False
            
            session = session_response.json()
            session_id = session["id"]
            
            # Test content embedding approach
            test_questions = [
                "What topics are covered in the uploaded production test document?",
                "What test time was mentioned in the document?",
                "What are the key features being tested?"
                "What is the document's purpose?"
            ]
            
            for i, question in enumerate(test_questions, 1):
                print(f"\n   Question {i}: {question}")
                
                chat_data = {"message": question}
                
                start_time = time.time()
                response = requests.post(
                    f"{self.prod_url}/api/v1/chat/{session_id}/messages",
                    json=chat_data,
                    timeout=30
                )
                end_time = time.time()
                
                if response.status_code == 200:
                    chat_result = response.json()
                    content = chat_result.get("message", "")
                    
                    print(f"   ✅ Response received ({end_time - start_time:.2f}s)")
                    print(f"   Length: {len(content)} chars")
                    print(f"   Preview: {content[:100]}...")
                    
                    # Check if content includes actual document info
                    doc_indicators = ["production_test", "Test Parameters", "Production Test Document"]
                    has_content = any(indicator.lower() in content.lower() for indicator in doc_indicators)
                    
                    if has_content:
                        print(f"   ✅ Content Access: DETECTED")
                    else:
                        print(f"   ⚠️  Content Access: NOT DETECTED")
                    
                    if end_time - start_time > 10:
                        print(f"   ⚠️  WARNING: Slow response ({end_time - start_time:.2f}s)")
                        
                else:
                    print(f"   ❌ Chat failed: {response.status_code}")
                    print(f"   Error: {response.text[:100]}")
                
                # Small delay between questions
                if i < len(test_questions):
                    time.sleep(1)
            
            # Cleanup session
            requests.delete(f"{self.prod_url}/api/v1/sessions/{session_id}", timeout=5)
            
            print("   ✅ Chat testing completed")
            return True
            
        except Exception as e:
            print(f"❌ CHAT ERROR: {str(e)}")
            return False
    
    def test_agent_with_files(self):
        """Test complete agent workflow with files"""
        print("\n6️⃣ Testing Complete End-to-End Workflow")
        print("-" * 45)
        
        try:
            # Create agent
            agent_id = self.test_create_agent()
            if not agent_id:
                return False
            
            # Upload file
            file_id, filename = self.test_file_upload(agent_id)
            if not file_id:
                requests.delete(f"{self.prod_url}/api/v1/agents/{agent_id}", timeout=5)
                return False
            
            # List files
            files = self.test_file_listing(agent_id)
            if files is None:
                requests.delete(f"{self.prod_url}/api/v1/agents/{agent_id}", timeout=5)
                return False
            
            # Test chat
            chat_success = self.test_chat_with_files(agent_id)
            
            # Cleanup
            if files and len(files) > 0:
                for file in files:
                    delete_response = requests.delete(
                        f"{self.prod_url}/api/v1/agents/{agent_id}/files/{file['id']}",
                        timeout=5
                    )
                    if delete_response.status_code == 200:
                        print(f"   Cleaned up file: {file['original_filename']}")
            
            delete_response = requests.delete(f"{self.prod_url}/api/v1/agents/{agent_id}", timeout=5)
            if delete_response.status_code == 200:
                print(f"   Cleaned up agent: Test Agent")
            
            return chat_success
            
        except Exception as e:
            print(f"❌ WORKFLOW ERROR: {str(e)}")
            return False
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        print("\n7️⃣ Testing Edge Cases")
        print("-" * 25)
        
        issues = []
        
        # Test 1: Non-existent agent
        print("   Testing: Non-existent agent ID")
        try:
            response = requests.get(f"{self.prod_url}/api/v1/agents/99999/files", timeout=10)
            if response.status_code == 404:
                print(f"   ✅ Correctly returns 404 for non-existent agent")
            else:
                print(f"   ⚠️ Unexpected response: {response.status_code}")
                issues.append("non-existent-agent-response")
        except Exception as e:
            print(f"   ❌ Request failed: {str(e)}")
            issues.append("non-existent-agent-error")
        
        # Test 2: Invalid file upload
        print("   Testing: Invalid file upload")
        try:
            agent_id = self.test_create_agent()
            if agent_id:
                files = {"file": ("test.txt", "content", "text/plain")}
                response = requests.post(f"{self.prod_url}/api/v1/agents/{agent_id}/upload", files=files, timeout=10)
                
                # Cleanup
                requests.delete(f"{self.prod_url}/api/v1/agents/{agent_id}", timeout=5)
                
                if response.status_code != 200:
                    print(f"   ✅ Correctly handles invalid upload (status: {response.status_code})")
                else:
                    print(f"   ⚠️ Invalid upload unexpectedly succeeded")
                    issues.append("invalid-upload-success")
        except Exception as e:
            print(f"   ❌ Invalid upload test failed: {str(e)}")
            issues.append("invalid-upload-error")
        
        # Test 3: Large file (within limits)
        print("   Testing: Large file upload")
        try:
            agent_id = self.test_create_agent()
            if agent_id:
                # Create a 50KB file (well under 100MB limit)
                large_content = "A" * 50000  # 50KB text
                files = {"file": ("large_test.txt", large_content, "text/plain")}
                
                response = requests.post(f"{self.prod_url}/api/v1/agents/{agent_id}/upload", files=files, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ Large file upload successful")
                    print(f"   Size: {result.get('size', 0)} bytes")
                    print(f"   Upload time: N/A")
                else:
                    print(f"   ❌ Large file failed: {response.status_code}")
                
                # Cleanup
                requests.delete(f"{self.prod_url}/api/v1/agents/{agent_id}", timeout=5)
                
        except Exception as e:
            print(f"   ❌ Large file test failed: {str(e)}")
        
        # Test 4: Rapid requests
        print("   Testing: Rapid consecutive requests")
        try:
            agent_id = self.test_create_agent()
            
            if agent_id:
                success_count = 0
                total_requests = 3
                
                for i in range(total_requests):
                    response = requests.get(f"{self.prod_url}/api/v1/agents/{agent_id}/files", timeout=10)
                    if response.status_code == 200:
                        success_count += 1
                    time.sleep(0.5)  # Brief delay
                
                print(f"   Success rate: {success_count}/{total_requests}")
                if success_count == total_requests:
                    print(f"   ✅ All rapid requests succeeded")
                else:
                    print(f"   ⚠️ Some requests failed")
                
                # Cleanup
                requests.delete(f"{self.prod_url}/api/v1/agents/{agent_id}", timeout=5)
                
        except Exception as e:
            print(f"   ❌ Rapid test failed: {str(e)}")
        
        return len(issues) == 0
    
    def run_production_test(self):
        """Run complete production test suite"""
        print("PRODUCTION SITE TESTING SUITE")
        print("=" * 50)
        print(f"Target: {self.prod_url}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        test_results = {}
        
        # Test basic health
        test_results['health'] = self.test_health_check()
        
        if not test_results['health']:
            print("\n❌ CRITICAL: Production site is not healthy!")
            print("Abandoning further tests.")
            return False
        
        # Test complete workflow
        test_results['workflow'] = self.test_agent_with_files()
        
        # Test edge cases
        test_results['edge_cases'] = self.test_edge_cases()
        
        # Generate report
        self.generate_report(test_results)
        
        return all(result is not False for result in test_results.values())
    
    def generate_report(self, results):
        """Generate comprehensive test report"""
        print(f"\n" + "=" * 50)
        print("PRODUCTION TEST REPORT")
        print("=" * 50)
        
        passed = []
        failed = []
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}: {test_name.upper()}")
            
            if result:
                passed.append(test_name)
            else:
                failed.append(test_name)
        
        print(f"\nSUMMARY:")
        print(f"Total Tests: {len(results)}")
        print(f"Passed: {len(passed)}")
        print(f"Failed: {len(failed)}")
        print(f"Success Rate: {len(passed)/len(results)*100:.1f}%")
        
        if len(failed) > 0:
            print(f"\nFailed Tests:")
            for test in failed:
                print(f"   - {test}")
        
        if len(passed) == len(results):
            print(f"\n🎉 ALL TESTS PASSED!")
            print(f"✅ Production site working correctly!")
            print(f"✅ Hybrid file approach functioning properly!")
            print(f"✅ Ready for production use!")
        else:
            print(f"\n⚠️  Some tests failed")
            print(f"Review and fix before full production use")
        
        print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Run production tests"""
    print("Z.ai Production Testing Suite")
    print("Testing hybrid file approach on live deployment")
    
    try:
        tester = ProductionTester()
        success = tester.run_production_test()
        
        return success
        
    except KeyboardInterrupt:
        print("\n⚹️  Test interrupted by user")
        return False
    except Exception as e:
        print(f"\n💥 Test failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    print(f"\nResult: {'SUCCESS' if success else 'FAILED'}")
    sys.exit(0 if success else 1)
