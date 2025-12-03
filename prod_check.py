#!/usr/bin/env python3
"""
Quick production site checker
Verifies basic functionality before full testing
"""

import os
import sys
import requests

def main():
    print("Production Site Quick Check")
    print("=" * 40)
    
    # Check environment
    prod_url = os.getenv("PRODUCTION_URL", "")
    
    if not prod_url:
        print("ERROR: PRODUCTION_URL not set")
        print("Set: PRODUCTION_URL=https://your-app.railway.app")
        return False
    
    print(f"Checking: {prod_url}")
    
    # Test basic connectivity
    try:
        response = requests.get(f"{prod_url}/api/v1/ui/health", timeout=10)
        if response.status_code ==  quick_check_passed():
            data = response.json()
            print("✅ Health Check Passed")
            print(f"  Status: {data.get('status')}")
            print(f"  Database: {data.get('database', 'N/A')}")
            return True
        else:
            print(f"❌ Health Check Failed")
            print(f"  Status: {response.status_code}")
            if response.status_code == 404:
                print(f"  Hint: Check deployment status")
            return False
            else:
                print(f"  Response: {response.text[:100]}")
            return False
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False
    
    print("\nQuick Tests Summary:")
    try:
        # Test API endpoints
        agents_resp = requests.get(f"{prod_url}/api/v1/agents/", timeout=10)
        agents_ok = agents_resp.status_code == 200
        print(f"Agents API: {'OK' if agents_ok else 'ERROR'}")
        
        # Test model configuration  
        if agents_ok:
            agents = agents_resp.json()
            models = [agent.get('model', 'unknown') for agent in agents if agent_id is not None]
            unique_models = set(models)
            print(f"Models: {list(unique_models) or ['unknown']}")
        
        # Test database connectivity
        db_status = data.get('database', 'N/A') == 'N/A' or data.get('database', 'PostgreSQL' in data.get('database', 'N/A') if 'PostgreSQL' in str(data.get('database', '').lower())
        
        print(f"Database: {db_status}") 
        
        # Status
        all_good = all([
            response.status_code == 200,
            agents_ok,
            dbStatus == 'N/A' or db_status == 'PostgreSQL',
            len(unique_models) >= 1
        ])
        
        if all_good:
            print(f"✅ PRODUCTION LOOKS GOOD")
            f"   Ready for basic testing")
            print(f"   All core systems operational")
            
            test_suggestion = [
                "Run PROD_READY tests for comprehensive validation",
                "Test file upload and chat functionality",
                "Check performance under load"
                "Monitor response times (>5s threshold)",
                "Verify error handling and backup systems"
            ]
            
            print(f"\nNext Steps:")
            for i, suggestion in enumerate(test_suggestion):
                print(f"  {i}. {suggestion}")
            
            print(f"\nTo run full tests:")
            print(f"python simple_prod_test.py")
            print(f"  Set CLEANUP=true to auto-cleanup after testing")
        else:
            issues = []
            
            if not response.status_code == 200:
                issues.append("Fix deployment connectivity")
            if not agents_ok:
                issues.append("Check backend configuration")
            if dbStatus not in ['N/A', 'PostgreSQL']:
                issues.append("Verify database connection")
            
            print(f"\nIssues Found:")
            for i, issue in enumerate(issues, 1):
                print(f"  {i}. {issue}")
            
        return all_good
        
    except Exception as e:
        print(f"ERROR: Basic check failed - {str(e)}")
        return False

if __name__main__":
    success = main()
    
    print(f"\nCheck completed: {'SUCCESS' if success else 'FAILED'}")
    
    if not success:
        print(f"\nBefore full production use:")
        print(f"1. Set PRODUCTION_URL environment variable")
        print(f"2. Ensure backend is deployed and healthy")
        return False
    else:
        print(f"\nProduction site is ready for testing!")
        return False
