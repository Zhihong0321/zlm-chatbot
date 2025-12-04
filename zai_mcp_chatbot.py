#!/usr/bin/env python3
"""
Z.ai Chatbot with MCP Integration
Integrates Z.ai API with File System MCP Server
"""

import os
import sys
import json
import asyncio
import subprocess
from typing import Dict, List, Any
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

class MCPEnabledZAIChatbot:
    """Z.ai Chatbot with MCP Server Integration"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("ZAI_API_KEY"),
            base_url="https://api.z.ai/api/coding/paas/v4"
        )
        self.mcp_process = None
        self.connected_tools = []
        
    async def start_mcp_server(self):
        """Start the MCP file server"""
        try:
            print("Starting MCP File Server...")
            
            # Start MCP server as subprocess
            cmd = [sys.executable, "mcp_file_server.py"]
            self.mcp_process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0
            )
            
            # Initialize MCP connection
            await self.initialize_mcp_connection()
            print("PASS: MCP Server started successfully")
            return True
            
        except Exception as e:
            print(f"Failed to start MCP server: {e}")
            return False
    
    async def initialize_mcp_connection(self):
        """Initialize MCP connection and discover tools"""
        # Send initialization message
        init_msg = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "zai-chatbot",
                    "version": "1.0.0"
                }
            }
        }
        
        # Send to MCP server
        if self.mcp_process and self.mcp_process.stdin:
            self.mcp_process.stdin.write(json.dumps(init_msg) + "\n")
            self.mcp_process.stdin.flush()
            
            # Read response
            response = self.mcp_process.stdout.readline()
            if response:
                response_data = json.loads(response.strip())
                print(f"MCP Connected: {response_data.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')}")
            
            # Discover available tools
            tools_msg = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            self.mcp_process.stdin.write(json.dumps(tools_msg) + "\n")
            self.mcp_process.stdin.flush()
            
            tools_response = self.mcp_process.stdout.readline()
            if tools_response:
                tools_data = json.loads(tools_response.strip())
                self.connected_tools = tools_data.get('result', {}).get('tools', [])
                print(f"Discovered {len(self.connected_tools)} MCP tools:")
                for tool in self.connected_tools:
                    print(f"  - {tool['name']}: {tool['description']}")
    
    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Call an MCP server tool"""
        try:
            tool_msg = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            if self.mcp_process and self.mcp_process.stdin:
                self.mcp_process.stdin.write(json.dumps(tool_msg) + "\n")
                self.mcp_process.stdin.flush()
                
                # Read response
                response = self.mcp_process.stdout.readline()
                if response:
                    response_data = json.loads(response.strip())
                    
                    if 'error' in response_data:
                        return f"Error: {response_data['error']}"
                    
                    result = response_data.get('result', {})
                    if 'content' in result:
                        content_list = result['content']
                        if content_list:
                            return content_list[0].get('text', 'No content returned')
                
                return "Tool call failed - no response received"
            
        except Exception as e:
            return f"Error calling tool {tool_name}: {str(e)}"
    
    def create_openai_tools(self) -> List[Dict[str, Any]]:
        """Convert MCP tools to OpenAI function format"""
        openai_tools = []
        
        for tool in self.connected_tools:
            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["inputSchema"]
                }
            }
            openai_tools.append(openai_tool)
        
        return openai_tools
    
    async def chat_with_mcp(self, user_message: str) -> str:
        """Chat with Z.ai using MCP tools"""
        try:
            # Setup conversation
            messages = [
                {
                    "role": "system",
                    "content": f"""You are a helpful AI assistant with access to file system tools. 
You can help users analyze code, read files, and explore the project structure.

Available MCP tools:
{chr(10).join(f"- {tool['name']}: {tool['description']}" for tool in self.connected_tools)}

When users ask you to analyze files, read code, or explore the project, use the available tools to provide accurate information."""
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]
            
            # Get OpenAI tools from MCP
            openai_tools = self.create_openai_tools()
            
            # Call Z.ai API with tools
            response = self.client.chat.completions.create(
                model="glm-4.6",
                messages=messages,
                tools=openai_tools,
                tool_choice="auto",
                temperature=0.7,
                max_tokens=1000
            )
            
            message = response.choices[0].message
            
            # Check if model wants to call tools
            if hasattr(message, 'tool_calls') and message.tool_calls:
                # Execute tool calls through MCP
                tool_results = []
                
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    try:
                        arguments = json.loads(tool_call.function.arguments)
                    except:
                        arguments = {}
                    
                    # Call MCP tool
                    result = await self.call_mcp_tool(tool_name, arguments)
                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "content": result
                    })
                
                # Add tool results to conversation
                messages.append(message)  # Assistant's tool call request
                messages.extend(tool_results)  # Tool results
                
                # Get final response
                final_response = self.client.chat.completions.create(
                    model="glm-4.6",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1000
                )
                
                return final_response.choices[0].message.content or "No response"
            
            # Check reasoning content
            if hasattr(message, 'reasoning_content') and message.reasoning_content:
                return message.reasoning_content
            
            # Regular response
            return message.content or "No response available"
            
        except Exception as e:
            return f"Error in chat: {str(e)}"
    
    async def start_interactive_chat(self):
        """Start interactive chat session"""
        print("\n" + "="*60)
        print("Z.ai Chatbot with MCP Integration")
        print("Type 'quit' or 'exit' to end the conversation")
        print("Try: 'list files', 'analyze main.py', 'search for import'")
        print("="*60 + "\n")
        
        try:
            while True:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() in ['quit', 'exit']:
                    print("Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                print("Assistant:", end=" ", flush=True)
                response = await self.chat_with_mcp(user_input)
                print(response)
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Clean up resources"""
        if self.mcp_process:
            try:
                self.mcp_process.terminate()
                self.mcp_process.wait(timeout=5)
            except:
                self.mcp_process.kill()

async def main():
    """Main function"""
    chatbot = MCPEnabledZAIChatbot()
    
    # Check API key
    if not os.getenv("ZAI_API_KEY"):
        print("Error: ZAI_API_KEY not found in environment variables")
        print("Please create a .env file with your Z.ai API key")
        return
    
    try:
        # Start MCP server
        if await chatbot.start_mcp_server():
            # Start interactive chat
            await chatbot.start_interactive_chat()
        else:
            print("Failed to initialize MCP server")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await chatbot.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
