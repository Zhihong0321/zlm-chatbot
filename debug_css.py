import requests

BASE_URL = "https://zlm-chatbot-production.up.railway.app"

def check_css_loading():
    print(f"Diagnosing CSS loading at {BASE_URL}...")
    
    # 1. Get index.html to find the CSS file name
    try:
        res = requests.get(BASE_URL)
        html_content = res.text
        
        if 'href="/assets/' in html_content:
            # Extract CSS path
            start = html_content.find('href="/assets/') + 6
            end = html_content.find('"', start)
            css_path = html_content[start:end]
            
            # Filter for .css
            if not css_path.endswith('.css'):
                # try to find next one
                start = html_content.find('href="/assets/', end) + 6
                end = html_content.find('"', start)
                css_path = html_content[start:end]

            print(f"Found CSS reference: {css_path}")
            
            # 2. Try to fetch the CSS file
            css_url = f"{BASE_URL}{css_path}"
            print(f"Fetching CSS from: {css_url}")
            
            css_res = requests.get(css_url)
            print(f"Status: {css_res.status_code}")
            print(f"Content-Type: {css_res.headers.get('content-type')}")
            print(f"Content Length: {len(css_res.text)}")
            
            if css_res.status_code == 200:
                print("\nFirst 100 chars of CSS:")
                print(css_res.text[:100])
            else:
                print("FAILED to fetch CSS file")
        else:
            print("No CSS link found in index.html")
            print("HTML Preview:", html_content[:500])
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_css_loading()
