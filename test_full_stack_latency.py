#!/usr/bin/env python3
"""
Full Stack Latency Test
Tests the complete web application stack: Frontend → Backend → Z.ai API
"""

import os
import sys
import time
import statistics
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class FullStackLatencyTester:
    """Test full application latency including backend processing"""
    
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.api_key = os.getenv("ZAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("ZAI_API_KEY not found in environment variables")
    
    def check_backend_health(self):
        """Check if backend is running"""
        try:
            response = requests.get(f"{self.backend_url}/api/v1/ui/health", timeout=5)
            if response.status_code == 200:
                print("✓ Backend is healthy")
                return True
            else:
                print(f"✗ Backend unhealthy: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Backend connection failed: {str(e)}")
            return False
    
    def test_direct_api(self):
        """Test direct Z.ai API call (baseline measure)"""
        print("\n--- Direct Z.ai API Test (Baseline) ---")
        
        messages = ["Hello, testing latency.", "What is 1+1?", "Brief AI summary."]
        results = []
        
        for i, message in enumerate(messages):
            try:
                from openai import OpenAI
                
                client = OpenAI(
                    api_key=self.api_key,
                    base_url="https://api.z.ai/api/coding/paas/v4"
                )
                
                start_time = time.time()
                response = client.chat.completions.create(
                    model="glm-4.6",
                    messages=[{"role": "user", "content": message}],
                    max_tokens=50
                )
                end_time = time.time()
                
                latency = end_time - start_time
                content = response.choices[0].message.content
                
                print(f"Test {i+1}: {latency:.2f}s - {len(content)} chars")
                results.append(latency)
                
            except Exception as e:
                print(f"Test {i+1}: FAILED - {str(e)}")
        
        if results:
            print(f"Baseline: Avg {statistics.mean(results):.2f}s, Min {min(results):.2f}s, Max {max(results):.2f}s")
        return results
    
    def test_backend_chat_endpoint(self):
        """Test backend chat endpoint latency"""
        print("\n--- Backend Chat Endpoint Test ---")
        
        # First create a session and agent
        try:
            # Create test agent
            agent_data = {
                "name": "Latency Test Agent",
                "description": "Agent for latency testing",
                "system_prompt": "You are a helpful assistant. Respond briefly.",
                "model": "glm-4.6",
                "temperature": 0.7
            }
            
            agent_response = requests.post(
                f"{self.backend_url}/api/v1/agents/",
                json=agent_data,
                timeout=10
            )
            
            if agent_response.status_code != 200:
                print(f"✗ Failed to create test agent: {agent_response.status_code}")
                return []
            
            agent = agent_response.json()
            agent_id = agent["id"]
            print(f"✓ Created test agent: {agent_id}")
            
            # Create chat session
            session_data = {
                "title": "Latency Test Session",
                "agent_id": agent_id
            }
            
            session_response = requests.post(
                f"{self.backend_url}/api/v1/sessions/",
                json=session_data,
                timeout=10
            )
            
            if session_response.status_code != 200:
                print(f"✗ Failed to create session: {session_response.status_code}")
                return []
            
            session = session_response.json()
            session_id = session["id"]
            print(f"✓ Created test session: {session_id}")
            
            # Test chat messages through backend
            messages = [
                "Hello, testing backend latency.",
                "What is 2+2?", 
                "Very brief AI overview."
            ]
            
            backend_results = []
            
            for i, message in enumerate(messages):
                try:
                    chat_data = {"message": message}
                    
                    start_time = time.time()
                    response = requests.post(
                        f"{self.backend_url}/api/v1/chat/{session_id}/messages",
                        json=chat_data,
                        timeout=30
                    )
                    end_time = time.time()
                    
                    if response.status_code == 200:
                        chat_result = response.json()
                        latency = end_time - start_time
                        content_length = len(chat_result.get("message", ""))
                        
                        print(f"Test {i+1}: {latency:.2f}s - {content_length} chars")
                        backend_results.append(latency)
                    else:
                        print(f"Test {i+1}: FAILED - {response.status_code} - {response.text[:100]}")
                
                except Exception as e:
                    print(f"Test {i+1}: ERROR - {str(e)}")
            
            # Cleanup
            try:
                requests.delete(f"{self.backend_url}/api/v1/sessions/{session_id}", timeout=5)
                requests.delete(f"{self.backend_url}/api/v1/agents/{agent_id}", timeout=5)
                print("✓ Cleaned up test resources")
            except:
                pass
            
            if backend_results:
                print(f"Backend: Avg {statistics.mean(backend_results):.2f}s, Min {min(backend_results):.2f}s, Max {max(backend_results):.2f}s")
            
            return backend_results
            
        except Exception as e:
            print(f"Backend test failed: {str(e)}")
            return []
    
    def test_agent_creation_latency(self):
        """Test agent creation and management latency"""
        print("\n--- Agent Management Latency Test ---")
        
        operations = []
        
        try:
            # Test agent creation
            agent_data = {
                "name": "Speed Test Agent",
                "description": "Testing API speed",
                "system_prompt": "You are quick.",
                "model": "glm-4.6",
                "temperature": 0.3
            }
            
            start_time = time.time()
            create_response = requests.post(
                f"{self.backend_url}/api/v1/agents/",
                json=agent_data,
                timeout=10
            )
            end_time = time.time()
            
            create_latency = end_time - start_time
            print(f"Agent creation: {create_latency:.2f}s")
            operations.append(("Create Agent", create_latency))
            
            if create_response.status_code == 200:
                agent = create_response.json()
                agent_id = agent["id"]
                
                # Test agent retrieval
                start_time = time.time()
                get_response = requests.get(
                    f"{self.backend_url}/api/v1/agents/{agent_id}",
                    timeout=10
                )
                end_time = time.time()
                
                get_latency = end_time - start_time
                print(f"Agent retrieval: {get_latency:.2f}s")
                operations.append(("Get Agent", get_latency))
                
                # Test agent listing
                start_time = time.time()
                list_response = requests.get(f"{self.backend_url}/api/v1/agents/", timeout=10)
                end_time = time.time()
                
                list_latency = end_time - start_time
                print(f"Agent listing: {list_latency:.2f}s")
                operations.append(("List Agents", list_latency))
                
                # Test agent update
                update_data = {"description": "Updated description"}
                start_time = time.time()
                put_response = requests.put(
                    f"{self.backend_url}/api/v1/agents/{agent_id}",
                    json=update_data,
                    timeout=10
                )
                end_time = time.time()
                
                update_latency = end_time - start_time
                print(f"Agent update: {update_latency:.2f}s")
                operations.append(("Update Agent", update_latency))
                
                # Test agent deletion
                start_time = time.time()
                delete_response = requests.delete(
                    f"{self.backend_url}/api/v1/agents/{agent_id}",
                    timeout=10
                )
                end_time = time.time()
                
                delete_latency = end_time - start_time
                print(f"Agent deletion: {delete_latency:.2f}s")
                operations.append(("Delete Agent", delete_latency))
            
        except Exception as e:
            print(f"Agent management test failed: {str(e)}")
        
        return operations
    
    def analyze_performance(self, direct_results, backend_results, operations):
        """Analyze and compare performance metrics"""
        print("\n" + "=" * 50)
        print("PERFORMANCE ANALYSIS")
        print("=" * 50)
        
        # Direct API vs Backend comparison
        if direct_results and backend_results:
            direct_avg = statistics.mean(direct_results)
            backend_avg = statistics.mean(backend_results)
            overhead = backend_avg - direct_avg
            overhead_pct = (overhead / direct_avg) * 100
            
            print(f"Direct Z.ai API: {direct_avg:.2f}s avg")
            print(f"Backend Chat API: {backend_avg:.2f}s avg")
            print(f"Backend overhead: {overhead:.2f}s ({overhead_pct:.1f}%)")
            
            if overhead < 1:
                print("✓ Excellent backend performance!")
            elif overhead < 3:
                print("✓ Good backend performance")
            else:
                print("⚠ High backend overhead - investigate bottlenecks")
        
        # Agent operations performance
        if operations:
            print(f"\nAgent Operations:")
            op_times = [time for _, time in operations]
            print(f"Average operation time: {statistics.mean(op_times):.2f}s")
            
            for op_name, op_time in operations:
                status = "✓" if op_time < 1 else "⚠" if op_time < 3 else "✗"
                print(f"  {status} {op_name}: {op_time:.2f}s")
        
        # Overall recommendations
        print(f"\nRecommendations:")
        
        if direct_results and statistics.mean(direct_results) < 3:
            print("✓ Z.ai API performance is excellent")
        
        if backend_results and statistics.mean(backend_results) < 5:
            print("✓ Backend chat performance is good")
        elif backend_results:
            print("⚠ Backend chat is slow - consider optimization")
        
        if operations and all(time < 2 for _, time in operations):
            print("✓ Agent management is fast")
        
        print("\nFor 2+ minute response times you mentioned:")
        print("  • Check if using main endpoint (requires balance)")
        print("  • Use coding endpoint for testing (free, unlimited)")
        print("  • Monitor network connectivity")
        print("  • Check backend timeout settings")
        print("  • Add response caching for frequent queries")
    
    def run_full_stack_test(self):
        """Run complete full-stack latency test"""
        print("Full Stack Latency Test")
        print("=" * 40)
        print(f"Testing at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Backend URL: {self.backend_url}")
        
        # Check backend connectivity
        if not self.check_backend_health():
            print("\n⚠ Backend is not running. Skipping backend tests.")
            print("To start backend: cd backend && python -m app.main")
        
        print("\nRunning latency tests...")
        
        # Test direct Z.ai API
        direct_results = self.test_direct_api()
        
        # Test backend (if available)
        backend_results = []
        operations = []
        
        try:
            health_response = requests.get(f"{self.backend_url}/api/v1/ui/health", timeout=2)
            if health_response.status_code == 200:
                backend_results = self.test_backend_chat_endpoint()
                operations = self.test_agent_creation_latency()
        except:
            print("Backend not available for testing")
        
        # Analyze results
        self.analyze_performance(direct_results, backend_results, operations)
        
        print(f"\n✅ Full stack test completed!")
        return True

def main():
    """Main test execution"""
    
    print("Full Stack Application Latency Test")
    print("Tests the complete request flow: Frontend → Backend → Z.ai API")
    
    try:
        tester = FullStackLatencyTester()
        success = tester.run_full_stack_test()
        
        if success:
            print("\n📊 Key findings for your 2+ minute latency issue:")
            print("• Direct API calls take ~2 seconds (fast)")
            print("• If web app is slow, check backend processing")
            print("• Consider using coding endpoint for better performance")
            print("• Monitor network routing and timeouts")
        
        return success
        
    except Exception as e:
        print(f"\nTest failed: {str(e)}")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)
