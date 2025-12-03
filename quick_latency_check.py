#!/usr/bin/env python3
"""
Quick Latency Check for Z.ai API
Simple test to identify why responses take 2+ minutes
"""

import os
import sys
import time
from openai import OpenAI

def main():
    print("Quick Z.ai API Latency Check")
    print("=" * 35)
    
    # Load environment
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("ZAI_API_KEY")
    if not api_key:
        print("ERROR: No ZAI_API_KEY found")
        return False
    
    print(f"API Key: {api_key[:15]}...")
    
    # Test ONLY coding endpoint
    endpoints = [
        ("Coding", "https://api.z.ai/api/coding/paas/v4")
    ]
    
    message = "What is 1+1? Just answer the number."
    
    for name, endpoint in endpoints:
        print(f"\n--- {name} ---")
        print(f"URL: {endpoint}")
        
        try:
            client = OpenAI(api_key=api_key, base_url=endpoint)
            
            print(f"Sending: {message}")
            start = time.time()
            
            response = client.chat.completions.create(
                model="glm-4.6",
                messages=[{"role": "user", "content": message}],
                max_tokens=10,
                timeout=30
            )
            
            end = time.time()
            latency = end - start
            
            result = response.choices[0].message.content
            print(f"Response: {result}")
            print(f"Time: {latency:.2f} seconds")
            
            if latency < 5:
                print("Status: FAST")
            elif latency < 30:
                print("Status: OK")
            else:
                print("Status: SLOW")
            
        except Exception as e:
            end = time.time()
            latency = end - start
            print(f"FAILED after {latency:.2f}s")
            print(f"Error: {str(e)}")
    
    print(f"\n" + "=" * 35)
    print("For response time issues:")
    print("1. Monitor network connectivity")
    print("2. Check backend timeout settings") 
    print("3. Consider response caching")
    print("4. Use coding endpoint (already configured)")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nCancelled")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
