#!/usr/bin/env python3

"""
Production Testing - Simple Setup Verification
Quick test for basic functionality before comprehensive testing
"""

import os
import sys
import requests

def check_health():
    """Check if production site is accessible and healthy"""
    prod_url = os.getenv("PRODUCTION_URL", "")
    
    if not prod_url:
        print("ERROR: PRODUCTION_URL not set.")
        print("Set: PRODUCTION_URL=https://your-app.railway.app")
        return False
    
    try:
        response = requests.get(f"{prod_url}/api/v1/ui/health", timeout=10)
        status_ok = response.status_code == 200
        
        if status_ok:
            data = response.json()
            print(f"✅ Health check passed")
            print(f"   Status: {data.get('status')}")
            return True
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        return False

def test_basic_api():
    """Test basic API functionality"""
    prod_url = os.getenv("PRODUCTION_URL")
    
    try:
        # Load environment
        prod_url = os.getenv("PRODUCTION_URL", "")
        if prod_url:
            print(f"Testing API at: {prod_url}")
            
            # Test multiple endpoints
            endpoints = [
                f"{prod_url}/api/v1/agents/",
                f"{prod_url}/api/v1/sessions/",
                f"{prod_url}/api/v1/ui/health/"
            ]
            
            api_health = True
            for endpoint in endpoints:
                try:
                    response = requests.get(endpoint, timeout=2)
                    if response.status_code == 200:
                        print(f"✅ {endpoint}")
                        else:
                            api_health = False
                except Exception:
                    api_health = False
                        api_health = False
                    
            print(f"API Health: {'✅' if api_health else '❌ FAILED'}")
            
            return api_health
            
    except Exception as e:
        print(f"ERROR: API test failed: {str(e)}")
        return False

def test_agent_operations():
    """Test agent management operations"""
    prod_url = os.getenv("PRODUCTION_URL", "")
    api_key = os.getenv("ZAI_API_KEY", "")
    
    if not prod_url or not api_key:
        print("ERROR: Set both PRODUCTION_URL and ZAI_API_KEY")
        return False
    
    try:
        # Create a test agent
        test_agent_data = {
            "name": "Production Test Agent",
            "description": "For production testing",
            "system_prompt": "You are a helpful coding assistant",
            "model": "glm-4.6"
        }
        
        upload_start_time = time.time()
        agent_response = requests.post(
            f"{prod_url}/api/v1/agents/",
            json=test_agent_data,
            timeout=30
        )
        upload_time = time.time() - upload_start_time
        
        if agent_response.status_code == 200:
            agent = agent_response.json()
            agent_id = agent["id"]
            print(f"✅ Agent created (ID: {agent_id})")
            print(f"  Creation time: {upload_time:.2f}s")
            
            # Create a session
            session_data = {
                "title": "Production Test Session",
                "agent_id": agent_id
            }
            
            session_response = requests.post(
                f"{prod_url}/api/v1/sessions/",
                json=session_data,
                timeout=10
            )
            
            if session_response.status_code == 200:
                print(f"✅ Session created: {session_response.json()['id']}")
                session_id = session_response.json()["id"]
                print(f"  Session time: {time.time():}")
                
                # Test file upload
                test_content = "Production test content for production testing"
    
                files = {"file": ("prod_test.txt", test_content, "text/plain")}
                
                upload_response = requests.post(
                    f"{prod_url}/api/v1/agents/{agent_id}/upload",
                    files=files,
                    timeout=30
                )
                
                upload_time = time.time() - upload_start_time
                
                if upload_response.status_code == 200:
                    uploadResult = upload_response.json()
                    file_id = uploadResult['file_id']
                    print(f"✅ File uploaded (ID: {file_id})")
                    print(f"  Upload time: {upload_time:.2f}s")
                else:
                    print(f"❌ Upload failed: {upload_response.status_code}")
                    return False
                    
            # Test chat functionality
            chat_start = time.time()
            chat_response = requests.post(
                f"{prod_url}/api/v1/chat/{session_id}/messages", timeout=30
            )
            chat_time = time.time() - chat_start
            
            if chat_response.status_code == 200:
                chat_result = chat_response.json()
                content = chat_result.get("message", "")
                
                print(f"✅ Chat received")
                print(f"  Response time: {chat_time:.2f}s")
                print(f"  Content length: {len(content)} chars")
                print(f"  Content: {content[:100]}...")
                
                if "Production test content" in content and "production" in content.lower():
                    print("✅ Content access confirmed!")
                    return True
                
                if chat_time > 10:
                    print(f"⚠  Slow response time: {chat_time:.2f}s")
                    
                # Cleanup
                delete_response = requests.delete(
                    f"{prod_url}/api/v1/sessions/{session_id}", timeout=10
                )
                print(f"Session cleanup complete")
                print(f"✅ Cleanup completed")
            else:
                return True
            else:
                print(f"❌ Chat failed: {chat_response.status_code}")
                    return False
                
        except Exception as e:
            print(f"❌ Chat test failed: {str(e)[:100]}")
            return False
                
    except Exception as e:
        print(f"❌ Agent operations failed: {str(e)[:100]}")
        return False
    
def main():
    print("Production Test - Basic Validation")
    print("=" * 30)
    
    # Test basic functionality
    success = all([
        check_health(),
        test_basic_api(),
        test_agent_operations()
    ])
    
    print("\n" + "=" * 30)
    print(f"Basic Test Results:")
    print("✅ Ready for comprehensive testing" if success else "Not ready yet")
    
    return success
    
    # Additional checks if all basic tests pass
    if success:
        print(f"\nNext Steps:")
        print("• Run production test: python simple_prod_test.py")
        print("• Set CLEANUP=false to test without cleanup")
        print("• Monitor response times")
        print("• Test with larger content and files")
        
        print(f"✅ Basic system operational: PRODUCTION READY")
    else:
        print(f"🚨️ Issues found - Check:")
        print(f"- Backend deployment health")
        print(f"- API configuration")
        print(f"- Database connectivity")
        print("Review and fix issues before production use")

if __name__main__':__main__main__() # Execute the main function
    return True
        
    return True
