# Agent Guide for Z.ai Chatbot Examples

This document provides essential information for agents working with the Z.ai GLM model integration examples.

## Project Overview

This is a Python-based collection of chatbot examples demonstrating integration with Z.ai's GLM models (GLM-4.6, GLM-4.5, GLM-4.5V, GLM-4.5-Air, GLM-4.5-Flash). The project uses the OpenAI SDK with Z.ai's custom endpoints.

## Essential Commands

### Setup and Installation
```bash
# Initial setup (installs dependencies and creates .env file)
python setup.py

# Manual dependency installation
pip install -r requirements.txt

# Test API connection
python test_connection.py
```

### Running Chatbot Examples
```bash
# Basic interactive chatbot
python zai_chatbot.py

# Advanced chatbot with streaming and function calling
python advanced_zai_chatbot.py

# Simple chat with direct reasoning content access
python simple_zai_chat.py

# Coding endpoint demonstration with reasoning content
python demo_coding_chatbot.py

# Multimodal example with vision capabilities
python multimodal_example.py

# Model comparison tool
python model_comparison.py

# Coding-specific chatbot
python zai_coding_chatbot.py
```

## API Configuration

### Two Endpoints Available

1. **Main Endpoint** (`https://api.z.ai/api/paas/v4`)
   - Requires account balance
   - All models available except GLM-4.5-Flash (which is free)
   - Standard responses without reasoning content

2. **Coding Endpoint** (`https://api.z.ai/api/coding/paas/v4`) 
   - **Preferred for testing** - works with zero balance
   - Available models: GLM-4.6, GLM-4.5, GLM-4.5V, GLM-4.5-Air
   - **Special feature**: Provides `reasoning_content` field showing model's thinking process
   - Unlimited access for development/testing

### API Key Configuration
- Set in `.env` file as `ZAI_API_KEY`
- Get keys from: https://z.ai/manage-apikey/apikey-list
- Format: `600826c0141e4ecfb805fd64f1892a1c.pbvCuCAVDqSAPQP7`

## Code Organization and Structure

### Core Pattern
All examples follow this consistent initialization pattern:

```python
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize client with appropriate endpoint
client = OpenAI(
    api_key=os.getenv("ZAI_API_KEY"),
    base_url="https://api.z.ai/api/coding/paas/v4"  # or main endpoint
)
```

### File Structure
- `setup.py` - Installation and environment setup script
- `test_connection.py` - API connection verification
- `zai_chatbot.py` - Basic conversation example
- `advanced_zai_chatbot.py` - Streaming + function calling
- `simple_zai_chat.py` - Minimal implementation
- `zai_coding_chatbot.py` - Coding endpoint specific
- `demo_coding_chatbot.py` - Reasoning content demonstration
- `multimodal_example.py` - Vision/image analysis
- `model_comparison.py` - Model comparison tool
- `requirements.txt` - Dependencies (openai>=1.0.0, python-dotenv>=1.0.0)
- `.env.example` - Environment template
- `.env` - Actual API configuration (user-specific)
- `latest_status.md` - Current project status and testing results

## Naming Conventions and Style Patterns

### Code Style
- Python 3.7+ compatible
- Snake_case for variables and functions
- Descriptive function names: `chat_with_zai()`, `get_weather()`, `encode_image()`
- Clear docstrings for all functions
- Consistent error handling with try/except blocks

### Variable Patterns
- `client` - OpenAI client instance
- `messages` - Conversation history list
- `response` - API response object
- `api_key` - Stored in environment, not hardcoded

### Model Naming
- Use string identifiers: `"glm-4.6"`, `"glm-4.5"`, `"glm-4.5v"`, etc.
- Consistent lowercase with hyphens

## Testing Approach

### Connection Testing
Always verify connection with `test_connection.py` before running examples:
- Checks API key validity
- Tests endpoint connectivity
- Validates reasoning content availability
- Reports usage statistics

### Error Handling Patterns
All examples include comprehensive error handling:
- Missing or invalid API keys
- Network connectivity issues
- Invalid responses
- Model availability
- Rate limiting (Error code 1113 for insufficient balance)

### Testing Different Models
Use the model comparison tool to test different GLM models:
- Performance comparison
- Cost analysis
- Feature availability
- Use case recommendations

## Important Gotchas and Non-Obvious Patterns

### Reasoning Content Feature
The coding endpoint provides a unique `reasoning_content` field that shows the model's step-by-step thinking process:

```python
message = response.choices[0].message
if message.reasoning_content:
    print(f"Reasoning: {message.reasoning_content}")
elif message.content:
    print(f"Response: {message.content}")
```

### Model Response Differences
- **Main endpoint**: Standard `content` field
- **Coding endpoint**: Often has empty `content` but detailed `reasoning_content`

### Balance Requirements
- Main endpoint returns Error 1113 for insufficient balance
- Coding endpoint works with zero balance (preferred for development)
- GLM-4.5-Flash is free on main endpoint

### Function Calling Implementation
Function calling uses OpenAI-compatible format:
```python
functions = [
    {
        "name": "function_name",
        "description": "What the function does",
        "parameters": {
            "type": "object",
            "properties": {
                "param": {"type": "string", "description": "Parameter description"}
            },
            "required": ["param"]
        }
    }
]
```

### Vision Model Usage
For image analysis with GLM-4.5V:
- Use main endpoint (not coding endpoint)
- Encode images as base64
- Format messages with mixed content types
- Model: `"glm-4.5v"` (note the 'v' suffix)

## Model Specifications

| Model | Context | Pricing (Input/Output per 1M tokens) | Features |
|-------|---------|-------------------------------------|----------|
| GLM-4.6 | 128K | $0.6 / $2.2 | Latest flagship, best performance |
| GLM-4.5 | 96K | $0.6 / $2.2 | High performance |
| GLM-4.5V | 16K | $0.6 / $1.8 | Vision/image analysis |
| GLM-4.5-Air | 128K | $0.2 / $1.1 | Cost-efficient |
| GLM-4.5-Flash | 128K | Free / Free | Free model with all features |

## Environment Variables

- `ZAI_API_KEY` - Required for all API calls
- Stored in `.env` file (not committed to version control)
- Use `.env.example` as template

## Common API Parameters

- `temperature` (0-2): Controls randomness
- `max_tokens`: Maximum response length
- `stream`: Enable streaming responses
- `top_p`: Nucleus sampling (alternative to temperature)

## Platform-Specific Notes

### Windows Compatibility
- Unicode characters avoided in print statements
- Standard Python libraries used for cross-platform compatibility

### Dependencies
- `openai>=1.0.0` - OpenAI SDK for API communication
- `python-dotenv>=1.0.0` - Environment variable management

## Security Considerations

- Never hardcode API keys in code
- Use environment variables exclusively
- `.env` file should be in `.gitignore`
- API keys follow format: `hash.keyhash` (both parts required)