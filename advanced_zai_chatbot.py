import os
import sys
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize the OpenAI client with Z.ai's endpoint
client = OpenAI(
    api_key=os.getenv("ZAI_API_KEY"),
    base_url="https://api.z.ai/api/coding/paas/v4"  # Using coding endpoint for unlimited access
)

# Define a simple function for the model to call
def get_weather(location):
    """Mock function to get weather information"""
    weather_data = {
        "New York": {"temperature": "72°F", "condition": "Sunny"},
        "London": {"temperature": "60°F", "condition": "Rainy"},
        "Tokyo": {"temperature": "75°F", "condition": "Cloudy"},
        "Beijing": {"temperature": "68°F", "condition": "Clear"}
    }
    
    if location in weather_data:
        return json.dumps({
            "location": location,
            "temperature": weather_data[location]["temperature"],
            "condition": weather_data[location]["condition"]
        })
    else:
        return json.dumps({
            "error": f"Weather data not available for {location}"
        })

# Define the function schema for function calling
functions = [
    {
        "name": "get_weather",
        "description": "Get current weather information for a city",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city name, e.g., New York, London, Tokyo"
                }
            },
            "required": ["location"]
        }
    }
]

def stream_chat_with_zai():
    """Interactive streaming chat with function calling"""
    print("Z.ai Advanced Chatbot - GLM-4.6 with Streaming and Function Calling")
    print("Type 'quit' or 'exit' to end the conversation\n")
    
    # Initialize conversation history
    messages = [
        {
            "role": "system",
            "content": "You are a helpful AI assistant powered by Z.ai's GLM-4.6 model. You can help with various tasks including checking weather information."
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
            # Check if this is a weather-related query
            if "weather" in user_input.lower() or any(city in user_input.lower() for city in ["new york", "london", "tokyo", "beijing"]):
                # Try function calling
                response = client.chat.completions.create(
                    model="glm-4.6",
                    messages=messages,
                    functions=functions,
                    function_call="auto",
                    temperature=0.7
                )
                
                message = response.choices[0].message
                
                # Check if the model wants to call a function
                if message.function_call:
                    function_name = message.function_call.name
                    function_args = json.loads(message.function_call.arguments)
                    
                    if function_name == "get_weather":
                        # Execute the function
                        function_result = get_weather(function_args["location"])
                        
                        # Add function result to conversation
                        messages.append(message)
                        messages.append({
                            "role": "function",
                            "name": function_name,
                            "content": function_result
                        })
                        
                        # Get the final response from the model
                        final_response = client.chat.completions.create(
                            model="glm-4.6",
                            messages=messages,
                            temperature=0.7
                        )
                        
                        print(f"Assistant: {final_response.choices[0].message.content}")
                        messages.append(final_response.choices[0].message)
                else:
                    # Regular response without function calling
                    print(f"Assistant: {message.content}")
                    messages.append(message)
            else:
                # Regular streaming response
                print("Assistant: ", end="", flush=True)
                stream = client.chat.completions.create(
                    model="glm-4.6",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1000,
                    stream=True
                )
                
                assistant_response = ""
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        print(content, end="", flush=True)
                        assistant_response += content
                
                print()  # New line after streaming
                messages.append({"role": "assistant", "content": assistant_response})
            
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Please check your API key and connection.")

def test_streaming():
    """Test streaming functionality"""
    print("Testing streaming response from Z.ai API...")
    
    try:
        stream = client.chat.completions.create(
            model="glm-4.6",
            messages=[
                {"role": "user", "content": "Count from 1 to 5 slowly"}
            ],
            stream=True,
            max_tokens=100
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
    
    # Test streaming first
    if test_streaming():
        print("\nStarting advanced chat interface...\n")
        stream_chat_with_zai()