import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize the OpenAI client with Z.ai's endpoint
client = OpenAI(
    api_key=os.getenv("ZAI_API_KEY"),
    base_url="https://api.z.ai/api/coding/paas/v4"  # Using coding endpoint for unlimited access
)

def chat_with_zai():
    """Interactive chat with Z.ai's GLM model"""
    print("Z.ai Chatbot - GLM-4.6")
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
            # Create chat completion with Z.ai
            response = client.chat.completions.create(
                model="glm-4.6",  # Using the latest GLM model
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
                stream=False
            )
            
            # Get the assistant's response
            message = response.choices[0].message
            
            # Check for reasoning content first (coding endpoint special feature)
            if hasattr(message, 'reasoning_content') and message.reasoning_content:
                reasoning = message.reasoning_content
                # Extract actual answer from reasoning content
                lines = reasoning.split('\n')
                answer_lines = []
                found_answer = False
                
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith(('1.', '2.', '3.', '4.', '5.', '*', '-', '#')):
                        # Look for direct answer
                        if any(keyword in line.lower() for keyword in ['answer:', 'result:', 'therefore', 'so ', 'the answer']):
                            found_answer = True
                        if found_answer or len(line) < 100:
                            answer_lines.append(line)
                
                if answer_lines:
                    answer = ' '.join(answer_lines).strip()
                    print(f"Assistant: {answer}")
                else:
                    # Fallback to reasoning content (shortened)
                    reasoning_preview = reasoning[:200] + "..." if len(reasoning) > 200 else reasoning
                    print(f"Assistant: {reasoning_preview}")
                
                messages.append({"role": "assistant", "content": message.reasoning_content})
            elif message.content:
                print(f"Assistant: {message.content}")
                messages.append({"role": "assistant", "content": message.content})
            else:
                print("Assistant: [No response available]")
            
        except Exception as e:
            print(f"Error: {str(e)}")
            print("Please check your API key and connection.")

def test_zai_connection():
    """Test basic connection to Z.ai API"""
    print("Testing connection to Z.ai API...")
    
    try:
        response = client.chat.completions.create(
            model="glm-4.6",
            messages=[
                {"role": "user", "content": "Hello! Just testing the connection. Please respond with 'Connection successful!'"}
            ],
            max_tokens=50
        )
        
        print(f"Connection test successful!")
        print(f"Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"Connection test failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Check if API key is set
    if not os.getenv("ZAI_API_KEY"):
        print("Error: ZAI_API_KEY not found in environment variables.")
        print("Please create a .env file with your Z.ai API key:")
        print("ZAI_API_KEY=your_api_key_here")
        sys.exit(1)
    
    # Test connection first
    if test_zai_connection():
        print("\nStarting chat interface...\n")
        chat_with_zai()