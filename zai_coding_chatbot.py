import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize the OpenAI client with Z.ai's coding endpoint
client = OpenAI(
    api_key=os.getenv("ZAI_API_KEY"),
    base_url="https://api.z.ai/api/coding/paas/v4"
)

def chat_with_zai_coding():
    """Interactive chat with Z.ai's GLM model using coding endpoint"""
    print("Z.ai Coding Chatbot - GLM-4.6")
    print("Using coding endpoint with unlimited access")
    print("Type 'quit' or 'exit' to end the conversation\n")
    
    # Initialize conversation history
    messages = [
        {
            "role": "system",
            "content": "You are a helpful AI assistant powered by Z.ai's GLM-4.6 model. Be concise and helpful."
        }
    ]
    
    while True:
        # Get user input
        user_input = input("You: ").strip()
        
        # Check for exit commands
        if user_input.lower() in ['quit', 'exit']:
            print("Goodbye!")
            break
        
        # Skip empty input
        if not user_input:
            continue
            
        # Add user message to conversation
        messages.append({"role": "user", "content": user_input})
        
        try:
            # Create chat completion with Z.ai coding endpoint
            response = client.chat.completions.create(
                model="glm-4.6",  # Using the GLM-4.6 model
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
                stream=False
            )
            
            # Get the assistant's response
            message = response.choices[0].message
            
            # Check for reasoning content first (coding endpoint special feature)
            if message.reasoning_content:
                print(f"Assistant: {message.reasoning_content}")
                messages.append({"role": "assistant", "content": message.reasoning_content})
            elif message.content:
                print(f"Assistant: {message.content}")
                messages.append({"role": "assistant", "content": message.content})
            else:
                print("Assistant: [No response available]")
            
        except Exception as e:
            print(f"Error: {str(e)}")
            print("Please check your API key and connection.")

def test_zai_coding_connection():
    """Test basic connection to Z.ai coding API"""
    print("Testing connection to Z.ai Coding API...")
    
    try:
        response = client.chat.completions.create(
            model="glm-4.6",
            messages=[
                {"role": "user", "content": "Hello! Just testing the connection. Please respond with 'Connection successful!'"}
            ],
            max_tokens=50
        )
        
        message = response.choices[0].message
        
        print(f"Connection test successful!")
        
        # Check for reasoning content
        if message.reasoning_content:
            print(f"Response: {message.reasoning_content[:100]}...")
        elif message.content:
            print(f"Response: {message.content[:100]}...")
        
        # Print usage info
        if hasattr(response, 'usage'):
            usage = response.usage
            print(f"Tokens used: {usage.prompt_tokens} input, {usage.completion_tokens} output")
            if hasattr(usage, 'prompt_tokens_details') and usage.prompt_tokens_details and usage.prompt_tokens_details.cached_tokens:
                print(f"Cached tokens: {usage.prompt_tokens_details.cached_tokens}")
        
        return True
        
    except Exception as e:
        print(f"Connection test failed: {str(e)}")
        return False

def test_streaming_coding():
    """Test streaming with coding endpoint"""
    print("Testing streaming with coding API...")
    
    try:
        stream = client.chat.completions.create(
            model="glm-4.6",
            messages=[
                {"role": "user", "content": "Count from 1 to 5 slowly"}
            ],
            stream=True,
            max_tokens=50
        )
        
        print("Streaming response: ", end="", flush=True)
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
        
        print("\nStreaming test successful!")
        return True
        
    except Exception as e:
        print(f"Streaming test failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Check if API key is set
    if not os.getenv("ZAI_API_KEY"):
        print("Error: ZAI_API_KEY not found in environment variables.")
        print("Please create a .env file with your Z.ai API key:")
        print("ZAI_API_KEY=your_api_key_here")
        sys.exit(1)
    
    # Test connection first
    if test_zai_coding_connection():
        print("\nStarting chat interface...\n")
        chat_with_zai_coding()