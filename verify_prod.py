import requests
import sys
import time
import json
from datetime import datetime

PROD_URL = "https://zlm-chatbot-production.up.railway.app"
HEALTH_ENDPOINT = f"{PROD_URL}/api/v1/ui/health"

def check_status():
    print(f"[{datetime.now().isoformat()}] Checking production status...")
    print(f"Target: {HEALTH_ENDPOINT}")
    
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=10)
        print(f"HTTP Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n--- Health Report ---")
            print(f"Overall Status: {data.get('status')}")
            print(f"Timestamp: {data.get('timestamp')}")
            
            details = data.get('details', {})
            
            # Database
            db = details.get('database', {})
            print("\n[Database]")
            print(f"  Status: {db.get('status')}")
            print(f"  Type: {db.get('type')}")
            print(f"  Version: {db.get('version')}")
            if 'tables' in db:
                print("  Tables:")
                for table, count in db['tables'].items():
                    print(f"    - {table}: {count} rows")
            if 'error' in db:
                print(f"  ERROR: {db.get('error')}")
            if 'connection_error' in db:
                print(f"  CONNECTION ERROR: {db.get('connection_error')}")

            # Z.ai API
            zai = details.get('zai_api', {})
            print("\n[Z.ai API]")
            print(f"  Status: {zai.get('status')}")
            
            return data.get('status') == 'healthy'
        else:
            print(f"Failed to get valid JSON response. Content preview: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("Connection Error: Could not connect to the server.")
        return False
    except requests.exceptions.Timeout:
        print("Timeout Error: Server took too long to respond.")
        return False
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return False

if __name__ == "__main__":
    success = check_status()
    if success:
        print("\n[OK] Production seems HEALTHY")
        sys.exit(0)
    else:
        print("\n[FAIL] Production seems UNHEALTHY")
        sys.exit(1)
