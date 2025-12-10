# AI Agent Guide — Z.ai Chatbot System

> **Don't guess — measure, ask, verify, then fix.**

This document provides operational rules and technical guidance for agents working on Z.ai GLM chatbot system.

---

## Engineering Principles

**Make it work first; simplest correct code wins.**
- No overengineering, no unnecessary abstractions
- Keep dependencies minimal, flow clear, code readable

**Root-Cause First**
- Fix symptoms last — find the real root cause first
- Validate every assumption; never guess
- If uncertain → ask me questions or add logs to get real evidence

**Debugging Discipline**
- Use logs to expose actual inputs, states, env values
- Do not add speculative fixes or silent retries
- Never hide errors — surface failures plainly

**Behavior Rules**
- No wild guessing
- No masking failures
- No fake progress or fallback behavior
- If a shortcut risks confusion/instability → reject it

---

## Project Overview

Python-based collection of chatbot examples demonstrating integration with Z.ai's GLM models (GLM-4.6, GLM-4.5, GLM-4.5V, GLM-4.5-Air, GLM-4.5-Flash). Uses OpenAI SDK with Z.ai's custom endpoints.

---

## Critical Endpoints

### Primary Endpoint (DEPLOYED ONLY)
- **URL**: `https://api.z.ai/api/coding/paas/v4` 
- **Models**: GLM-4.6, GLM-4.5, GLM-4.5V, GLM-4.5-Air
- **Features**: Provides `reasoning_content` field showing model's thinking process
- **Access**: Works with zero balance (coding plan)

### Forbidden Endpoint
- **URL**: `https://api.z.ai/api/paas/v4`
- **Status**: ❌ NEVER USE - requires balance, Error 1113
- **Risk**: Deployment failure, service interruption

---

## Core Workflow

**When debugging:**
1. Understand the problem
2. Identify unknowns  
3. Ask questions / add logs
4. Verify root cause
5. Apply smallest correct fix
6. Re-check system behavior

**When blocked:**
- Ask targeted questions
- Present clear A/B/C investigation paths
- Do not proceed until diagnostic tree is clear

---

## Essential Commands

```bash
# Setup & Test
python setup.py                    # Install dependencies + .env creation
python test_connection.py            # Verify API connectivity

# Core Examples
python zai_chatbot.py              # Basic conversation
python advanced_zai_chatbot.py       # Streaming + function calling
python demo_coding_chatbot.py        # Reasoning content demo
python zai_coding_chatbot.py        # Coding-specific implementation

# Testing
python model_comparison.py           # Compare model performance
```

---

## Key Gotchas

### API Key Management
- **Location**: `.env` file as `ZAI_API_KEY`
- **Format**: `hash.keyhash` (both parts required)
- **Source**: https://z.ai/manage-apikey/apikey-list

### Reasoning Content Field
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

### Function Calling Implementation
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

---

## Error Handling Patterns

### Common API Errors
- **Error 1113**: Insufficient balance → Use coding endpoint
- **Network failures**: Check endpoint URL (coding vs main)
- **Invalid API key**: Verify format in `.env`

### Error Response Structure
```python
try:
    response = client.chat.completions.create(...)
    # Process response
except Exception as e:
    print(f"Error: {e}")
    # Log actual error, don't mask
```

---

## Model Specifications

| Model | Context | Pricing (Input/Output per 1M) | Features |
|--------|----------|-----------------------------------|----------|
| GLM-4.6 | 128K | $0.6 / $2.2 | Latest flagship, best performance |
| GLM-4.5 | 96K | $0.6 / $2.2 | High performance |
| GLM-4.5V | 16K | $0.6 / $1.8 | Vision/image analysis |
| GLM-4.5-Air | 128K | $0.2 / $1.1 | Cost-efficient |
| GLM-4.5-Flash | 128K | Free / Free | Free model with all features |

---

## Environment Variables

```bash
ZAI_API_KEY=your_api_key_here         # Required for all API calls
DATABASE_URL=your_db_connection      # Auto-provided by Railway
PORT=8000                          # Railway-provided port
```

---

## Deployment Rules

**Railway Environment:**
- All endpoints run on port 8000
- MCP endpoints integrated: `/api/v1/mcp/*`
- Database: Railway PostgreSQL (auto-configured)
- Frontend: Served via FastAPI static files

**Critical Errors to Avoid:**
- Never use main endpoint (requires balance)
- Never hardcode localhost:8001 (integrated now)
- Never assume environment variables are set

---

## Testing Discipline

**Before any fix:**
1. Reproduce the issue consistently
2. Check logs for actual error patterns
3. Verify environment variables and endpoint URLs
4. Test with minimal example first

**After any fix:**
1. Verify the original issue is resolved
2. Check for new side effects
3. Run related test cases
4. Update documentation if behavior changed

---

**One-Line Summary**
*"Make it work, keep it simple, measure everything, fix the root cause."*
