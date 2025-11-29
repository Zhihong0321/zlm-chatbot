#!/usr/bin/env python3
"""
Test script to verify Z.ai API connection
"""

import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

def main():
    """Test API connection"""
    print("Testing Z.ai API Connection")
    print("=" * 30)
    
    # Load environment variables
    load_dotenv()
    
    # Check API key
    api_key = os.getenv("ZAI_API_KEY")
    if not api_key or api_key == "your_zai_api_key_here":
        print("ZAI_API_KEY not configured")
        print("Please edit .env file and add your Z.ai API key")
        return False
    
    print("API key found")
    
    try:
        # Initialize client
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.z.ai/api/coding/paas/v4"  # Using coding endpoint for unlimited access
        )
        
        # Test connection with a simple request
        print("Testing connection...")
        response = client.chat.completions.create(
            model="glm-4.6",  # Using GLM-4.6 model with coding endpoint
            messages=[
                {"role": "user", "content": "Respond with 'Connection successful!'"}
            ],
            max_tokens=50
        )
        
        message = response.choices[0].message
        print("Connection successful!")
        
        # Check for reasoning content
        if hasattr(message, 'reasoning_content') and message.reasoning_content:
            print(f"Response: {message.reasoning_content[:100]}...")
        elif message.content:
            print(f"Response: {message.content[:100]}...")
        else:
            print("Response: [No content available]")
        
        return True
        
    except Exception as e:
        print("Connection failed: " + str(e))
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)