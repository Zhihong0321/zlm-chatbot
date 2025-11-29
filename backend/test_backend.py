# Backend Production Test

import requests
import json
import os

# Configuration
API_BASE = "http://localhost:8000/api/v1"

def test_health_check():
    """Test health check endpoint"""
    print("Testing health check...")
    try:
        response = requests.get(f"{API_BASE}/ui/health")
        print(f"Health check: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_agent_creation():
    """Test agent creation"""
    print("\nTesting agent creation...")
    agent_data = {
        "name": "Test Assistant",
        "description": "A test assistant for deployment validation",
        "system_prompt": "You are a helpful assistant that provides concise answers.",
        "model": "glm-4.5",
        "temperature": 0.7
    }
    
    try:
        response = requests.post(f"{API_BASE}/agents", json=agent_data)
        print(f"Agent creation: {response.status_code}")
        if response.status_code == 200:
            agent = response.json()
            print(f"Agent ID: {agent['id']}")
            return agent['id']
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Agent creation failed: {e}")
        return None

def test_session_creation(agent_id):
    """Test session creation"""
    print("\nTesting session creation...")
    session_data = {
        "title": "Deployment Test Session",
        "agent_id": agent_id
    }
    
    try:
        response = requests.post(f"{API_BASE}/sessions", json=session_data)
        print(f"Session creation: {response.status_code}")
        if response.status_code == 200:
            session = response.json()
            print(f"Session ID: {session['id']}")
            return session['id']
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Session creation failed: {e}")
        return None

def test_api_endpoints():
    """Test all API endpoints"""
    print("Running Backend API Tests\n")
    
    results = {}
    
    # Test health check
    results['health'] = test_health_check()
    
    # Test agent creation and management
    agent_id = test_agent_creation()
    results['agent_creation'] = agent_id is not None
    
    if agent_id:
        # Test getting agents
        try:
            response = requests.get(f"{API_BASE}/agents")
            results['agent_list'] = response.status_code == 200
            print(f"\nAgent list: {response.status_code}")
        except:
            results['agent_list'] = False
    
    # Test session creation
    if agent_id:
        session_id = test_session_creation(agent_id)
        results['session_creation'] = session_id is not None
        
        if session_id:
            # Test getting sessions
            try:
                response = requests.get(f"{API_BASE}/sessions")
                results['session_list'] = response.status_code == 200
                print(f"Session list: {response.status_code}")
            except:
                results['session_list'] = False
            
            # Test getting session history
            try:
                response = requests.get(f"{API_BASE}/sessions/{session_id}/history")
                results['session_history'] = response.status_code == 200
                print(f"Session history: {response.status_code}")
            except:
                results['session_history'] = False
    
    # Test API documentation
    try:
        response = requests.get(f"{API_BASE.replace('/api/v1', '')}/docs")
        results['api_docs'] = response.status_code == 200
        print(f"API docs: {response.status_code}")
    except:
        results['api_docs'] = False
    
    return results

def print_test_summary(results):
    """Print test summary"""
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name.replace('_', ' ').title():<25} {status}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("All tests passed! Backend is ready for deployment.")
    else:
        print("Some tests failed. Check output above for details.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    # Run API tests
    results = test_api_endpoints()
    
    # Print summary
    print_test_summary(results)
    
    # Exit with appropriate code
    exit(0 if all(results.values()) else 1)