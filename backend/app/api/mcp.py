"""
MCP Management HTTP Endpoints
RESTful API for managing MCP servers in the Z.ai chatbot system
"""

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import asyncio
from pathlib import Path

# Import MCP Manager
from app.core.mcp_manager import mcp_manager

router = APIRouter()

MAX_MCP_FILE_BYTES = 5 * 1024 * 1024  # 5 MB per file
MAX_MCP_FILES = 20

# Pydantic Models
class MCPFile(BaseModel):
    path: str = Field(..., description="Relative file path under working_directory")
    content: str = Field(..., description="UTF-8 text content to write")


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
    files: Optional[List[MCPFile]] = Field(default=None, description="Optional files to create under working_directory")

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
    created_at: float  # Convert DateTime to Unix timestamp
    updated_at: float  # Convert DateTime to Unix timestamp
    command: Optional[str] = None
    arguments: Optional[List[str]] = None
    environment: Optional[Dict[str, str]] = None
    working_directory: Optional[str] = None
    health_check_interval: Optional[int] = None

class ServerActionResponse(BaseModel):
    success: bool
    message: str
    process_id: Optional[int] = None

# MCP Management Endpoints

@router.get("/servers", response_model=List[MCPServerResponse])
async def list_servers(
    status: Optional[str] = Query(None, description="Filter by status (running, stopped, error)"),
    enabled: Optional[bool] = Query(None, description="Filter by enabled status")
):
    """List all MCP servers with optional filters"""
    servers = mcp_manager.list_servers()
    
    # Apply filters
    if status:
        servers = [s for s in servers if s.get("status") == status]
    if enabled is not None:
        servers = [s for s in servers if s.get("enabled") == enabled]
    
    return [MCPServerResponse(**server) for server in servers]

@router.post("/servers", response_model=Dict[str, Any])
async def add_server(server_config: MCPServerCreate):
    """Add a new MCP server"""
    working_dir = _resolve_working_dir(server_config.working_directory)

    if server_config.files:
        _write_files(working_dir, server_config.files)

    payload = server_config.dict()
    payload.pop("files", None)
    payload["working_directory"] = str(working_dir)

    result = mcp_manager.add_server(payload)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    # Auto-start if enabled
    if server_config.enabled and server_config.auto_start:
        start_result = await mcp_manager.start_server(result["server_id"])
        if not start_result["success"]:
            result["message"] += f". Warning: Auto-start failed: {start_result['error']}"
    
    return result

@router.get("/servers/{server_id}", response_model=MCPServerResponse)
async def get_server(server_id: str):
    """Get detailed information about a specific MCP server"""
    server_info = mcp_manager.get_server(server_id)
    
    if not server_info:
        raise HTTPException(status_code=404, detail=f"MCP server '{server_id}' not found")
    
    return MCPServerResponse(**server_info)

@router.put("/servers/{server_id}", response_model=Dict[str, Any])
async def update_server(server_id: str, updates: MCPServerUpdate):
    """Update an existing MCP server configuration"""
    # Filter out None values
    update_data = {k: v for k, v in updates.dict().items() if v is not None}
    
    result = mcp_manager.update_server(server_id, update_data)
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result

@router.delete("/servers/{server_id}", response_model=Dict[str, Any])
async def delete_server(server_id: str):
    """Delete an MCP server"""
    result = mcp_manager.delete_server(server_id)
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result

# Server Control Endpoints

@router.post("/servers/{server_id}/start", response_model=ServerActionResponse)
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

