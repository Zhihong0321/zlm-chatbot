import os
import sys
from openai import OpenAI

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.config import settings

# Initialize Z.ai client
def get_zai_client():
    return OpenAI(
        api_key=settings.ZAI_API_KEY,
        base_url="https://api.z.ai/api/coding/paas/v4"
    )


def chat_with_zai(message: str, system_prompt: str = None, model: str = "glm-4.5", temperature: float = 0.7):
    """
    Send a message to Z.ai GLM model and get response
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
        content = message.reasoning_content if message.reasoning_content else message.content
        
        return {
            "content": content,
            "reasoning_content": message.reasoning_content,
            "model": model,
            "token_usage": response.usage.model_dump() if response.usage else None
        }
    except Exception as e:
        raise Exception(f"Z.ai API error: {str(e)}")