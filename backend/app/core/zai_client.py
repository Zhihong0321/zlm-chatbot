import os
import sys
import httpx
from openai import OpenAI

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.config import settings

# Initialize Z.ai client (CODING ENDPOINT ONLY)
def get_zai_client():
    try:
        # Create a custom HTTP client to handle connection details explicitly
        # This avoids OpenAI client trying to auto-configure proxies in a way that might fail
        http_client = httpx.Client()
        
        return OpenAI(
            api_key=settings.ZAI_API_KEY,
            base_url="https://api.z.ai/api/coding/paas/v4",
            http_client=http_client
        )
    except TypeError as e:
        import openai
        # This helps debug if the server is running an old version or if args are wrong
        raise Exception(f"OpenAI Init Error (v{openai.__version__}): {str(e)}")


def chat_with_zai(message: str, system_prompt: str = None, model: str = "glm-4.6", temperature: float = 0.7):
    """
    Send a message to Z.ai GLM coding model and get response
    NOTE: Uses coding endpoint - available with Z.ai Coding Plan subscription
    """
    client = get_zai_client()
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    
    messages.append({"role": "user", "content": message})
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=2000
        )
        
        message = response.choices[0].message
        
        # Logic to separate Content and Reasoning
        # If content is present, use it. If empty, fall back to reasoning (some models only output reasoning)
        # This fixes the issue where reasoning overwrote the actual answer
        content = message.content
        if not content and message.reasoning_content:
             content = message.reasoning_content
        
        return {
            "content": content,
            "reasoning_content": message.reasoning_content,
            "model": model,
            "token_usage": response.usage.model_dump() if response.usage else None
        }
    except Exception as e:
        raise Exception(f"Z.ai Coding API error: {str(e)}")