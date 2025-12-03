import requests
import sys

BASE_URL = "https://zlm-chatbot-production.up.railway.app"

def diagnose_frontend():
    print(f"Diagnosing frontend at {BASE_URL}...")
    
    # 1. Check Root (index.html)
    print("\n1. Checking Root (index.html)...")
    try:
        res = requests.get(BASE_URL)
        print(f"Status: {res.status_code}")
        print(f"Content Type: {res.headers.get('content-type')}")
        print(f"Content Length: {len(res.text)} bytes")
        if len(res.text) < 500:
            print("Content Preview:\n", res.text)
        else:
            print("Content Preview:\n", res.text[:200] + "...")
            
        # Extract script src
        if 'src="/assets/' in res.text:
            start = res.text.find('src="/assets/') + 5
            end = res.text.find('"', start)
            asset_path = res.text[start:end]
            print(f"\nFound Asset Reference: {asset_path}")
            
            # 2. Check Asset
            print(f"\n2. Checking Asset ({asset_path})...")
            asset_url = f"{BASE_URL}{asset_path}"
            res_asset = requests.get(asset_url)
            print(f"Status: {res_asset.status_code}")
            print(f"Content Type: {res_asset.headers.get('content-type')}")
            print(f"Content Length: {len(res_asset.text)} bytes")
        else:
             print("\nWARNING: No /assets/ script tag found in index.html")
             
    except Exception as e:
        print(f"Error: {e}")

    # 3. Check /assets/ mount directly
    print("\n3. Checking /assets/ directory listing (should be 404 or 403)...")
    res = requests.get(f"{BASE_URL}/assets/")
    print(f"Status: {res.status_code}")

if __name__ == "__main__":
    diagnose_frontend()
