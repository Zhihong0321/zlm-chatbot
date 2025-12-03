import os
import sys
import httpx
from openai import OpenAI

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.config import settings

# Global client instance
_client = None
_http_client = None

# Initialize Z.ai client (CODING ENDPOINT ONLY)
def get_zai_client():
    global _client, _http_client
    
    if _client is not None:
        return _client

    try:
        # Create a custom HTTP client to handle connection details explicitly
        # Reuse this http_client to keep connections alive (connection pooling)
        if _http_client is None:
            _http_client = httpx.Client(
                timeout=300.0,  # 5 minute timeout at HTTP level
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
            )
        
        _client = OpenAI(
            api_key=settings.ZAI_API_KEY,
            base_url="https://api.z.ai/api/coding/paas/v4",
            http_client=_http_client
        )
        return _client
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