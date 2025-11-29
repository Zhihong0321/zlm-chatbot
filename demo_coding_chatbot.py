#!/usr/bin/env python3
"""
Demo script to showcase Z.ai coding endpoint capabilities
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client with Z.ai's coding endpoint
client = OpenAI(
    api_key=os.getenv("ZAI_API_KEY"),
    base_url="https://api.z.ai/api/coding/paas/v4"
)

def demo_reasoning_content():
    """Demonstrate reasoning content feature"""
    print("=== Z.ai Coding Endpoint - Reasoning Content Demo ===\n")
    
    questions = [
        "What is 2+2?",
        "Explain the concept of machine learning",
        "Write a Python function to check if a number is prime"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n--- Question {i}: {question} ---")
        print("Processing...")
        
        try:
            response = client.chat.completions.create(
                model="glm-4.6",
                messages=[
                    {"role": "user", "content": question}
                ],
                max_tokens=200
            )
            
            message = response.choices[0].message
            
            if hasattr(message, 'reasoning_content') and message.reasoning_content:
                # Show first 200 chars of reasoning
                reasoning_preview = message.reasoning_content[:200] + "..." if len(message.reasoning_content) > 200 else message.reasoning_content
                print(f"Reasoning: {reasoning_preview}")
            
            if message.content:
                print(f"Answer: {message.content}")
            else:
                print("Answer: [No direct answer available in content field]")
                
        except Exception as e:
            print(f"Error: {str(e)}")

def demo_different_models():
    """Test different models with coding endpoint"""
    print("\n=== Testing Different Models ===\n")
    
    models = ["glm-4.6", "glm-4.5", "glm-4.5-air"]
    test_prompt = "What is the difference between Python and JavaScript?"
    
    for model in models:
        print(f"\n--- Testing {model} ---")
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": test_prompt}
                ],
                max_tokens=100
            )
            
            message = response.choices[0].message
            
            # Check for reasoning content
            if hasattr(message, 'reasoning_content') and message.reasoning_content:
                reasoning_preview = message.reasoning_content[:100] + "..." if len(message.reasoning_content) > 100 else message.reasoning_content
                print(f"Reasoning: {reasoning_preview}")
            
            if message.content:
                print(f"Response: {message.content[:100]}...")
            else:
                print("Response: [No content available]")
            
            # Usage stats
            if hasattr(response, 'usage'):
                usage = response.usage
                print(f"Tokens: {usage.prompt_tokens} input, {usage.completion_tokens} output")
                
        except Exception as e:
            print(f"Error with {model}: {str(e)}")

def main():
    """Run all demos"""
    # Check API key
    if not os.getenv("ZAI_API_KEY"):
        print("Error: ZAI_API_KEY not configured. Please edit .env file.")
        return
    
    print("Z.ai Coding Endpoint Demo")
    print("=" * 50)
    print("This demo shows the special reasoning content feature")
    print("available through the coding API endpoint.\n")
    
    # Run demos
    demo_reasoning_content()
    demo_different_models()
    
    print("\n" + "=" * 50)
    print("Demo completed!")
    print("\nTo run an interactive chat session:")
    print("python zai_chatbot.py")

if __name__ == "__main__":
    main()