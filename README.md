# Z.ai Chatbot Examples

This project contains example chatbots powered by Z.ai's GLM models, demonstrating different integration approaches and capabilities.

## Quick Start

1. **Run the setup script:**
   ```bash
   python setup.py
   ```
   This will install dependencies and create the .env file.

2. **Get your API key:**
   - Visit [Z.ai API Console](https://z.ai/manage-apikey/apikey-list)
   - Copy your API key

3. **Configure the environment:**
   - Edit the `.env` file
   - Replace `your_zai_api_key_here` with your actual API key

4. **Test your connection:**
   ```bash
   python test_connection.py
   ```

5. **Run a chatbot:**
   ```bash
   python zai_chatbot.py  # Basic chatbot
   ```

## Important: Coding Endpoint

For unlimited access without balance requirements, this project uses Z.ai's coding endpoint:
- **Endpoint**: `https://api.z.ai/api/coding/paas/v4`
- **Models Available**: GLM-4.6, GLM-4.5, GLM-4.5V, GLM-4.5-Air
- **Special Feature**: Responses include reasoning content with detailed thinking process
- **No Balance Required**: Works with 0 balance accounts

## Manual Setup

If you prefer to set up manually:

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up your API key:**
   - Create a `.env` file in this directory:
   ```
   ZAI_API_KEY=your_zai_api_key_here
   ```
   (You can copy `.env.example` to `.env` and fill in your key)

## Examples

### 1. Basic Chatbot (`zai_chatbot.py`)

A simple interactive chatbot using Z.ai's GLM-4.6 model with conversation history.

```bash
python zai_chatbot.py
```

Features:
- Conversation history persistence
- Basic error handling
- Clean, simple interface

### 2. Advanced Chatbot (`advanced_zai_chatbot.py`)

An enhanced version demonstrating streaming responses and function calling.

```bash
python advanced_zai_chatbot.py
```

Features:
- Real-time streaming responses
- Function calling (weather API example)
- More sophisticated conversation handling
- Better error handling

## Available Models

You can use any of these models by changing the `model` parameter in the code:

- `glm-4.6` - Latest flagship model (128K context)
- `glm-4.5` - High performance model (96K context)
- `glm-4.5v` - Visual reasoning model (16K context)
- `glm-4.5-air` - Cost-efficient model
- `glm-4.5-flash` - Free model

## API Parameters

Common parameters you can adjust:

- `temperature` (0-2): Controls randomness (higher = more creative)
- `max_tokens`: Maximum response length
- `stream`: Enable/disable streaming responses
- `top_p`: Nucleus sampling (alternative to temperature)

## Function Calling

The advanced example demonstrates how to:
1. Define functions for the model to call
2. Handle function calls from the model
3. Process function results and continue conversation

## Error Handling

Both examples include basic error handling for:
- API key issues
- Network problems
- Invalid responses
- Rate limiting

### 3. Multimodal Example (`multimodal_example.py`)

Demonstrates text and vision capabilities with model testing and image analysis.

```bash
python multimodal_example.py
```

Features:
- Test multiple GLM models
- Image analysis with GLM-4.5V
- Interactive command interface
- Base64 image encoding

Commands:
- `text: <message>` - Text-only conversation
- `image: <path> <question>` - Analyze an image
- `models` - Test all available models
- `quit` - Exit

### 4. Model Comparison (`model_comparison.py`)

Compare different GLM models and get recommendations based on your use case.

```bash
python model_comparison.py
```

Features:
- Model specifications and pricing comparison
- Performance testing
- Model recommendations based on use case
- Cost estimation

### 5. Test Connection (`test_connection.py`)

Quick test to verify your API connection is working.

```bash
python test_connection.py
```

## Available Models

You can use any of these models by changing the `model` parameter in the code:

| Model | Context | Price (Input/Output per 1M tokens) | Features |
|-------|---------|-----------------------------------|----------|
| GLM-4.6 | 128K | $0.6 / $2.2 | Latest flagship, best performance |
| GLM-4.5 | 96K | $0.6 / $2.2 | High performance |
| GLM-4.5V | 16K | $0.6 / $1.8 | Vision/image analysis |
| GLM-4.5-Air | 128K | $0.2 / $1.1 | Cost-efficient |
| GLM-4.5-Flash | 128K | Free / Free | Free model with all features |

### 6. Coding Endpoint Demo (`demo_coding_chatbot.py`)

Showcase the special reasoning content feature of the coding endpoint.

```bash
python demo_coding_chatbot.py
```

Features:
- Demonstrates reasoning content extraction
- Tests multiple models
- Shows how to parse reasoning content for answers

## Next Steps

1. Try the basic chatbot first to test your connection
2. Experiment with the advanced version for more features
3. Test the multimodal example for vision capabilities
4. Use the model comparison tool to choose the right model
5. Modify the system prompt to customize the assistant's behavior
6. Add your own custom functions for your specific use case
7. Implement persistence for conversation history

## Resources

- [Z.ai API Documentation](https://docs.z.ai)
- [Z.ai API Reference](https://docs.z.ai/api-reference/introduction)
- [Z.ai Pricing](https://docs.z.ai/guides/overview/pricing)
- [Manage API Keys](https://z.ai/manage-apikey/apikey-list)
- [Check Rate Limits](https://z.ai/manage-apikey/rate-limits)