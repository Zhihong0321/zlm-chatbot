#!/usr/bin/env python3
"""
Z.ai API Latency Test Suite
Tests direct API calls using codebase configuration and measures response times
"""

import os
import sys
import time
import statistics
import asyncio
import httpx
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from codebase .env
load_dotenv()

class ZaiLatencyTester:
    """Comprehensive latency testing for Z.ai API"""
    
    def __init__(self):
        self.api_key = os.getenv("ZAI_API_KEY")
        self.results = []
        
        if not self.api_key:
            raise ValueError("ZAI_API_KEY not found in environment variables")
        
        if os.getenv("ZAI_API_KEY").startswith('600826'):
            print("   WARNING: Using example API key - may not work")
        else:
            print(f"   Using API Key: {self.api_key[:20]}...")
    
    def test_connection_with_httpx(self, endpoint: str, timeout: int = 10):
        """Test basic connectivity to Z.ai endpoints"""
        print(f"\n🌐 Testing connectivity to: {endpoint}")
        
        try:
            start_time = time.time()
            
            # Test with httpx (what OpenAI uses internally)
            with httpx.Client(timeout=timeout) as client:
                response = client.post(
                    endpoint,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "glm-4.6",
                        "messages": [{"role": "user", "content": "Hello, just testing connection."}],
                        "max_tokens": 10
                    }
                )
            
            end_time = time.time()
            latency = end_time - start_time
            
            if response.status_code == 200:
                print(f"✅ Connection successful!")
                print(f"   Response time: {latency:.2f}s")
                print(f"   Status code: {response.status_code}")
                return True, latency
            else:
                print(f"❌ Connection failed!")
                print(f"   Status code: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False, latency
                
        except Exception as e:
            print(f"❌ Connection error: {str(e)}")
            return False, 0
    
    def test_endpoint_with_openai(self, endpoint: str, model: str, messages: list, max_tokens: int = 100):
        """Test endpoint using OpenAI client (real API call)"""
        print(f"\n🤖 Testing {model} on {endpoint}")
        
        try:
            from openai import OpenAI
            
            start_time = time.time()
            
            client = OpenAI(
                api_key=self.api_key,
                base_url=endpoint
            )
            
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=max_tokens
            )
            
            end_time = time.time()
            latency = end_time - start_time
            
            message = response.choices[0].message
            content = message.reasoning_content if message.reasoning_content else message.content
            
            print(f"✅ API call successful!")
            print(f"   Response time: {latency:.2f}s")
            print(f"   Content length: {len(content)} chars")
            print(f"   Model used: {model}")
            print(f"   Preview: {content[:100]}...")
            
            return {
                "success": True,
                "latency": latency,
                "content": content,
                "model": model,
                "endpoint": endpoint,
                "content_length": len(content),
                "token_usage": response.usage.model_dump() if response.usage else None
            }
            
        except Exception as e:
            print(f"❌ API call failed: {str(e)}")
            return {
                "success": False,
                "latency": 0,
                "error": str(e),
                "model": model,
                "endpoint": endpoint
            }
    
    def test_streaming_latency(self, endpoint: str, model: str, message: str):
        """Test streaming response latency"""
        print(f"\n🌊 Testing streaming {model} on {endpoint}")
        
        try:
            from openai import OpenAI
            
            client = OpenAI(
                api_key=self.api_key,
                base_url=endpoint
            )
            
            start_time = time.time()
            first_chunk_time = None
            chunk_count = 0
            total_chars = 0
            
            stream = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": message}],
                temperature=0.7,
                max_tokens=200,
                stream=True
            )
            
            for chunk in stream:
                chunk_count += 1
                if first_chunk_time is None:
                    first_chunk_time = time.time()
                    first_chunk_latency = first_chunk_time - start_time
                    print(f"   First chunk received: {first_chunk_latency:.2f}s")
                
                if chunk.choices[0].delta.content:
                    total_chars += len(chunk.choices[0].delta.content)
            
            end_time = time.time()
            total_latency = end_time - start_time
            
            print(f"✅ Streaming completed!")
            print(f"   Total time: {total_latency:.2f}s")
            print(f"   First chunk: {first_chunk_latency:.2f}s")
            print(f"   Total chars: {total_chars}")
            print(f"   Chunks received: {chunk_count}")
            
            return {
                "success": True,
                "total_latency": total_latency,
                "first_chunk_latency": first_chunk_latency,
                "total_chars": total_chars,
                "chunk_count": chunk_count,
                "model": model
            }
            
        except Exception as e:
            print(f"❌ Streaming failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def run_comprehensive_latency_test(self):
        """Run comprehensive latency tests across multiple conditions"""
        print("Starting Comprehensive Z.ai API Latency Test")
        print("=" * 70)
        
        test_messages = [
            {"role": "user", "content": "What is artificial intelligence?"},
            {"role": "user", "content": "Explain machine learning in simple terms."},
            {"role": "user", "content": "Provide a brief summary of climate change causes."},
        ]
        
        endpoints_and_models = [
            ("https://api.z.ai/api/coding/paas/v4", "glm-4.6"),  # Free unlimited coding endpoint ONLY
        ]
        
        all_results = []
        
        # Test connectivity first
        print("\n" + "="*50)
        print("CONNECTIVITY TESTS")
        print("="*50)
        
        connectivity_results = {}
        for endpoint, _ in endpoints_and_models:
            success, latency = self.test_connection_with_httpx(endpoint)
            connectivity_results[endpoint] = {"success": success, "latency": latency}
        
        # Test API calls
        print("\n" + "="*50)
        print("LATENCY TESTS")
        print("="*50)
        
        for endpoint, model in endpoints_and_models:
            if not connectivity_results[endpoint]["success"]:
                print(f"Skipping {endpoint} (connectivity failed)")
                continue
            
            endpoint_results = []
            
            for i, message in enumerate(test_messages[:2]):  # Test 2 messages per model
                print(f"\n--- Test {i+1}: {model} on {endpoint} ---")
                
                result = self.test_endpoint_with_openai(endpoint, model, [message], max_tokens=100)
                result["test_number"] = i + 1
                endpoint_results.append(result)
                all_results.append(result)
                
                # Add delay between tests
                if i < len(test_messages) - 1:
                    print("   Waiting 2 seconds before next test...")
                    time.sleep(2)
            
            # Calculate averages for this endpoint/model
            successful_results = [r for r in endpoint_results if r["success"]]
            if successful_results:
                latencies = [r["latency"] for r in successful_results]
                avg_latency = statistics.mean(latencies)
                print(f"   {model} on {endpoint}:")
                print(f"   Average latency: {avg_latency:.2f}s")
                print(f"   Min latency: {min(latencies):.2f}s")
                print(f"   Max latency: {max(latencies):.2f}s")
        
        # Test streaming
        streaming_message = "Count from 1 to 5 slowly"
        print("\n" + "="*50)
        print("STREAMING TESTS")
        print("="*50)
        
        for endpoint, model in [("https://api.z.ai/api/coding/paas/v4", "glm-4.6")]:
            if connectivity_results[endpoint]["success"]:
                streaming_result = self.test_streaming_latency(endpoint, model, streaming_message)
                all_results.append(streaming_result)
        
        return all_results
    
    def analyze_results(self, results):
        """Analyze and present test results"""
        print("\n" + "="*60)
        print("RESULTS ANALYSIS")
        print("="*60)
        
        # Filter successful API calls
        api_results = [r for r in results if "token_usage" in r and r["success"]]
        
        if not api_results:
            print("No successful API calls to analyze")
            return
        
        latencies = [r["latency"] for r in api_results]
        
        print(f"🎯 Overall Statistics:")
        print(f"   Successful calls: {len(api_results)}")
        print(f"   Average latency: {statistics.mean(latencies):.2f}s")
        print(f"   Median latency: {statistics.median(latencies):.2f}s")
        print(f"   Min latency: {min(latencies):.2f}s")
        print(f"   Max latency: {max(latencies):.2f}s")
        print(f"   Std deviation: {statistics.stdev(latencies):.2f}s")
        
        # Latency categories
        fast_calls = [l for l in latencies if l < 5]
        medium_calls = [l for l in latencies if 5 <= l < 30]
        slow_calls = [l for l in latencies if l >= 30]
        
        print(f"\n⏱️  Latency Breakdown:")
        print(f"   Fast (<5s): {len(fast_calls)} calls ({len(fast_calls)/len(latencies)*100:.1f}%)")
        print(f"   Medium (5-30s): {len(medium_calls)} calls ({len(medium_calls)/len(latencies)*100:.1f}%)")
        print(f"   Slow (>30s): {len(slow_calls)} calls ({len(slow_calls)/len(latencies)*100:.1f}%)")
        
        # Model comparison
        models = {}
        for result in api_results:
            model = result["model"]
            if model not in models:
                models[model] = []
            models[model].append(result["latency"])
        
        print(f"\n🤖 Model Performance:")
        for model, model_latencies in models.items():
            print(f"   {model}: {statistics.mean(model_latencies):.2f}s avg ({len(model_latencies)} calls)")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        
        if slow_calls:
            print(f"   ⚠️  {len(slow_calls)} calls took >30s. Consider:")
            print(f"      - Check network connectivity")
            print(f"      - Use shorter prompts")
            print(f"      - Set proper timeout values")
        
        if statistics.mean(latencies) > 20:
            print(f"   ⚠️  Average latency is high. Check:")
            print(f"      - API key balance for main endpoint")
            print(f"      - Network routing to Z.ai servers")
            print(f"      - Consider using coding endpoint")
        
        if len(fast_calls) >= len(latencies) * 0.7:
            print(f"   ✅ Most calls are fast! System is performing well.")
    
    def save_results(self, results, filename: str = None):
        """Save test results to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"zai_latency_test_{timestamp}.json"
        
        with open(filename, 'w') as f:
            import json
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "api_key": self.api_key[:20] + "...",
                "results": results
            }, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {filename}")

def main():
    """Main test execution"""
    
    print("Z.ai API Latency Test Suite")
    print(f"Testing at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Check configuration
        if not os.getenv("ZAI_API_KEY"):
            print("ERROR: ZAI_API_KEY not found in environment variables")
            print("Please check your .env file or set the environment variable")
            return False
        
        # Run tests
        tester = ZaiLatencyTester()
        results = tester.run_comprehensive_latency_test()
        
        # Analyze results
        tester.analyze_results(results)
        
        # Save results
        tester.save_results(results)
        
        print(f"\nTest completed successfully!")
        return True
        
    except KeyboardInterrupt:
        print(f"\nTest cancelled by user")
        return False
    except Exception as e:
        print(f"\nTest failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
