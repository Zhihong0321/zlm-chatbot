#!/usr/bin/env python3
"""
Integration Test for File-Enabled Agent Management System
Tests the complete frontend-backend integration with Z.ai file uploads
"""

import os
import sys
import json
import requests
from pathlib import Path

# Add backend path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class KnowledgeAgentTester:
    """Test suite for the integrated agent management system"""
    
    def __init__(self):
        self.api_key = os.getenv("ZAI_API_KEY")
        self.backend_url = "http://localhost:8000"  # Assuming local backend
        self.test_agent_id = None
        self.test_file_id = None
    
    def test_health_check(self):
        """Test if the backend is running"""
        try:
            response = requests.get(f"{self.backend_url}/api/v1/ui/health", timeout=5)
            if response.status_code == 200:
                print("✓ Backend health check passed")
                return True
            else:
                print(f"✗ Backend health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Backend connection failed: {str(e)}")
            return False
    
    def test_agent_crud(self):
        """Test agent creation, retrieval, and management"""
        print("\n=== Testing Agent CRUD ===")
        
        # Test agent creation
        agent_data = {
            "name": "Knowledge Test Agent",
            "description": "Agent for testing file upload capabilities",
            "model": "glm-4.6",
            "system_prompt": "You are a helpful assistant with access to uploaded knowledge files. Use the uploaded files to answer questions accurately.",
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                f"{self.backend_url}/api/v1/agents/",
                json=agent_data,
                timeout=10
            )
            
            if response.status_code == 200:
                agent = response.json()
                self.test_agent_id = agent["id"]
                print(f"✓ Agent created successfully: {agent['name']} (ID: {agent['id']})")
                
                # Test agent retrieval with files
                response = requests.get(
                    f"{self.backend_url}/api/v1/agents/{self.test_agent_id}/with-files",
                    timeout=10
                )
                
                if response.status_code == 200:
                    agent_with_files = response.json()
                    print(f"✓ Agent with files retrieved: {len(agent_with_files.get('knowledge_files', []))} files")
                    return True
                else:
                    print(f"✗ Failed to retrieve agent with files: {response.status_code}")
                    return False
            else:
                print(f"✗ Failed to create agent: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"✗ Agent CRUD test failed: {str(e)}")
            return False
    
    def test_file_upload(self):
        """Test file upload to Z.ai API via backend"""
        print("\n=== Testing File Upload ===")
        
        if not self.test_agent_id:
            print("✗ No test agent available")
            return False
        
        # Create test knowledge file
        test_content = """AI Knowledge Base Test File

This is a test document for the knowledge agent system.

Topics:
1. Machine Learning - Teaching computers to learn from data
2. Natural Language Processing - Understanding human language
3. Computer Vision - Teaching computers to see and understand images
4. Robotics - Building intelligent machines that interact with the physical world

Key Facts:
- Machine Learning uses algorithms to find patterns in data
- NLP enables chatbots and translation services
- Computer Vision powers facial recognition and self-driving cars
- AI is transforming healthcare, finance, and transportation

This file should be uploaded and stored in Z.ai's file system.
The agent should be able to reference this content when answering questions.
"""
        
        temp_file_path = "test_knowledge.txt"
        try:
            # Write test file
            with open(temp_file_path, "w", encoding="utf-8") as f:
                f.write(test_content)
            
            # Upload via backend API
            with open(temp_file_path, "rb") as f:
                files = {"file": ("test_knowledge.txt", f, "text/plain")}
                data = {"purpose": "agent"}
                
                response = requests.post(
                    f"{self.backend_url}/api/v1/agents/{self.test_agent_id}/upload",
                    files=files,
                    data=data,
                    timeout=30
                )
            
            if response.status_code == 200:
                upload_result = response.json()
                self.test_file_id = upload_result.get("file_id")
                print(f"✓ File uploaded successfully: {upload_result['filename']} ({upload_result['size']} bytes)")
                print(f"   Z.ai File ID: {self.test_file_id}")
                return True
            else:
                print(f"✗ File upload failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"✗ File upload test failed: {str(e)}")
            return False
        finally:
            # Clean up temp file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    
    def test_file_retrieval(self):
        """Test retrieving uploaded files for an agent"""
        print("\n=== Testing File Retrieval ===")
        
        if not self.test_agent_id:
            print("✗ No test agent available")
            return False
        
        try:
            response = requests.get(
                f"{self.backend_url}/api/v1/agents/{self.test_agent_id}/files",
                timeout=10
            )
            
            if response.status_code == 200:
                files = response.json()
                print(f"✓ Retrieved {len(files)} files for agent")
                
                for file in files:
                    print(f"   - {file['original_filename']} ({file['file_size']} bytes)")
                
                if len(files) > 0:
                    return True
                else:
                    print("✗ No files found for agent")
                    return False
            else:
                print(f"✗ Failed to retrieve files: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ File retrieval test failed: {str(e)}")
            return False
    
    def test_file_deletion(self):
        """Test deleting uploaded files"""
        print("\n=== Testing File Deletion ===")
        
        if not self.test_agent_id:
            print("✗ No test agent available")
            return False
        
        try:
            # Get files list first
            response = requests.get(
                f"{self.backend_url}/api/v1/agents/{self.test_agent_id}/files",
                timeout=10
            )
            
            if response.status_code == 200:
                files = response.json()
                
                if len(files) > 0:
                    file_to_delete = files[0]
                    file_id = file_to_delete["id"]
                    
                    # Delete the file
                    response = requests.delete(
                        f"{self.backend_url}/api/v1/agents/{self.test_agent_id}/files/{file_id}",
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        print(f"✓ File deleted successfully: {file_to_delete['original_filename']}")
                        return True
                    else:
                        print(f"✗ File deletion failed: {response.status_code}")
                        return False
                else:
                    print("✗ No files to delete")
                    return False
            else:
                print(f"✗ Failed to get files for deletion: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ File deletion test failed: {str(e)}")
            return False
    
    def test_agent_deletion(self):
        """Test cleaning up test agent"""
        print("\n=== Testing Agent Cleanup ===")
        
        if not self.test_agent_id:
            print("✗ No test agent to clean up")
            return False
        
        try:
            response = requests.delete(
                f"{self.backend_url}/api/v1/agents/{self.test_agent_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                print("✓ Test agent cleaned up successfully")
                return True
            else:
                print(f"✗ Agent cleanup failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ Agent cleanup failed: {str(e)}")
            return False
    
    def test_zai_direct_upload(self):
        """Test direct upload to Z.ai API (independent test)"""
        print("\n=== Testing Direct Z.ai Upload ===")
        
        if not self.api_key:
            print("✗ ZAI_API_KEY not found in environment")
            return False
        
        test_content = "Direct upload test for Z.ai API integration."
        
        try:
            import requests
            
            url = "https://api.z.ai/api/paas/v4/files"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json"
            }
            
            files = {
                'file': ('direct_test.txt', test_content, 'text/plain'),
                'purpose': (None, 'agent')
            }
            
            response = requests.post(url, headers=headers, files=files)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ Direct upload successful: {result['filename']}")
                print(f"   File ID: {result['id']}")
                return True
            else:
                print(f"✗ Direct upload failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"✗ Direct upload test failed: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run the complete test suite"""
        print("🧪 Starting Knowledge Agent Integration Tests")
        print("=" * 60)
        
        tests = [
            ("Backend Health", self.test_health_check),
            ("Agent CRUD Operations", self.test_agent_crud),
            ("File Upload", self.test_file_upload),
            ("File Retrieval", self.test_file_retrieval),
            ("File Deletion", self.test_file_deletion),
            ("Agent Cleanup", self.test_agent_deletion),
        ]
        
        # Add direct Z.ai test if API key is available
        if self.api_key:
            tests.insert(-1, ("Direct Z.ai Upload", self.test_zai_direct_upload))
        
        results = []
        
        for test_name, test_func in tests:
            print(f"\n🔍 Running: {test_name}")
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"✗ {test_name} crashed: {str(e)}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Test Results Summary")
        print("=" * 60)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}: {test_name}")
            if result:
                passed += 1
        
        print(f"\nScore: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! The knowledge agent system is working correctly.")
        elif passed >= total * 0.7:
            print("⚠️  Most tests passed. The system is mostly functional.")
        else:
            print("🚨 Many tests failed. The system needs attention.")
        
        return passed == total

def main():
    """Run the integration tests"""
    
    print("🤖 Knowledge Agent System Integration Test")
    print("\nThis test validates:")
    print("  • Backend API connectivity")
    print("  • Agent CRUD operations")
    print("  • File upload to Z.ai")
    print("  • Agent-file associations")
    print("  • File deletion and cleanup")
    
    print("\n⚠️  Prerequisites:")
    print("  • Backend server running on http://localhost:8000")
    print("  • ZAI_API_KEY environment variable set")
    print("  • Internet connection for Z.ai API")
    
    # Check if backend is running
    try:
        response = requests.get("http://localhost:8000/api/v1/ui/health", timeout=5)
        if response.status_code != 200:
            print(f"\n❌ Backend is not running or unhealthy: {response.status_code}")
            print("Please start the backend server:")
            print("  cd backend && python -m app.main")
            return False
    except Exception as e:
        print(f"\n❌ Cannot connect to backend server: {str(e)}")
        print("Please start the backend server:")
        print("  cd backend && python -m app.main")
        return False
    
    # Run the tests
    tester = KnowledgeAgentTester()
    success = tester.run_all_tests()
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        sys.exit(1)
