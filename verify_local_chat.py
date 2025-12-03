import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

try:
    client = OpenAI(
        api_key=os.getenv("ZAI_API_KEY"),
        base_url="https://api.z.ai/api/coding/paas/v4"
    )
    
    print(f"Client created successfully. OpenAI version: {sys.modules['openai'].__version__}")
    
    response = client.chat.completions.create(
        model="glm-4.5",
        messages=[{"role": "user", "content": "Hello"}],
        max_tokens=10
    )
    print("Chat success:", response.choices[0].message.content or response.choices[0].message.reasoning_content)
    
except Exception as e:
    print(f"Local Test Failed: {e}")
