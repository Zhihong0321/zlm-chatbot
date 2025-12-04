#!/usr/bin/env python3
"""
Basic MCP Server for Z.ai Chatbot
File system and code analysis MCP server compatible with Z.ai coding plan API
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource
except ImportError as e:
    print(f"MCP packages not available: {e}")
    print("Please install: pip install mcp")
    sys.exit(1)

# Initialize MCP Server
server = Server("zai-file-system-server")

# Configuration
BASE_PATH = Path(__file__).parent.parent  # Project root
ALLOWED_PATHS = [BASE_PATH, BASE_PATH / "backend", BASE_PATH / "frontend"]

def is_safe_path(path: Path) -> bool:
    """Check if path is within allowed directories"""
    try:
        path = path.resolve()
        for allowed in ALLOWED_PATHS:
            if path.is_relative_to(allowed.resolve()):
                return True
        return False
    except (OSError, ValueError):
        return False

@server.list_resources()
async def handle_list_resources() -> List[Resource]:
    """List available resources"""
    resources = []
    
    # Add project files as resources
    for py_file in BASE_PATH.glob("*.py"):
        if is_safe_path(py_file):
            resources.append(
                Resource(
                    uri=f"file://{py_file}",
                    name=f"Python file: {py_file.name}",
                    description=f"Source code file: {py_file.name}",
                    mimeType="text/python"
                )
            )
    
    return resources

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read resource content"""
    if uri.startswith("file://"):
        file_path = Path(uri[7:])
        
        if not is_safe_path(file_path):
            raise ValueError(f"Access denied to {file_path}")
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        return file_path.read_text(encoding='utf-8')
    
    raise ValueError(f"Unsupported URI scheme: {uri}")

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available tools"""
    return [
        Tool(
            name="list_files",
            description="List files and directories in a given path",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path to list files from",
                        "default": "."
                    },
                    "pattern": {
                        "type": "string", 
                        "description": "File pattern to filter (e.g., '*.py', '*.md')",
                        "default": "*"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="read_file",
            description="Read contents of a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path to read"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="search_code",
            description="Search for text patterns in code files",
            inputSchema={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Text pattern to search for"
                    },
                    "file_pattern": {
                        "type": "string",
                        "description": "File pattern to search in (e.g., '*.py')",
                        "default": "*.py"
                    },
                    "directory": {
                        "type": "string",
                        "description": "Directory to search in",
                        "default": "."
                    }
                },
                "required": ["pattern"]
            }
        ),
        Tool(
            name="analyze_file_structure",
            description="Analyze the structure of Python files",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to Python file to analyze"
                    }
                },
                "required": ["file_path"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls"""
    
    if name == "list_files":
        path = Path(arguments.get("path", "."))
        pattern = arguments.get("pattern", "*")
        
        if not is_safe_path(path):
            return [TextContent(type="text", text=f"Error: Access denied to path '{path}'")]
        
        if not path.exists():
            return [TextContent(type="text", text=f"Error: Path '{path}' does not exist")]
        
        if not path.is_dir():
            return [TextContent(type="text", text=f"Error: '{path}' is not a directory")]
        
        files = []
        for item in path.glob(pattern):
            if is_safe_path(item):
                files.append(f"{'[DIR]' if item.is_dir() else '[FILE]'} {item.name}")
        
        files.sort()
        return [TextContent(type="text", text=f"Files in {path}:\n" + "\n".join(files))]
    
    elif name == "read_file":
        file_path = Path(arguments["path"])
        
        if not is_safe_path(file_path):
            return [TextContent(type="text", text=f"Error: Access denied to file '{file_path}'")]
        
        if not file_path.exists():
            return [TextContent(type="text", text=f"Error: File '{file_path}' does not exist")]
        
        if not file_path.is_file():
            return [TextContent(type="text", text=f"Error: '{file_path}' is not a file")]
        
        try:
            content = file_path.read_text(encoding='utf-8')
            # Limit content size to avoid overwhelming the AI
            if len(content) > 2000:
                content = content[:2000] + "\n\n... (content truncated)"
            
            return [TextContent(type="text", text=f"Content of {file_path}:\n\n{content}")]
        
        except Exception as e:
            return [TextContent(type="text", text=f"Error reading file '{file_path}': {str(e)}")]
    
    elif name == "search_code":
        pattern = arguments["pattern"]
        file_pattern = arguments.get("file_pattern", "*.py")
        directory = Path(arguments.get("directory", "."))
        
        if not is_safe_path(directory):
            return [TextContent(type="text", text=f"Error: Access denied to directory '{directory}'")]
        
        results = []
        try:
            for file_path in directory.rglob(file_pattern):
                if is_safe_path(file_path) and file_path.is_file():
                    try:
                        content = file_path.read_text(encoding='utf-8')
                        lines = content.split('\n')
                        matches = [f"Line {i+1}: {lines[i].strip()}" 
                                 for i, line in enumerate(lines) 
                                 if pattern.lower() in line.lower()]
                        
                        if matches:
                            rel_path = file_path.relative_to(BASE_PATH)
                            results.append(f"\n📁 {rel_path}")
                            results.extend(matches[:5])  # Limit matches per file
                            
                    except Exception:
                        continue
            
            if results:
                return [TextContent(type="text", text=f"Search results for '{pattern}':\n" + "\n".join(results[0:]))]
            else:
                return [TextContent(type="text", text=f"No matches found for pattern '{pattern}'")]
        
        except Exception as e:
            return [TextContent(type="text", text=f"Error searching code: {str(e)}")]
    
    elif name == "analyze_file_structure":
        file_path = Path(arguments["file_path"])
        
        if not is_safe_path(file_path):
            return [TextContent(type="text", text=f"Error: Access denied to file '{file_path}'")]
        
        if not file_path.exists() or not file_path.is_file():
            return [TextContent(type="text", text=f"Error: File '{file_path}' does not exist")]
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Basic analysis
            total_lines = len(lines)
            imports = [line.strip() for line in lines if line.strip().startswith(('import ', 'from '))]
            functions = [line.strip() for line in lines if line.strip().startswith('def ')]
            classes = [line.strip() for line in lines if line.strip().startswith('class ')]
            
            analysis = f"📊 Analysis of {file_path.name}:\n"
            analysis += f"📍 Total lines: {total_lines}\n"
            analysis += f"📦 Imports: {len(imports)}\n"
            if imports:
                analysis += "\n".join(f"  • {imp}" for imp in imports[:3])
                if len(imports) > 3:
                    analysis += f"\n  ... and {len(imports) - 3} more"
            
            analysis += f"\n🔧 Functions: {len(functions)}\n"
            if functions:
                analysis += "\n".join(f"  • {func}" for func in functions[:3])
                if len(functions) > 3:
                    analysis += f"\n  ... and {len(functions) - 3} more"
            
            analysis += f"\n🏗️  Classes: {len(classes)}\n"
            if classes:
                analysis += "\n".join(f"  • {cls}" for cls in classes[:3])
                if len(classes) > 3:
                    analysis += f"\n  ... and {len(classes) - 3} more"
            
            return [TextContent(type="text", text=analysis)]
        
        except Exception as e:
            return [TextContent(type="text", text=f"Error analyzing file '{file_path}': {str(e)}")]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """Main server function"""
    print("Starting Z.ai File System MCP Server...", file=sys.stderr)
    print(f"Base path: {BASE_PATH}", file=sys.stderr)
    print(f"Allowed paths: {ALLOWED_PATHS}", file=sys.stderr)
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped by user", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        sys.exit(1)
