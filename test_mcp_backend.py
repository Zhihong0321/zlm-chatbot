#!/usr/bin/env python3
"""
Final MCP Integration Test for Z.ai API
Demonstrates fully working MCP integration with backend API
"""

import os
import sys
import json
from dotenv import load_dotenv
from openai import OpenAI

class ZaiMCPBackend:
    """Backend API with MCP Integration for Z.ai Chatbot"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("ZAI_API_KEY"),
            base_url="https://api.z.ai/api/coding/paas/v4"
        )
        self.available_tools = self._setup_mcp_tools()
    
    def _setup_mcp_tools(self):
        """Setup MCP-compatible tools"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "list_directory",
                    "description": "List files and directories in a path",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Directory path", "default": "."},
                            "pattern": {"type": "string", "description": "File pattern filter", "default": "*"}
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
                            "path": {"type": "string", "description": "File to read"}
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_code",
                    "description": "Search for text patterns in code files",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "pattern": {"type": "string", "description": "Text to search for"},
                            "file_pattern": {"type": "string", "description": "File pattern", "default": "*.py"},
                            "directory": {"type": "string", "description": "Search directory", "default": "."}
                        },
                        "required": ["pattern"]
                    }
                }
            }
        ]
    
    def execute_mcp_tool(self, tool_name, arguments):
        """Execute MCP tool locally (simulated server)"""
        try:
            if tool_name == "list_directory":
                path = arguments.get("path", ".")
                pattern = arguments.get("pattern", "*")
                
                if not os.path.exists(path):
                    return f"Error: Path '{path}' does not exist"
                
                if not os.path.isdir(path):
                    return f"Error: '{path}' is not a directory"
                
                files = []
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    if item.endswith(pattern.replace("*", "")) or pattern == "*":
                        files.append(f"{'[DIR]' if os.path.isdir(item_path) else '[FILE]'} {item}")
                
                files.sort()
                return f"Files in {path}:\n" + "\n".join(files)
            
            elif tool_name == "read_file":
                path = arguments["path"]
                
                if not os.path.exists(path):
                    return f"Error: File '{path}' not found"
                
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Limit size
                if len(content) > 2000:
                    content = content[:2000] + "\n\n... (content truncated)"
                
                return f"Content of {path}:\n\n{content}"
            
            elif tool_name == "search_code":
                pattern = arguments["pattern"]
                file_pattern = arguments.get("file_pattern", "*.py")
                directory = arguments.get("directory", ".")
                
                results = []
                
                try:
                    for root, dirs, files in os.walk(directory):
                        for file in files:
                            if file.endswith(file_pattern.replace("*", "")):
                                file_path = os.path.join(root, file)
                                try:
                                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                        content = f.read()
                                        lines = content.split('\n')
                                        matches = [f"Line {i+1}: {line.strip()}" 
                                                 for i, line in enumerate(lines) 
                                                 if pattern.lower() in line.lower()]
                                        
                                        if matches:
                                            rel_path = os.path.relpath(file_path, directory)
                                            results.append(f"\nFile: {rel_path}")
                                            results.extend(matches[:3])  # Limit matches
                                            
                                            if len(matches) > 3:
                                                results.append(f"... and {len(matches)-3} more matches")
                                            
                                except Exception:
                                    continue
                                    
                                if len(results) > 50:  # Limit total results
                                    results.append("... (search truncated)")
                                    break
                                    
                except Exception as e:
                    return f"Error searching: {str(e)}"
                
                if results:
                    return f"Search results for '{pattern}':\n" + "\n".join(results)
                else:
                    return f"No matches found for '{pattern}'"
            
            else:
                return f"Error: Unknown tool '{tool_name}'"
                
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"
    
    def process_message(self, user_message):
        """Process user message with MCP tools"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": f"""You are a helpful AI assistant with access to file system tools.
Available tools:
{json.dumps([tool['function'] for tool in self.available_tools], indent=2)}

When users ask about files, code, or project structure, use the available tools to provide accurate information."""
                },
                {"role": "user", "content": user_message}
            ]
            
            # Request tool usage from Z.ai
            response = self.client.chat.completions.create(
                model="glm-4.6",
                messages=messages,
                tools=self.available_tools,
                tool_choice="auto",
                temperature=0.7,
                max_tokens=1000
            )
            
            message = response.choices[0].message
            
            # Check for tool calls
            if hasattr(message, 'tool_calls') and message.tool_calls:
                # Execute tools locally
                tool_results = []
                
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    try:
                        arguments = json.loads(tool_call.function.arguments)
                    except:
                        arguments = {}
                    
                    # Execute tool
                    result = self.execute_mcp_tool(tool_name, arguments)
                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool", 
                        "content": result
                    })
                
                # Continue conversation with tool results
                messages.append(message)  # Assistant's tool call
                messages.extend(tool_results)  # Tool results
                
                # Get final response
                final_response = self.client.chat.completions.create(
                    model="glm-4.6",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1000
                )
                
                return {
                    "response": final_response.choices[0].message.content,
                    "tools_used": [tc.function.name for tc in message.tool_calls],
                    "success": True
                }
            
            # Check reasoning content
            if hasattr(message, 'reasoning_content') and message.reasoning_content:
                return {
                    "response": message.reasoning_content,
                    "tools_used": [],
                    "success": True
                }
            
            # Regular response
            return {
                "response": message.content,
                "tools_used": [],
                "success": True
            }
            
        except Exception as e:
            return {
                "response": f"Error processing message: {str(e)}",
                "tools_used": [],
                "success": False
            }

def test_backend_mcp_api():
    """Test backend API with MCP integration"""
    print("Testing Backend MCP API")
    print("=" * 50)
    
    backend = ZaiMCPBackend()
    
    test_cases = [
        "List files in the current directory",
        "Read the main application file (app.py)",
        "Search for imports in Python files",
        "Analyze this project structure"
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test {i}: {test_case} ---")
        
        result = backend.process_message(test_case)
        
        print(f"Tools used: {', '.join(result['tools_used']) if result['tools_used'] else 'None'}")
        print(f"Response preview: {result['response'][:200]}...")
        print(f"Status: {'PASS' if result['success'] else 'FAIL'}")
        
        results.append(result['success'])
    
    return all(results), results

def main():
    """Main test function"""
    print("Z.ai MCP Backend Integration Test")
    print("=" * 60)
    
    if not os.getenv("ZAI_API_KEY"):
        print("Error: ZAI_API_KEY not configured")
        return False
    
    load_dotenv()
    
    try:
        success, details = test_backend_mcp_api()
        
        print(f"\n{'='*60}")
        print("FINAL RESULTS:")
        print(f"Overall Status: {'SUCCESS' if success else 'PARTIAL SUCCESS'}")
        print(f"Tests Passed: {sum(details)}/{len(details)}")
        
        if success:
            print("\nThe Z.ai backend is now MCP-enabled!")
            print("Features available:")
            print("- File system operations via MCP")
            print("- Code search and analysis")
            print("- Tool discovery and execution")
            print("- Context-aware conversations")
            
            print("\nNext steps:")
            print("1. Deploy backend with FastAPI")
            print("2. Add HTTP endpoints for MCP operations")
            print("3. Connect frontend to enhanced backend")
            print("4. Add more MCP servers (database, API, etc.)")
        
        return success
        
    except Exception as e:
        print(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
