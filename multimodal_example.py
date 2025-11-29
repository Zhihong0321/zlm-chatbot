import os
import sys
import base64
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize the OpenAI client with Z.ai's endpoint
client = OpenAI(
    api_key=os.getenv("ZAI_API_KEY"),
    base_url="https://api.z.ai/api/paas/v4"
)

def encode_image(image_path):
    """Encode image to base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_image(image_path, question="What do you see in this image?"):
    """Analyze an image using GLM-4.5V model"""
    try:
        # Get the base64 string
        base64_image = encode_image(image_path)
        
        # Create the message with image
        response = client.chat.completions.create(
            model="glm-4.5v",  # Using the vision model
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": question
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error analyzing image: {str(e)}"

def test_model_info():
    """Display information about available models"""
    print("Testing Z.ai API Models...")
    
    models_to_test = [
        ("GLM-4.6 (Text)", "glm-4.6"),
        ("GLM-4.5 (Text)", "glm-4.5"),
        ("GLM-4.5V (Vision)", "glm-4.5v"),
        ("GLM-4.5-Air (Efficient)", "glm-4.5-air"),
        ("GLM-4.5-Flash (Free)", "glm-4.5-flash")
    ]
    
    for display_name, model_id in models_to_test:
        try:
            response = client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "user", "content": f"Hello! Just testing {display_name}. Respond with 'Working!'"}
                ],
                max_tokens=10
            )
            print(f"{display_name}: {response.choices[0].message.content}")
        except Exception as e:
            print(f"{display_name}: {str(e)}")

def interactive_multimodal_chat():
    """Interactive chat with potential image support"""
    print("Z.ai Multimodal Chat")
    print("Commands:")
    print("  Type 'text: <message>' for text-only conversation")
    print("  Type 'image: <path> <question>' to analyze an image")
    print("  Type 'models' to test all available models")
    print("  Type 'quit' to exit\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'exit']:
            print("Goodbye!")
            break
        
        if user_input.lower() == 'models':
            test_model_info()
            continue
        
        if user_input.startswith('image:'):
            # Parse image command
            parts = user_input[6:].strip().split(' ', 1)
            if len(parts) == 2:
                image_path, question = parts
            else:
                image_path = parts[0]
                question = "What do you see in this image?"
            
            # Check if image exists
            if not os.path.exists(image_path):
                print(f"Error: Image file '{image_path}' not found.")
                continue
            
            print("Analyzing image...")
            result = analyze_image(image_path, question)
            print(f"Assistant: {result}")
        
        elif user_input.startswith('text:'):
            # Text-only conversation
            question = user_input[5:].strip()
            try:
                response = client.chat.completions.create(
                    model="glm-4.6",
                    messages=[
                        {"role": "user", "content": question}
                    ],
                    max_tokens=500
                )
                print(f"Assistant: {response.choices[0].message.content}")
            except Exception as e:
                print(f"Error: {str(e)}")
        
        else:
            print("Please use 'text: <message>' or 'image: <path> <question>' format")

if __name__ == "__main__":
    # Check if API key is set
    if not os.getenv("ZAI_API_KEY"):
        print("Error: ZAI_API_KEY not found in environment variables.")
        print("Please create a .env file with your Z.ai API key:")
        print("ZAI_API_KEY=your_api_key_here")
        sys.exit(1)
    
    print("Z.ai Multimodal Example")
    print("This example demonstrates text and vision capabilities.\n")
    
    # Start interactive chat
    interactive_multimodal_chat()