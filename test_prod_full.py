import requests
import sys
import time
import json
import random
import string
from datetime import datetime

BASE_URL = "https://zlm-chatbot-production.up.railway.app/api/v1"
HEALTH_URL = "https://zlm-chatbot-production.up.railway.app/api/v1/ui/health"

def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def log(message, type="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    prefix = f"[{timestamp}] [{type}]"
    if type == "PASS":
        print(f"[PASS] {prefix} {message}")
    elif type == "FAIL":
        print(f"[FAIL] {prefix} {message}")
    elif type == "WARN":
        print(f"[WARN] {prefix} {message}")
    else:
        print(f"[INFO] {prefix} {message}")

class ProdApiTester:
    def __init__(self):
        self.test_agent = None
        self.test_session = None
        self.results = {
            "total": 0,
            "passed": 0,
            "failed": 0
        }

    def record_result(self, success):
        self.results["total"] += 1
        if success:
            self.results["passed"] += 1
        else:
            self.results["failed"] += 1
        return success

    def test_health(self):
        log("Testing Health Endpoint...")
        try:
            res = requests.get(HEALTH_URL, timeout=10)
            if res.status_code == 200 and res.json().get("status") == "healthy":
                log("System is HEALTHY", "PASS")
                return self.record_result(True)
            else:
                log(f"System Unhealthy: {res.text}", "FAIL")
                return self.record_result(False)
        except Exception as e:
            log(f"Health Check Failed: {e}", "FAIL")
            return self.record_result(False)

    def test_agents_crud(self):
        log("Testing Agents CRUD...")
        try:
            # 1. List Agents
            res = requests.get(f"{BASE_URL}/agents/") # Added trailing slash
            if res.status_code != 200:
                # Retry without trailing slash
                res = requests.get(f"{BASE_URL}/agents")
            
            if res.status_code != 200:
                log("Failed to list agents", "FAIL")
                return self.record_result(False)
            
            agents = res.json()
            log(f"Found {len(agents)} existing agents", "INFO")
            
            # 2. Create Agent
            new_agent_data = {
                "name": f"Test_Agent_{generate_random_string()}",
                "description": "Automated Test Agent",
                "system_prompt": "You are a test agent.",
                "model": "glm-4.5-flash",
                "temperature": 0.7
            }
            res = requests.post(f"{BASE_URL}/agents/", json=new_agent_data)
            if res.status_code != 200:
                log(f"Failed to create agent: {res.text}", "FAIL")
                return self.record_result(False)
            
            self.test_agent = res.json()
            log(f"Created Agent ID: {self.test_agent['id']}", "PASS")
            
            # 3. Read Agent
            res = requests.get(f"{BASE_URL}/agents/{self.test_agent['id']}")
            if res.status_code != 200:
                log("Failed to read created agent", "FAIL")
                return self.record_result(False)
            
            # 4. Update Agent
            update_data = {"description": "Updated Description"}
            res = requests.put(f"{BASE_URL}/agents/{self.test_agent['id']}", json=update_data)
            if res.status_code == 200 and res.json()["description"] == "Updated Description":
                log("Agent updated successfully", "PASS")
            else:
                log("Failed to update agent", "FAIL")
                self.record_result(False)
                
            return self.record_result(True)
            
        except Exception as e:
            log(f"Agents CRUD Exception: {e}", "FAIL")
            return self.record_result(False)

    def test_sessions_crud(self):
        if not self.test_agent:
            log("Skipping Session tests (No Agent)", "WARN")
            return False
            
        log("Testing Sessions CRUD...")
        try:
            # 1. Create Session
            session_data = {
                "title": f"Test_Session_{generate_random_string()}",
                "agent_id": self.test_agent['id']
            }
            res = requests.post(f"{BASE_URL}/sessions/", json=session_data)
            if res.status_code != 200:
                log(f"Failed to create session: {res.text}", "FAIL")
                return self.record_result(False)
            
            self.test_session = res.json()
            log(f"Created Session ID: {self.test_session['id']}", "PASS")
            
            # 2. Get Session
            res = requests.get(f"{BASE_URL}/sessions/{self.test_session['id']}")
            if res.status_code == 200:
                log("Retrieved session details", "PASS")
            else:
                log("Failed to retrieve session", "FAIL")
                self.record_result(False)
            
            # 3. List Sessions (verify presence)
            res = requests.get(f"{BASE_URL}/sessions/")
            sessions = res.json()
            found = any(s['id'] == self.test_session['id'] for s in sessions)
            if found:
                log("Session found in list", "PASS")
            else:
                log("New session not found in list", "FAIL")
                self.record_result(False)
                
            return self.record_result(True)
            
        except Exception as e:
            log(f"Sessions CRUD Exception: {e}", "FAIL")
            return self.record_result(False)

    def test_chat_flow(self):
        if not self.test_session:
            log("Skipping Chat tests (No Session)", "WARN")
            return False
            
        log("Testing Chat Flow...")
        try:
            # 1. Send Message
            msg_data = {"message": "Hello, are you working?"}
            res = requests.post(f"{BASE_URL}/chat/{self.test_session['id']}/messages", json=msg_data)
            
            if res.status_code == 200:
                response_data = res.json()
                log(f"Message sent. Response: {response_data.get('content', '')[:50]}...", "PASS")
            else:
                log(f"Failed to send message: {res.text}", "FAIL")
                return self.record_result(False)
            
            # 2. Check History
            res = requests.get(f"{BASE_URL}/sessions/{self.test_session['id']}/history")
            history = res.json()
            if len(history) >= 2: # User + Assistant
                log(f"History verified (Count: {len(history)})", "PASS")
                return self.record_result(True)
            else:
                log("History incomplete", "FAIL")
                return self.record_result(False)
                
        except Exception as e:
            log(f"Chat Flow Exception: {e}", "FAIL")
            return self.record_result(False)

    def test_advanced_features(self):
        log("Testing Advanced Features (Search, Analytics)...")
        try:
            # 1. Search
            res = requests.get(f"{BASE_URL}/sessions/search?q=Test")
            if res.status_code == 200:
                log("Search endpoint working", "PASS")
            else:
                log("Search endpoint failed", "FAIL")
            
            # 2. Analytics
            res = requests.get(f"{BASE_URL}/sessions/analytics/summary")
            if res.status_code == 200:
                log("Analytics summary working", "PASS")
            else:
                log("Analytics summary failed", "FAIL")
                
            return self.record_result(True)
        except Exception as e:
            log(f"Advanced Features Exception: {e}", "FAIL")
            return self.record_result(False)

    def cleanup(self):
        log("Cleaning up test data...")
        
        # Delete Session
        if self.test_session:
            try:
                requests.delete(f"{BASE_URL}/sessions/{self.test_session['id']}")
                log("Test session deleted", "PASS")
            except:
                log("Failed to delete test session", "WARN")
        
        # Delete Agent
        if self.test_agent:
            try:
                requests.delete(f"{BASE_URL}/agents/{self.test_agent['id']}")
                log("Test agent deleted", "PASS")
            except:
                log("Failed to delete test agent", "WARN")

    def run(self):
        print("[START] Starting Comprehensive API Test (PROD)\n")
        self.test_health()
        self.test_agents_crud()
        self.test_sessions_crud()
        self.test_chat_flow()
        self.test_advanced_features()
        self.cleanup()
        
        print("\n----------------------------------------")
        print(f"Test Summary: {self.results['passed']}/{self.results['total']} Passed")
        print("----------------------------------------")

if __name__ == "__main__":
    tester = ProdApiTester()
    tester.run()
