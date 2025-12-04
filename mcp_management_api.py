#!/usr/bin/env python3
"""
MCP Management HTTP Endpoints
RESTful API for managing MCP servers in the Z.ai chatbot system
"""

from fastapi import FastAPI, HTTPException, Query, Body
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
import asyncio
from fastapi.middleware.cors import CORSMiddleware

# Import MCP Manager
from mcp_manager import MCPServerManager, mcp_manager

# Pydantic Models
class MCPServerCreate(BaseModel):
    name: str = Field(..., description="Server name")
    description: str = Field(..., description="Server description")
    command: str = Field(..., description="Command to start the server")
    arguments: Optional[List[str]] = Field(default_factory=list, description="Command arguments")
    environment: Optional[Dict[str, str]] = Field(default_factory=dict, description="Environment variables")
    working_directory: Optional[str] = Field(default=None, description="Working directory")
    enabled: Optional[bool] = Field(default=True, description="Whether server is enabled")
    auto_start: Optional[bool] = Field(default=True, description="Whether to auto-start server")
    health_check_interval: Optional[int] = Field(default=30, description="Health check interval in seconds")

class MCPServerUpdate(BaseModel):
    name: Optional[str] = Field(default=None, description="Server name")
    description: Optional[str] = Field(default=None, description="Server description")
    command: Optional[str] = Field(default=None, description="Command to start the server")
    arguments: Optional[List[str]] = Field(default=None, description="Command arguments")
    environment: Optional[Dict[str, str]] = Field(default=None, description="Environment variables")
    working_directory: Optional[str] = Field(default=None, description="Working directory")
    enabled: Optional[bool] = Field(default=None, description="Whether server is enabled")
    auto_start: Optional[bool] = Field(default=None, description="Whether to auto-start server")
    health_check_interval: Optional[int] = Field(default=None, description="Health check interval in seconds")

class MCPServerResponse(BaseModel):
    id: str
    name: str
    description: str
    status: str
    enabled: bool
    auto_start: bool
    process_id: Optional[int] = None
    created_at: float
    updated_at: float
    command: Optional[str] = None
    arguments: Optional[List[str]] = None
    environment: Optional[Dict[str, str]] = None
    working_directory: Optional[str] = None
    health_check_interval: Optional[int] = None

class ServerActionResponse(BaseModel):
    success: bool
    message: str
    process_id: Optional[int] = None