@router.post("/servers/{server_id}/stop", response_model=ServerActionResponse)
async def stop_server(server_id: str):
    """Stop an MCP server"""
    result = mcp_manager.stop_server(server_id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return ServerActionResponse(success=result["success"], message=result["message"])

@router.post("/servers/{server_id}/restart", response_model=ServerActionResponse)
async def restart_server(server_id: str):
    """Restart an MCP server"""
    try:
        stop_result = mcp_manager.stop_server(server_id)
        
        if not stop_result["success"] and "already stopped" not in stop_result.get("error", ""):
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

@router.post("/start-all", response_model=Dict[str, Any])
async def start_all_enabled_servers():
    """Start all enabled servers with auto_start enabled"""
    result = await mcp_manager.start_all_enabled()
    
    return result

@router.post("/stop-all", response_model=Dict[str, Any])
async def stop_all_servers():
    """Stop all running MCP servers"""
    # Implementation logic moved entirely to API for now as manager only has start_all
    running = mcp_manager.get_running_servers()
    stopped_count = 0
    failed = []
    
    for server_id in running:
        result = mcp_manager.stop_server(server_id)
        if result["success"]:
            stopped_count += 1
        else:
            failed.append(f"{server_id}: {result.get('error', 'Unknown error')}")
    
    return {
        "success": len(failed) == 0,
        "stopped_count": stopped_count,
        "failed_servers": failed,
        "message": f"Stopped {stopped_count} servers" + (f", {len(failed)} failed" if failed else "")
    }

# Status and Info

@router.get("/status", response_model=Dict[str, Any])
async def get_mcp_status():
    """Get overall MCP system status"""
    servers = mcp_manager.list_servers()
    running = [s for s in servers if s.get("status") == "running"]
    enabled = [s for s in servers if s.get("enabled")]
    stopped = [s for s in servers if s.get("status") == "stopped"]
    error = [s for s in servers if s.get("status") == "error"]
    
    # Calculate actual tool count from running servers
    total_tools = 0
    for server in running:
        try:
            # Estimate tool count based on server type
            if 'filesystem' in server.get('name', '').lower():
                total_tools += 4  # list_files, read_file, search_code, analyze_file_structure
            elif 'database' in server.get('name', '').lower():
                total_tools += 3  # query_sql, get_schema, list_tables
            elif 'git' in server.get('name', '').lower():
                total_tools += 3  # git_status, git_diff, git_log
            elif 'fetch' in server.get('name', '').lower():
                total_tools += 2  # fetch_url, http_request
            else:
                total_tools += 2  # Default estimate
        except:
            pass
    
    return {
        "total_servers": len(servers),
        "running_servers": len(running),
        "enabled_servers": len(enabled),
        "stopped_servers": len(stopped),
        "error_servers": len(error),
        "total_tools": total_tools
    }

@router.get("/health")
async def health_check():
    """Detailed health check of MCP system"""
    servers = mcp_manager.list_servers()
    running = [s for s in servers if s.get("status") == "running"]
    enabled = [s for s in servers if s.get("enabled")]
    
    return {
        "status": "healthy",
        "mcp_manager": "running",
        "servers": {
            "total": len(servers),
            "running": len(running),
            "enabled": len(enabled)
        }
    }


# Helpers
def _resolve_working_dir(working_directory: Optional[str]) -> Path:
    base = Path.cwd()
    if working_directory:
        wd = Path(working_directory)
        if not wd.is_absolute():
            wd = base / wd
    else:
        wd = base
    return wd.resolve()


def _write_files(working_dir: Path, files: List[MCPFile]):
    if len(files) > MAX_MCP_FILES:
        raise HTTPException(status_code=400, detail=f"Too many files; max {MAX_MCP_FILES}")

    working_dir.mkdir(parents=True, exist_ok=True)
    base = working_dir.resolve()

    for file in files:
        # Basic path validation: no absolute paths
        if Path(file.path).is_absolute():
            raise HTTPException(status_code=400, detail=f"File path must be relative: {file.path}")

        target = (working_dir / file.path).resolve()
        try:
            target.relative_to(base)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"File path escapes working_directory: {file.path}")

        # Size validation
        size_bytes = len(file.content.encode("utf-8"))
        if size_bytes > MAX_MCP_FILE_BYTES:
            raise HTTPException(status_code=400, detail=f"File '{file.path}' exceeds {MAX_MCP_FILE_BYTES} bytes")

        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(file.content, encoding="utf-8")
