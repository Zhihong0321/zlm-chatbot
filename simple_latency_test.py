#!/usr/bin/env python3
"""
Simple Z.ai API Latency Test
Tests direct API response times using codebase configuration
"""

import os
import sys
import time
import statistics
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from codebase .env
load_dotenv()

def test_zai_latency():
    """Test Z.ai API latency with simple messages"""
    
    print("Z.ai API Latency Test")
    print("=" * 40)
    print(f"Testing at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check API key
    api_key = os.getenv("ZAI_API_KEY")
    if not api_key:
        print("ERROR: ZAI_API_KEY not found in environment variables")
        print("Please check your .env file")
        return False
    
    print(f"Using API Key: {api_key[:15]}...")
    
    # Test configuration - ONLY CODING ENDPOINT
    endpoints = [
        ("Coding Endpoint", "https://api.z.ai/api/coding/paas/v4", "glm-4.6"),
    ]
    
    test_messages = [
        "Hello, just testing response time.",
        "What is 2+2?", 
        "Briefly explain AI.",
    ]
    
    results = []
    
    print("\nStarting latency tests...")
    
    for endpoint_name, endpoint_url, model in endpoints:
        print(f"\n--- Testing {endpoint_name} ---")
        
        try:
            client = OpenAI(
                api_key=api_key,
                base_url=endpoint_url
            )
            
            endpoint_results = []
            
            for i, message in enumerate(test_messages, 1):
                print(f"Test {i}: {message[:30]}...")
                
                start_time = time.time()
                
                try:
                    response = client.chat.completions.create(
                        model=model,
                        messages=[{"role": "user", "content": message}],
                        temperature=0.7,
                        max_tokens=50
                    )
                    
                    end_time = time.time()
                    latency = end_time - start_time
                    
                    content = response.choices[0].message.content
                    
                    print(f"  SUCCESS: {latency:.2f}s")
                    print(f"  Response: {content[:50]}...")
                    
                    endpoint_results.append({
                        "success": True,
                        "latency": latency,
                        "response_length": len(content)
                    })
                    
                    # Small delay between tests
                    if i < len(test_messages):
                        time.sleep(1)
                
                except Exception as e:
                    end_time = time.time()
                    latency = end_time - start_time
                    print(f"  FAILED: {latency:.2f}s - {str(e)}")
                    
                    endpoint_results.append({
                        "success": False,
                        "latency": latency,
                        "error": str(e)
                    })
            
            # Calculate endpoint statistics
            successful = [r for r in endpoint_results if r["success"]]
            if successful:
                latencies = [r["latency"] for r in successful]
                avg_latency = statistics.mean(latencies)
                print(f"\n{endpoint_name} Results:")
                print(f"  Success rate: {len(successful)}/{len(endpoint_results)}")
                print(f"  Average latency: {avg_latency:.2f}s")
                print(f"  Min latency: {min(latencies):.2f}s")
                print(f"  Max latency: {max(latencies):.2f}s")
            else:
                print(f"\n{endpoint_name}: All tests failed")
            
            results.extend(endpoint_results)
            
        except Exception as e:
            print(f"ERROR setting up client: {str(e)}")
    
    # Overall analysis
    print(f"\n" + "=" * 40)
    print("OVERALL RESULTS")
    print("=" * 40)
    
    all_successful = [r for r in results if r["success"]]
    
    if all_successful:
        all_latencies = [r["latency"] for r in all_successful]
        
        print(f"Total successful calls: {len(all_successful)}")
        print(f"Average latency: {statistics.mean(all_latencies):.2f}s")
        print(f"Min latency: {min(all_latencies):.2f}s")
        print(f"Max latency: {max(all_latencies):.2f}s")
        
        # Categorize performance
        fast = len([l for l in all_latencies if l < 5])
        medium = len([l for l in all_latencies if 5 <= l < 30])
        slow = len([l for l in all_latencies if l >= 30])
        
        print(f"\nPerformance breakdown:")
        print(f"  Fast (<5s): {fast} calls")
        print(f"  Medium (5-30s): {medium} calls") 
        print(f"  Slow (>30s): {slow} calls")
        
        print(f"\nRecommendations:")
        if slow > 0:
            print("  - Slow responses detected. Check network connectivity")
        if medium > 0:
            print("  - Some responses are slow, but acceptable")
        if fast == len(all_successful):
            print("  - Excellent performance! All responses are fast")
    else:
        print("No successful API calls")
    
    return len(all_successful) > 0

if __name__ == "__main__":
    try:
        success = test_zai_latency()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nTest failed: {str(e)}")
        sys.exit(1)
