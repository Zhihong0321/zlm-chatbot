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

def simple_chat():
    """Simple interactive chat with Z.ai's GLM model"""
    print("Z.ai Simple Chat - GLM-4.6")
    print("Type 'quit' or 'exit' to end the conversation\n")
    
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
            
        try:
            # Create chat completion with Z.ai coding endpoint
            response = client.chat.completions.create(
                model="glm-4.6",
                messages=[
                    {"role": "user", "content": user_input}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            message = response.choices[0].message
            
            # Display reasoning content (special feature of coding endpoint)
            if hasattr(message, 'reasoning_content') and message.reasoning_content:
                print(f"Assistant: {message.reasoning_content}")
            elif message.content:
                print(f"Assistant: {message.content}")
            else:
                print("Assistant: [No response available]")
            
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    # Check if API key is set
    if not os.getenv("ZAI_API_KEY"):
        print("Error: ZAI_API_KEY not found in environment variables.")
        print("Please create a .env file with your Z.ai API key:")
        print("ZAI_API_KEY=your_api_key_here")
        exit(1)
    
    # Start chat
    simple_chat()