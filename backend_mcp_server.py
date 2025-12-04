#!/usr/bin/env python3
"""
MCP-Enhanced Backend API for Z.ai Chatbot
Provides HTTP endpoints with MCP tool integration
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import sys

# Add parent directory to path for tools
sys.path.append(os.path.dirname(__file__))
from test_mcp_backend import ZaiMCPBackend

# Load environment
load_dotenv()

app = FastAPI(
    title="Z.ai MCP-Enhanced Chatbot API",
    description="Backend API with MCP tool integration for Z.ai GLM models",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MCP Backend
mcp_backend = ZaiMCPBackend()

# Pydantic models
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000

class ChatResponse(BaseModel):
    message: str
    tools_used: List[str]
    success: bool
    reasoning: Optional[str] = None

class ToolInfo(BaseModel):
    name: str
    description: str

class ToolListResponse(BaseModel):
    tools: List[ToolInfo]
    count: int

# Utility functions
def extract_user_message(messages: List[ChatMessage]) -> str:
    """Extract the last user message from conversation"""
    for msg in reversed(messages):
        if msg.role.lower() == "user":
            return msg.content
    return messages[-1].content if messages else ""

# Health endpoints
@app.get("/")
def root():
    """Health check endpoint"""
    return {"status": "healthy", "version": "2.0.0", "mcp_enabled": True}

@app.get("/health")
def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "zai_api": "connected" if os.getenv("ZAI_API_KEY") else "missing_key",
        "mcp_tools": len(mcp_backend.available_tools),
        "backend": "mcp_enhanced"
    }

# Tool management endpoints
@app.get("/api/v1/tools", response_model=ToolListResponse)
def list_available_tools():
    """List all available MCP tools"""
    tools = [
        ToolInfo(
            name=tool["function"]["name"],
            description=tool["function"]["description"]
        )
        for tool in mcp_backend.available_tools
    ]
    
    return ToolListResponse(
        tools=tools,
        count=len(tools)
    )

@app.get("/api/v1/tools/{tool_name}")
def get_tool_info(tool_name: str):
    """Get information about a specific tool"""
    for tool in mcp_backend.available_tools:
        if tool["function"]["name"] == tool_name:
            return tool["function"]
    
    raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")

# Chat endpoints
@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat_with_mcp(request: ChatRequest):
    """Process chat message with MCP tool integration"""
    try:
        # Extract user message
        user_message = extract_user_message(request.messages)
        
        if not user_message.strip():
            raise HTTPException(status_code=400, detail="Empty user message")
        
        # Process with MCP backend
        result = mcp_backend.process_message(user_message)
        
        return ChatResponse(
            message=result["response"],
            tools_used=result["tools_used"],
            success=result["success"],
            reasoning=result["response"][:200] if result["success"] else None
        )
        
    except Exception as e:
        return ChatResponse(
            message=f"Error processing request: {str(e)}",
            tools_used=[],
            success=False
        )

@app.post("/api/v1/chat/simple")
async def simple_chat(message: str):
    """Simple chat endpoint for quick testing"""
    try:
        result = mcp_backend.process_message(message)
        
        return {
            "response": result["response"],
            "tools_used": result["tools_used"],
            "success": result["success"]
        }
    
    except Exception as e:
        return {
            "response": f"Error: {str(e)}",
            "tools_used": [],
            "success": False
        }

# Tool execution endpoints
@app.post("/api/v1/tools/execute")
async def execute_tool(tool_name: str, arguments: Dict[str, Any]):
    """Execute a specific MCP tool directly"""
    try:
        result = mcp_backend.execute_mcp_tool(tool_name, arguments)
        
        return {
            "tool": tool_name,
            "arguments": arguments,
            "result": result,
            "success": True
        }
    
    except Exception as e:
        return {
            "tool": tool_name,
            "arguments": arguments,
            "result": f"Error: {str(e)}",
            "success": False
        }

# Information endpoints
@app.get("/api/v1/info")
def get_api_info():
    """Get API information and capabilities"""
    return {
        "api_version": "2.0.0",
        "features": [
            "MCP tool integration",
            "File system operations",
            "Code search and analysis",
            "Context-aware chat",
            "Z.ai GLM-4.6 integration"
        ],
        "available_tools": len(mcp_backend.available_tools),
        "model": "glm-4.6",
        "endpoint": "https://api.z.ai/api/coding/paas/v4",
        "project_directory": os.getcwd()
    }

# Demo endpoints
@app.get("/api/v1/demo")
async def demo_mcp_features():
    """Demonstrate MCP capabilities"""
    demo_results = {}
    
    # Test 1: List files
    result1 = mcp_backend.execute_mcp_tool("list_directory", {"path": ".", "pattern": "*.py"})
    demo_results["file_listing"] = result1[:200] + "..." if len(result1) > 200 else result1
    
    # Test 2: Read demo file
    demo_results["file_reading"] = "Demo: File reading capability available"
    
    # Test 3: Search demo
    result3 = mcp_backend.execute_mcp_tool("search_code", {"pattern": "import", "file_pattern": "*.py"})
    demo_results["code_search"] = result3[:200] + "..." if len(result3) > 200 else result3
    
    return {
        "message": "MCP Demo Results",
        "features": demo_results,
        "status": "mcp_integration_working"
    }

if __name__ == "__main__":
    import uvicorn
    
    # Check configuration
    if not os.getenv("ZAI_API_KEY"):
        print("WARNING: ZAI_API_KEY not configured. Please set up your .env file.")
    
    print("Starting Z.ai MCP-Enhanced Backend...")
    print(f"MCP tools available: {len(mcp_backend.available_tools)}")
    print("Available endpoints:")
    print("  GET  / - Health check")
    print("  GET  /api/v1/info - API information")
    print("  GET  /api/v1/tools - List available tools")
    print("  POST /api/v1/chat - Chat with MCP integration")
    print("  POST /api/v1/chat/simple - Simple chat endpoint")
    print("  POST /api/v1/tools/execute - Execute tool directly")
    print("  GET  /api/v1/demo - Demo MCP features")
    
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