# Create FastAPI app
app = FastAPI(
    title="MCP Server Management API",
    description="RESTful API for managing Model Context Protocol (MCP) servers",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MCP Management Endpoints

@app.get("/")
async def root():
    """Health check and API info"""
    return {
        "status": "healthy",
        "api": "MCP Management",
        "version": "1.0.0",
        "total_servers": len(mcp_manager.servers),
        "running_servers": len(mcp_manager.get_running_servers()),
        "enabled_servers": len(mcp_manager.get_enabled_servers())
    }

@app.get("/api/v1/mcp/servers", response_model=List[MCPServerResponse])
async def list_servers(
    status: Optional[str] = Query(None, description="Filter by status (running, stopped, error)"),
    enabled: Optional[bool] = Query(None, description="Filter by enabled status")
):
    """List all MCP servers with optional filters"""
    servers = mcp_manager.list_servers()
    
    # Apply filters
    if status:
        servers = [s for s in servers if s["status"] == status]
    if enabled is not None:
        servers = [s for s in servers if s["enabled"] == enabled]
    
    return [MCPServerResponse(**server) for server in servers]

@app.post("/api/v1/mcp/servers", response_model=Dict[str, Any])
async def add_server(server_config: MCPServerCreate):
    """Add a new MCP server"""
    result = mcp_manager.add_server(server_config.dict())
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    # Auto-start if enabled
    if server_config.enabled and server_config.auto_start:
        start_result = await mcp_manager.start_server(result["server_id"])
        if not start_result["success"]:
            result["message"] += f". Warning: Auto-start failed: {start_result['error']}"
    
    return result

@app.get("/api/v1/mcp/servers/{server_id}", response_model=MCPServerResponse)
async def get_server(server_id: str):
    """Get detailed information about a specific MCP server"""
    server_info = mcp_manager.get_server(server_id)
    
    if not server_info:
        raise HTTPException(status_code=404, detail=f"MCP server '{server_id}' not found")
    
    return MCPServerResponse(**server_info)

@app.put("/api/v1/mcp/servers/{server_id}", response_model=Dict[str, Any])
async def update_server(server_id: str, updates: MCPServerUpdate):
    """Update an existing MCP server configuration"""
    # Filter out None values
    update_data = {k: v for k, v in updates.dict().items() if v is not None}
    
    result = mcp_manager.update_server(server_id, update_data)
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result

@app.delete("/api/v1/mcp/servers/{server_id}", response_model=Dict[str, Any])
async def delete_server(server_id: str):
    """Delete an MCP server"""
    result = mcp_manager.delete_server(server_id)
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result

# Server Control Endpoints

@app.post("/api/v1/mcp/servers/{server_id}/start", response_model=ServerActionResponse)
async def start_server(server_id: str):
    """Start an MCP server"""
    result = await mcp_manager.start_server(server_id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return ServerActionResponse(
        success=result["success"],
        message=result["message"],
        process_id=result.get("process_id")
    )

@app.post("/api/v1/mcp/servers/{server_id}/stop", response_model=ServerActionResponse)
async def stop_server(server_id: str):
    """Stop an MCP server"""
    result = mcp_manager.stop_server(server_id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return ServerActionResponse(success=result["success"], message=result["message"])

@app.post("/api/v1/mcp/servers/{server_id}/restart", response_model=ServerActionResponse)
async def restart_server(server_id: str):
    """Restart an MCP server"""
    # For restart, we need to handle async properly
    try:
        stop_result = mcp_manager.stop_server(server_id)
        
        if not stop_result["success"] and "already stopped" not in stop_result["error"]:
            raise HTTPException(status_code=400, detail=stop_result["error"])
        
        # Wait a moment
        await asyncio.sleep(1)
        
        # Start the server
        start_result = await mcp_manager.start_server(server_id)
        
        if not start_result["success"]:
            raise HTTPException(status_code=400, detail=start_result["error"])
        
        return ServerActionResponse(
            success=True,
            message=start_result["message"],
            process_id=start_result.get("process_id")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server restart failed: {str(e)}")

# Bulk Operations Endpoints

@app.post("/api/v1/mcp/start-all", response_model=Dict[str, Any])
async def start_all_enabled_servers():
    """Start all enabled servers with auto_start enabled"""
    result = await mcp_manager.start_all_enabled()
    
    return {
        "success": result["success"],
        "started_servers": result["started"],
        "failed_servers": result["failed"],
        "total_started": len(result["started"]),
        "total_failed": len(result["failed"]),
        "message": result["message"]
    }

@app.post("/api/v1/mcp/stop-all", response_model=Dict[str, Any])
async def stop_all_servers():
    """Stop all running MCP servers"""
    stopped_count = 0
    failed = []
    
    for server_id in list(mcp_manager.servers.keys()):
        if mcp_manager.servers[server_id].status == "running":
            result = mcp_manager.stop_server(server_id)
            if result["success"]:
                stopped_count += 1
            else:
                failed.append(f"{server_id}: {result['error']}")
    
    return {
        "success": len(failed) == 0,
        "stopped_count": stopped_count,
        "failed_servers": failed,
        "message": f"Stopped {stopped_count} servers" + (f", {len(failed)} failed" if failed else "")
    }

# Tools and Discovery Endpoints

@app.get("/api/v1/mcp/tools", response_model=List[Dict[str, Any]])
async def get_all_tools():
    """Get all available tools from running MCP servers"""
    return mcp_manager.get_tools_from_servers()

@app.get("/api/v1/mcp/servers/running", response_model=List[str])
async def get_running_servers():
    """Get list of running server IDs"""
    return mcp_manager.get_running_servers()

@app.get("/api/v1/mcp/servers/enabled", response_model=List[str])
async def get_enabled_servers():
    """Get list of enabled server IDs"""
    return mcp_manager.get_enabled_servers()

# Configuration and Status Endpoints

@app.get("/api/v1/mcp/status", response_model=Dict[str, Any])
async def get_mcp_status():
    """Get overall MCP system status"""
    return {
        "total_servers": len(mcp_manager.servers),
        "running_servers": len(mcp_manager.get_running_servers()),
        "enabled_servers": len(mcp_manager.get_enabled_servers()),
        "stopped_servers": len([s for s in mcp_manager.servers.values() if s.status == "stopped"]),
        "error_servers": len([s for s in mcp_manager.servers.values() if s.status == "error"]),
        "total_tools": len(mcp_manager.get_tools_from_servers())
    }

@app.get("/api/v1/mcp/servers/{server_id}/logs")
async def get_server_logs(server_id: str, lines: int = Query(50, description="Number of log lines to retrieve")):
    """Get logs from a specific server (if available)"""
    if server_id not in mcp_manager.servers:
        raise HTTPException(status_code=404, detail=f"Server '{server_id}' not found")
    
    config = mcp_manager.servers[server_id]
    
    # For now, return placeholder logs
    # In a real implementation, you would read from log files or stdout
    return {
        "server_id": server_id,
        "server_name": config.name,
        "status": config.status,
        "logs": [
            {
                "timestamp": "2025-01-01T00:00:00Z",
                "level": "INFO",
                "message": f"Server '{config.name}' log entry (placeholder)"
            }
        ]
    }

# Health Check Endpoint
@app.get("/api/v1/mcp/health")
async def health_check():
    """Detailed health check of MCP system"""
    return {
        "status": "healthy",
        "mcp_manager": "running",
        "servers": {
            "total": len(mcp_manager.servers),
            "running": len(mcp_manager.get_running_servers()),
            "enabled": len(mcp_manager.get_enabled_servers()),
            "healthy": len([s for s in mcp_manager.servers.values() if s.status == "running"])
        },
        "endpoints": {
            "servers": "/api/v1/mcp/servers",
            "tools": "/api/v1/mcp/tools",
            "status": "/api/v1/mcp/status"
        }
    }

# Server Templates
@app.get("/api/v1/mcp/templates", response_model=List[Dict[str, Any]])
async def get_server_templates():
    """Get predefined server templates for easy setup"""
    templates = [
        {
            "name": "File System Server",
            "description": "Local file system operations (list, read, search files)",
            "template": {
                "command": "python",
                "arguments": ["mcp_file_server.py"],
                "environment": {},
                "working_directory": os.getcwd(),
                "enabled": True,
                "auto_start": True,
                "health_check_interval": 30
            }
        },
        {
            "name": "Database Server",
            "description": "Database query and management tools",
            "template": {
                "command": "npx",
                "arguments": ["-y", "@modelcontextprotocol/server-postgres"],
                "environment": {"DATABASE_URL": "sqlite:///chatbot.db"},
                "working_directory": os.getcwd(),
                "enabled": True,
                "auto_start": True,
                "health_check_interval": 30
            }
        },
        {
            "name": "Git Server",
            "description": "Git repository operations and version control",
            "template": {
                "command": "npx",
                "arguments": ["-y", "@modelcontextprotocol/server-git"],
                "environment": {},
                "working_directory": os.getcwd(),
                "enabled": True,
                "auto_start": True,
                "health_check_interval": 30
            }
        },
        {
            "name": "Web Fetch Server",
            "description": "Web content fetching and HTTP requests",
            "template": {
                "command": "npx",
                "arguments": ["-y", "@modelcontextprotocol/server-fetch"],
                "environment": {},
                "working_directory": os.getcwd(),
                "enabled": True,
                "auto_start": True,
                "health_check_interval": 30
            }
        },
        {
            "name": "Memory Server",
            "description": "Knowledge graph and memory storage",
            "template": {
                "command": "npx",
                "arguments": ["-y", "@modelcontextprotocol/server-memory"],
                "environment": {},
                "working_directory": os.getcwd(),
                "enabled": True,
                "auto_start": True,
                "health_check_interval": 30
            }
        }
    ]
    
    return templates

# Error Handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Not found", "detail": exc.detail}

@app.exception_handler(400)
async def bad_request_handler(request, exc):
    return {"error": "Bad request", "detail": exc.detail}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "Internal server error", "detail": str(exc)}

if __name__ == "__main__":
    import uvicorn
    
    print("Starting MCP Management API Server...")
    print("Available endpoints:")
    print("  GET  /api/v1/mcp/servers - List servers")
    print("  POST /api/v1/mcp/servers - Add server")
    print("  GET  /api/v1/mcp/servers/{id} - Get server details")
    print("  PUT  /api/v1/mcp/servers/{id} - Update server")
    print("  DELETE /api/v1/mcp/servers/{id} - Delete server")
    print("  POST /api/v1/mcp/servers/{id}/start - Start server")
    print("  POST /api/v1/mcp/servers/{id}/stop - Stop server")
    print("  POST /api/v1/mcp/servers/{id}/restart - Restart server")
    print("  POST /api/v1/mcp/start-all - Start all enabled")
    print("  POST /api/v1/mcp/stop-all - Stop all")
    print("  GET  /api/v1/mcp/tools - Get all tools")
    print("  GET  /api/v1/mcp/status - System status")
    print("  GET  /api/v1/mcp/templates - Server templates")
    
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
