#!/usr/bin/env python3
"""
Model comparison for Z.ai GLM models
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize the OpenAI client with Z.ai's coding endpoint
client = OpenAI(
    api_key=os.getenv("ZAI_API_KEY"),
    base_url="https://api.z.ai/api/coding/paas/v4"
)

# Model specifications
MODELS = {
    "glm-4.6": {
        "name": "GLM-4.6",
        "description": "Latest flagship model",
        "context_length": 128000,
        "pricing": {"input": 0.6, "output": 2.2},
        "features": ["Text", "Function Calling", "Streaming", "JSON Mode"]
    },
    "glm-4.5": {
        "name": "GLM-4.5",
        "description": "High performance model",
        "context_length": 96000,
        "pricing": {"input": 0.6, "output": 2.2},
        "features": ["Text", "Function Calling", "Streaming", "JSON Mode"]
    },
    "glm-4.5v": {
        "name": "GLM-4.5V",
        "description": "Visual reasoning model",
        "context_length": 16000,
        "pricing": {"input": 0.6, "output": 1.8},
        "features": ["Text", "Vision", "Image Analysis", "Streaming"]
    },
    "glm-4.5-air": {
        "name": "GLM-4.5-Air",
        "description": "Cost-efficient model",
        "context_length": 128000,
        "pricing": {"input": 0.2, "output": 1.1},
        "features": ["Text", "Function Calling", "Streaming", "JSON Mode"]
    },
    "glm-4.5-flash": {
        "name": "GLM-4.5-Flash",
        "description": "Free model",
        "context_length": 128000,
        "pricing": {"input": 0, "output": 0},
        "features": ["Text", "Function Calling", "Streaming", "JSON Mode"]
    }
}

def display_model_info():
    """Display comparison of all models"""
    print("Z.ai GLM Models Comparison")
    print("=" * 100)
    
    # Header
    print(f"{'Model':<15} {'Context':<10} {'Input $/M':<10} {'Output $/M':<10} {'Features'}")
    print("-" * 100)
    
    # Model info
    for model_id, info in MODELS.items():
        print(f"{info['name']:<15} {info['context_length']:<10} "
              f"{info['pricing']['input']:<10.2f} {info['pricing']['output']:<10.2f} "
              f"{', '.join(info['features'])}")
    
    print("\nModel Details:")
    print("-" * 100)
    
    for model_id, info in MODELS.items():
        print(f"\n{info['name']} ({model_id})")
        print(f"  Description: {info['description']}")
        print(f"  Context Length: {info['context_length']:,} tokens")
        print(f"  Pricing: ${info['pricing']['input']}/1M input tokens, ${info['pricing']['output']}/1M output tokens")
        print(f"  Features: {', '.join(info['features'])}")

def test_model_performance(model_id, test_message="Write a short poem about AI."):
    """Test a specific model's performance"""
    print(f"\nTesting {MODELS[model_id]['name']}...")
    
    try:
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "user", "content": test_message}
            ],
            max_tokens=100,
            temperature=0.7
        )
        
        result = response.choices[0].message.content
        print(f"Response: {result[:100]}...")
        
        # Return usage info if available
        if hasattr(response, 'usage'):
            usage = response.usage
            print(f"   Tokens used: {usage.prompt_tokens} input, {usage.completion_tokens} output")
            
            # Calculate cost
            input_cost = (usage.prompt_tokens / 1000000) * MODELS[model_id]['pricing']['input']
            output_cost = (usage.completion_tokens / 1000000) * MODELS[model_id]['pricing']['output']
            total_cost = input_cost + output_cost
            
            print(f"   Estimated cost: ${total_cost:.6f}")
        
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def compare_models():
    """Compare models with a simple test"""
    print("\nModel Performance Comparison")
    print("=" * 50)
    
    test_message = "Explain quantum computing in one sentence."
    
    results = {}
    for model_id in MODELS.keys():
        print(f"\nTesting {model_id}...")
        try:
            start_time = time.time()
            response = client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "user", "content": test_message}
                ],
                max_tokens=50,
                temperature=0.7
            )
            
            elapsed_time = time.time() - start_time
            result = response.choices[0].message.content
            
            results[model_id] = {
                "response": result,
                "time": elapsed_time,
                "tokens": response.usage.prompt_tokens if hasattr(response, 'usage') else None
            }
            
            print(f"Response: {result[:50]}... ({elapsed_time:.2f}s)")
            
        except Exception as e:
            print(f"Error: {str(e)}")
            results[model_id] = {"error": str(e)}
    
    return results

def recommend_model(use_case, budget="free", priority="performance"):
    """Recommend a model based on use case"""
    print(f"\nModel Recommendation for: {use_case}")
    print(f"Budget: {budget}, Priority: {priority}")
    print("-" * 50)
    
    # Simple recommendation logic
    if budget == "free":
        recommendation = "glm-4.5-flash"
        reason = "Free model with all basic features"
    elif priority == "performance":
        recommendation = "glm-4.6"
        reason = "Latest flagship model with best performance"
    elif priority == "cost":
        recommendation = "glm-4.5-air"
        reason = "Most cost-effective model with good performance"
    elif "image" in use_case.lower() or "vision" in use_case.lower():
        recommendation = "glm-4.5v"
        reason = "Only model with vision capabilities"
    elif priority == "balance":
        recommendation = "glm-4.5"
        reason = "Good balance of performance and features"
    else:
        recommendation = "glm-4.6"
        reason = "Default recommendation for general use"
    
    print(f"Recommended Model: {MODELS[recommendation]['name']}")
    print(f"Reason: {reason}")
    print(f"Model ID: {recommendation}")
    
    return recommendation

if __name__ == "__main__":
    import time
    
    # Check if API key is set
    if not os.getenv("ZAI_API_KEY"):
        print("Error: ZAI_API_KEY not found in environment variables.")
        print("Please create a .env file with your Z.ai API key:")
        print("ZAI_API_KEY=your_api_key_here")
        sys.exit(1)
    
    # Display model information
    display_model_info()
    
    # Get user choice
    print("\nWhat would you like to do?")
    print("1. Test a specific model")
    print("2. Compare all models")
    print("3. Get model recommendation")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        print("\nAvailable models:")
        for i, model_id in enumerate(MODELS.keys(), 1):
            print(f"{i}. {MODELS[model_id]['name']}")
        
        model_choice = input("Enter model number: ").strip()
        try:
            model_index = int(model_choice) - 1
            model_id = list(MODELS.keys())[model_index]
            test_model_performance(model_id)
        except (ValueError, IndexError):
            print("Invalid choice")
    
    elif choice == "2":
        compare_models()
    
    elif choice == "3":
        use_case = input("Describe your use case: ").strip()
        budget = input("Your budget (free/low/medium/high): ").strip()
        priority = input("Your priority (performance/cost/balance): ").strip()
        recommend_model(use_case, budget, priority)
    
    else:
        print("Invalid choice")