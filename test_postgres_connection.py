#!/usr/bin/env python3
"""
TEST SCRIPT: Verify PostgreSQL connection and show data
Run this to SEE if your Railway app is using PostgreSQL
"""

import requests
import json
import sys

def test_railway_postgres():
    """Test if Railway app is actually connected to PostgreSQL"""
    
    # Replace with your actual Railway URL
    app_url = "https://zlm-chatbot-production.up.railway.app"
    
    print("TESTING: Is Railway app connected to PostgreSQL?")
    print("=" * 60)
    
    # Test 1: Health check - shows database status
    print("\n1. HEALTH CHECK - Database Connection Status:")
    try:
        response = requests.get(f"{app_url}/api/v1/ui/health", timeout=10)
        health_data = response.json()
        print(f"   Status: {health_data.get('status', 'NO STATUS')}")
        print(f"   Full Health Data: {json.dumps(health_data, indent=2)}")
        
        if "Database connection" in health_data.get('status', ''):
            print(f"   Success: PostgreSQL connection: DETECTED")
        else:
            print(f"   Failure: PostgreSQL connection: NOT DETECTED")
            
    except Exception as e:
        print(f"   Failure: Health check failed: {e}")
    
    # Test 2: Check if agents exist in database
    print("\n2. AGENTS TEST - PostgreSQL Data Check:")
    try:
        response = requests.get(f"{app_url}/api/v1/agents/", timeout=10)
        agents = response.json()
        
        if isinstance(agents, list) and len(agents) > 0:
            print(f"   Success: Found {len(agents)} agents in database")
            for agent in agents[:3]:  # Show first 3
                print(f"      - {agent.get('name', 'No Name')} (ID: {agent.get('id', 'No ID')})")
        else:
            print(f"   Failure: No agents found - database connection issue")
            
    except Exception as e:
        print(f"   Failure: Agents check failed: {e}")
    
    # Test 3: Check if sessions exist
    print("\n3. SESSIONS TEST - PostgreSQL Data Check:")
    try:
        response = requests.get(f"{app_url}/api/v1/sessions/", timeout=10)
        sessions = response.json()
        
        if isinstance(sessions, list) and len(sessions) > 0:
            print(f"   Success: Found {len(sessions)} sessions in database")
        else:
            print("   Failure: No sessions found - database connection issue")
            
    except Exception as e:
        print(f"   Failure: Sessions check failed: {e}")
    
    # Test 4: Try to create a session - database write test
    print("\n4. WRITE TEST - Can we write to PostgreSQL:")
    try:
        # Get first agent
        agents_response = requests.get(f"{app_url}/api/v1/agents/", timeout=10)
        agents = agents_response.json()
        
        if agents:
            agent_id = agents[0].get('id')
            session_data = {
                "title": "PostgreSQL Test Session",
                "agent_id": agent_id
            }
            
            response = requests.post(
                f"{app_url}/api/v1/sessions/",
                json=session_data,
                timeout=10
            )
            
            if response.status_code == 200:
                new_session = response.json()
                session_id = new_session.get('id')
                print(f"   Success: Successfully created session {session_id} in PostgreSQL")
                
                # Clean up - delete the test session
                delete_response = requests.delete(f"{app_url}/api/v1/sessions/{session_id}", timeout=10)
                if delete_response.status_code == 200:
                    print("   Success: Successfully deleted test session")
                
            else:
                print(f"   Failure: Failed to create session: {response.status_code}")
        else:
            print("   Failure: No agents available for session test")
            
    except Exception as e:
        print(f"   Failure: Write test failed: {e}")
    
    print("\n" + "=" * 60)
    print("SUMMARY: If you see Success checks above, PostgreSQL is working!")
    print("If you see Failure checks, PostgreSQL is NOT working properly")
    print(f"Test completed for: {app_url}")

if __name__ == "__main__":
    test_railway_postgres()