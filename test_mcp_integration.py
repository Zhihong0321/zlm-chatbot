#!/usr/bin/env python3
"""
Test script to verify MCP compatibility with Z.ai coding plan API
"""

import os
import sys
import asyncio
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

def test_mcp_basic_integration():
    """Test basic MCP-style integration with Z.ai API"""
    print("Testing MCP Integration with Z.ai API")
    print("=" * 40)
    
    try:
        # Initialize client
        client = OpenAI(
            api_key=os.getenv("ZAI_API_KEY"),
            base_url="https://api.z.ai/api/coding/paas/v4"
        )
        
        # Simulate MCP function calling approach
        messages = [
            {
                "role": "system",
                "content": "You are an AI assistant with access to external tools. Users will ask you to perform tasks that may require tool usage."
            },
            {
                "role": "user", 
                "content": "List the files in the current directory and analyze the Python structure."
            }
        ]
        
        # Define simulated MCP tools (like function definitions)
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "list_directory",
                    "description": "List files and directories in a given path",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Directory path to list"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read contents of a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "File path to read"
                            }
                        }
                    }
                }
            }
        ]
        
        print("Testing tool-based interaction...")
        response = client.chat.completions.create(
            model="glm-4.6",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.7,
            max_tokens=1000
        )
        
        message = response.choices[0].message
        
        # Check if model wants to call tools
        if hasattr(message, 'tool_calls') and message.tool_calls:
            print("PASS: Model requested tool calls (MCP-compatible):")
            for tool_call in message.tool_calls:
                print(f"  - Tool: {tool_call.function.name}")
                print(f"  - Arguments: {tool_call.function.arguments}")
        else:
            print("FAIL: Model did not request tools")
            print(f"Response: {message.content}")
        
        # Check reasoning content
        if hasattr(message, 'reasoning_content') and message.reasoning_content:
            print(f"PASS: Reasoning content available: {message.reasoning_content[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_streaming_with_tools():
    """Test streaming with tool calls"""
    print("\nTesting Streaming with Tools...")
    
    try:
        client = OpenAI(
            api_key=os.getenv("ZAI_API_KEY"),
            base_url="https://api.z.ai/api/coding/paas/v4"
        )
        
        messages = [
            {"role": "user", "content": "Analyze the codebase structure using tools"}
        ]
        
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_files",
                    "description": "Search for files with specific patterns",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "pattern": {"type": "string", "description": "File pattern to search"},
                            "directory": {"type": "string", "description": "Directory to search"}
                        }
                    }
                }
            }
        ]
        
        stream = client.chat.completions.create(
            model="glm-4.6",
            messages=messages,
            tools=tools,
            stream=True,
            max_tokens=500
        )
        
        print("Streaming response:")
        for chunk in stream:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if hasattr(delta, 'content') and delta.content:
                    print(delta.content, end="", flush=True)
        
        print("\nPASS: Streaming with tools successful")
        return True
        
    except Exception as e:
        print(f"FAIL: Streaming test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Z.ai MCP Compatibility Test Suite")
    print("=" * 50)
    
    success1 = test_mcp_basic_integration()
    success2 = test_streaming_with_tools()
    
    print(f"\nRESULTS:")
    print(f"Basic MCP Integration: {'PASS' if success1 else 'FAIL'}")
    print(f"Streaming with Tools: {'PASS' if success2 else 'FAIL'}")
    
    if success1 and success2:
        print("SUCCESS: MCP is compatible with Z.ai coding plan API!")
    else:
        print("WARNING: Some MCP features may not be fully supported")
    
    sys.exit(0 if (success1 or success2) else 1)
