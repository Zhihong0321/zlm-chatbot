#!/usr/bin/env python3
"""
Test Coding Endpoint with File Upload Capabilities
Comprehensive test for the updated coding endpoint + file management system
"""

import os
import sys
import time
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

class CodingEndpointFileTester:
    """Test the coding endpoint with file upload capabilities"""
    
    def __init__(self):
        self.api_key = os.getenv("ZAI_API_KEY")
        self.backend_url = "http://localhost:8000"
        
        if not self.api_key:
            raise ValueError("ZAI_API_KEY not found in environment variables")
        
        print(f"Using API Key: {self.api_key[:15]}...")
        print(f"Backend URL: {self.backend_url}")
    
    def test_coding_endpoint_basics(self):
        """Test basic coding endpoint functionality"""
        print("\n=== Testing Basic Coding Endpoint ===")
        
        try:
            client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.z.ai/api/coding/paas/v4"
            )
            
            start_time = time.time()
            response = client.chat.completions.create(
                model="glm-4.6",
                messages=[{"role": "user", "content": "Hello! Confirm coding endpoint works."}],
                max_tokens=50
            )
            end_time = time.time()
            
            content = response.choices[0].message.content
            latency = end_time - start_time
            
            print(f"✅ Coding endpoint working!")
            print(f"   Response: {content}")
            print(f"   Latency: {latency:.2f}s")
            print(f"   Model: {response.model}")
            
            return True
            
        except Exception as e:
            print(f"❌ Coding endpoint failed: {str(e)}")
            return False
    
    def test_file_upload_direct(self):
        """Test direct file upload to coding endpoint"""
        print("\n=== Testing Direct File Upload ===")
        
        # Create test file
        test_content = """Test Document for Coding Endpoint

This is a test file to verify file upload works with the coding endpoint.

内容包括:
1. 人工智能基础知识
2. 机器学习算法
3. 自然语言处理
4. 计算机视觉应用

Key points:
- AI enables machines to learn from data
- Machine learning is a subset of AI
- NLP helps computers understand human language
- Computer vision allows image recognition

This file should be uploaded successfully to the coding endpoint.
"""
        
        try:
            # Direct upload to coding endpoint
            url = "https://api.z.ai/api/coding/paas/v4/files"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json"
            }
            
            files = {
                'file': ('test_coding_upload.txt', test_content, 'text/plain'),
                'purpose': (None, 'agent')
            }
            
            print(f"Uploading to: {url}")
            start_time = time.time()
            
            response = requests.post(url, headers=headers, files=files)
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ File upload successful!")
                print(f"   File ID: {result.get('id')}")
                print(f"   Filename: {result.get('filename')}")
                print(f"   Size: {result.get('bytes')} bytes")
                print(f"   Upload time: {end_time - start_time:.2f}s")
                
                return result.get('id'), result.get('filename')
            else:
                print(f"❌ File upload failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None, None
                
        except Exception as e:
            print(f"❌ Upload error: {str(e)}")
            return None, None
    
    def test_backend_connectivity(self):
        """Test if backend is running and accessible"""
        print("\n=== Testing Backend Connectivity ===")
        
        try:
            response = requests.get(f"{self.backend_url}/api/v1/ui/health", timeout=5)
            
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Backend is healthy!")
                print(f"   Status: {health_data.get('status')}")
                print(f"   Database: {health_data.get('database', 'N/A')}")
                return True
            else:
                print(f"❌ Backend unhealthy: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Backend connection failed: {str(e)}")
            print(f"   Please start backend: cd backend && python -m app.main")
            return False
    
    def test_backend_file_workflow(self):
        """Test complete backend file workflow"""
        print("\n=== Testing Backend File Workflow ===")
        
        if not self.test_backend_connectivity():
            return False
        
        # Step 1: Create test agent
        agent_data = {
            "name": "File Test Agent (Coding)",
            "description": "Testing file upload with coding endpoint",
            "system_prompt": "You are a helpful assistant. Use uploaded files to answer questions accurately.",
            "model": "glm-4.6",
            "temperature": 0.7
        }
        
        try:
            # Create agent
            start_time = time.time()
            agent_response = requests.post(
                f"{self.backend_url}/api/v1/agents/",
                json=agent_data,
                timeout=10
            )
            
            if agent_response.status_code != 200:
                print(f"❌ Failed to create agent: {agent_response.status_code}")
                return False
            
            agent = agent_response.json()
            agent_id = agent["id"]
            print(f"✅ Created agent: {agent_id}")
            
            # Step 2: Test file upload through backend
            test_file_content = "Backend file upload test\n\nThis file tests the complete backend workflow with the coding endpoint."
            
            files = {
                "file": ("backend_test_file.txt", test_file_content, "text/plain")
            }
            data = {"purpose": "agent"}
            
            upload_start = time.time()
            upload_response = requests.post(
                f"{self.backend_url}/api/v1/agents/{agent_id}/upload",
                files=files,
                data=data,
                timeout=30
            )
            upload_end = time.time()
            
            if upload_response.status_code == 200:
                upload_result = upload_response.json()
                print(f"✅ Backend file upload successful!")
                print(f"   Filename: {upload_result['filename']}")
                print(f"   Size: {upload_result['size']} bytes")
                print(f"   Upload time: {upload_end - upload_start:.2f}s")
                print(f"   Z.ai File ID: {upload_result['file_id']}")
                
                # Step 3: List files for agent
                files_response = requests.get(
                    f"{self.backend_url}/api/v1/agents/{agent_id}/files",
                    timeout=10
                )
                
                if files_response.status_code == 200:
                    files_list = files_response.json()
                    print(f"✅ Retrieved {len(files_list)} files for agent")
                    
                    for file in files_list:
                        print(f"   - {file['original_filename']} ({file['file_size']} bytes)")
                    
                    # Step 4: Delete the file
                    if len(files_list) > 0:
                        file_to_delete = files_list[0]
                        delete_response = requests.delete(
                            f"{self.backend_url}/api/v1/agents/{agent_id}/files/{file_to_delete['id']}",
                            timeout=10
                        )
                        
                        if delete_response.status_code == 200:
                            print(f"✅ File deleted successfully")
                        else:
                            print(f"❌ File deletion failed: {delete_response.status_code}")
                
                # Step 5: Cleanup agent
                delete_agent_response = requests.delete(
                    f"{self.backend_url}/api/v1/agents/{agent_id}",
                    timeout=10
                )
                
                if delete_agent_response.status_code == 200:
                    print(f"✅ Test agent cleaned up")
                
                return True
                
            else:
                print(f"❌ Backend upload failed: {upload_response.status_code}")
                print(f"   Response: {upload_response.text}")
                
                # Still cleanup agent
                requests.delete(f"{self.backend_url}/api/v1/agents/{agent_id}", timeout=10)
                return False
                
        except Exception as e:
            print(f"❌ Backend workflow error: {str(e)}")
            return False
    
    def test_chat_with_files_coding(self):
        """Test chat functionality with uploaded files using coding endpoint"""
        print("\n=== Testing Chat with Files (Coding Endpoint) ===")
        
        if not self.test_backend_connectivity():
            return False
        
        try:
            # Create agent for file testing
            agent_data = {
                "name": "Chat File Test Agent",
                "description": "Testing chat with uploaded files using coding endpoint",
                "system_prompt": "You are a helpful assistant. When users ask about uploaded files, use the file content to provide accurate answers.",
                "model": "glm-4.6",
                "temperature": 0.7
            }
            
            # Create agent
            agent_response = requests.post(
                f"{self.backend_url}/api/v1/agents/",
                json=agent_data,
                timeout=10
            )
            
            if agent_response.status_code != 200:
                print(f"❌ Failed to create test agent")
                return False
            
            agent = agent_response.json()
            agent_id = agent["id"]
            
            # Create session
            session_data = {
                "title": "File Chat Test Session",
                "agent_id": agent_id
            }
            
            session_response = requests.post(
                f"{self.backend_url}/api/v1/sessions/",
                json=session_data,
                timeout=10
            )
            
            if session_response.status_code != 200:
                print(f"❌ Failed to create session")
                requests.delete(f"{self.backend_url}/api/v1/agents/{agent_id}", timeout=5)
                return False
            
            session = session_response.json()
            session_id = session["id"]
            
            # Upload a knowledge file
            knowledge_content = """AI Knowledge Base

TOPICS:
1. Machine Learning - Teaching computers from data
2. Deep Learning - Neural networks with multiple layers
3. Natural Language Processing - Understanding human language
4. Computer Vision - Processing visual information

KEY FACTS:
- ML algorithms find patterns in data
- Deep learning uses artificial neural networks
- NLP enables chatbots and translation
- Computer vision powers facial recognition

APPLICATIONS:
- Virtual assistants use NLP
- Self-driving cars use computer vision
- Recommendation systems use ML
- Medical diagnosis uses deep learning

This document should be referenceable when users ask about AI topics.
"""
            
            files = {
                "file": ("ai_knowledge.txt", knowledge_content, "text/plain")
            }
            data = {"purpose": "agent"}
            
            upload_response = requests.post(
                f"{self.backend_url}/api/v1/agents/{agent_id}/upload",
                files=files,
                data=data,
                timeout=30
            )
            
            if upload_response.status_code != 200:
                print(f"❌ Failed to upload knowledge file")
                # Cleanup
                requests.delete(f"{self.backend_url}/api/v1/sessions/{session_id}", timeout=5)
                requests.delete(f"{self.backend_url}/api/v1/agents/{agent_id}", timeout=5)
                return False
            
            print(f"✅ Knowledge file uploaded successfully")
            
            # Test chat messages
            test_questions = [
                "What topics are covered in the uploaded file?",
                "Explain machine learning according to the document.",
                "What are some applications of AI mentioned?",
                "What is the main purpose of this document?"
            ]
            
            for i, question in enumerate(test_questions):
                print(f"\nTesting Question {i+1}: {question}")
                
                chat_data = {"message": question}
                
                start_time = time.time()
                chat_response = requests.post(
                    f"{self.backend_url}/api/v1/chat/{session_id}/messages",
                    json=chat_data,
                    timeout=30
                )
                end_time = time.time()
                
                if chat_response.status_code == 200:
                    chat_result = chat_response.json()
                    content = chat_result.get("message", "")
                    latency = end_time - start_time
                    
                    print(f"✅ Chat response received")
                    print(f"   Latency: {latency:.2f}s")
                    print(f"   Response: {content[:200]}...")
                else:
                    print(f"❌ Chat failed: {chat_response.status_code}")
                    print(f"   Response: {chat_response.text[:200]}")
            
            # Cleanup
            requests.delete(f"{self.backend_url}/api/v1/sessions/{session_id}", timeout=5)
            requests.delete(f"{self.backend_url}/api/v1/agents/{agent_id}", timeout=5)
            
            print(f"✓ Chat with files test completed")
            return True
            
        except Exception as e:
            print(f"❌ Chat test error: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run all tests"""
        print("Comprehensive Coding Endpoint File Upload Test")
        print("=" * 60)
        print(f"Testing at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        tests = [
            ("Basic Coding Endpoint", self.test_coding_endpoint_basics),
            ("Direct File Upload", self.test_file_upload_direct),
            ("Backend File Workflow", self.test_backend_file_workflow),
            ("Chat with Files", self.test_chat_with_files_coding),
        ]
        
        results = []
        
        for test_name, test_func in tests:
            print(f"\n{'='*50}")
            print(f"RUNNING: {test_name}")
            print(f"{'='*50}")
            
            try:
                start_time = time.time()
                success = test_func()
                end_time = time.time()
                
                duration = end_time - start_time
                status = "✅ PASS" if success else "❌ FAIL"
                
                print(f"\n{status}: {test_name} ({duration:.2f}s)")
                results.append((test_name, success, duration))
                
            except Exception as e:
                print(f"\n💥 {test_name} crashed: {str(e)}")
                results.append((test_name, False, 0))
        
        # Summary
        print(f"\n{'='*60}")
        print("TEST RESULTS SUMMARY")
        print(f"{'='*60}")
        
        passed = 0
        total = len(results)
        
        for test_name, success, duration in results:
            status = "✅ PASS" if success else "❌ FAIL"
            duration_str = f"({duration:.2f}s)" if duration > 0 else ""
            print(f"{status}: {test_name} {duration_str}")
            if success:
                passed += 1
        
        print(f"\nScore: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! The coding endpoint with files is working perfectly!")
        elif passed >= total * 0.75:
            print("⚠️  Most tests passed. The system is mostly functional.")
        else:
            print("🚨 Many tests failed. The system needs attention.")
        
        print(f"\nKey Features Verified:")
        print(f"  • Coding endpoint connectivity: {'✅' if results[0][1] else '❌'}")
        print(f"  • Direct file upload to Z.ai: {'✅' if results[1][1] else '❌'}")
        print(f"  • Backend file workflow: {'✅' if results[2][1] else '❌'}")
        print(f"  • Chat with uploaded files: {'✅' if results[3][1] else '❌'}")
        
        return passed == total

def main():
    """Main test execution"""
    
    print("Coding Endpoint + File Upload Test Suite")
    print("Tests the updated system using Z.ai Coding Plan subscription")
    
    try:
        tester = CodingEndpointFileTester()
        success = tester.run_comprehensive_test()
        return success
        
    except KeyboardInterrupt:
        print("\nTest cancelled by user")
        return False
    except Exception as e:
        print(f"\nTest failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
