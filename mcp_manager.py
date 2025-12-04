#!/usr/bin/env python3
"""
MCP Server Management System
Provides full CRUD operations for MCP servers in the Z.ai chatbot system
"""

import json
import os
import subprocess
import asyncio
import uuid
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import time

@dataclass
class MCPServerConfig:
    """MCP Server Configuration"""
    id: str
    name: str
    description: str
    command: str
    arguments: List[str]
    environment: Dict[str, str]
    working_directory: Optional[str] = None
    enabled: bool = True
    auto_start: bool = True
    health_check_interval: int = 30
    created_at: float = None
    updated_at: float = None
    process_id: Optional[int] = None
    status: str = "stopped"  # running, stopped, error, starting
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()
        if self.updated_at is None:
            self.updated_at = time.time()

class MCPServerManager:
    """Manages MCP servers lifecycle and configuration"""
    
    def __init__(self, config_file: str = "mcp_servers.json"):
        self.config_file = Path(config_file)
        self.servers: Dict[str, MCPServerConfig] = {}
        self.processes: Dict[str, subprocess.Popen] = {}
        self.health_check_tasks: Dict[str, asyncio.Task] = {}
        
        # Initialize with default servers
        self._load_servers()
        
    def _load_servers(self):
        """Load server configurations from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    for server_data in data.get('servers', []):
                        config = MCPServerConfig(**server_data)
                        self.servers[config.id] = config
                print(f"Loaded {len(self.servers)} MCP server configurations")
            except Exception as e:
                print(f"Error loading MCP servers: {e}")
                self.servers = {}
        else:
            # Create default configuration
            self._create_default_servers()
            
    def _create_default_servers(self):
        """Create default MCP server configurations"""
        default_servers = [
            MCPServerConfig(
                id="filesystem-1",
                name="File System Server",
                description="Local file system operations (list, read, search)",
                command="python",
                arguments=["mcp_file_server.py"],
                environment={},
                working_directory=os.getcwd()
            ),
            MCPServerConfig(
                id="database-1", 
                name="Database Server",
                description="Database query and management tools",
                command="npx",
                arguments=["-y", "@modelcontextprotocol/server-postgres"],
                environment={"DATABASE_URL": "sqlite:///chatbot.db"},
                working_directory=os.getcwd()
            ),
            MCPServerConfig(
                id="git-1",
                name="Git Server", 
                description="Git repository operations and file version control",
                command="npx",
                arguments=["-y", "@modelcontextprotocol/server-git"],
                environment={},
                working_directory=os.getcwd()
            ),
            MCPServerConfig(
                id="web-fetch-1",
                name="Web Fetch Server",
                description="Web content fetching and HTTP requests",
                command="npx", 
                arguments=["-y", "@modelcontextprotocol/server-fetch"],
                environment={},
                working_directory=os.getcwd()
            )
        ]
        
        for server in default_servers:
            self.servers[server.id] = server
            
        self._save_servers()
        print(f"Created {len(default_servers)} default MCP server configurations")
    
    def _save_servers(self):
        """Save server configurations to file"""
        try:
            data = {
                "servers": [asdict(server) for server in self.servers.values()],
                "last_updated": time.time()
            }
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving MCP servers: {e}")
    
    # CRUD Operations
    def list_servers(self) -> List[Dict[str, Any]]:
        """List all MCP servers with their status"""
        servers_info = []
        for server_id, config in self.servers.items():
            servers_info.append({
                "id": server_id,
                "name": config.name,
                "description": config.description,
                "status": config.status,
                "enabled": config.enabled,
                "auto_start": config.auto_start,
                "process_id": config.process_id,
                "created_at": config.created_at,
                "updated_at": config.updated_at
            })
        return servers_info
    
    def add_server(self, server_config: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new MCP server"""
        try:
            # Generate unique ID if not provided
            if 'id' not in server_config:
                server_config['id'] = str(uuid.uuid4())
            
            server_id = server_config['id']
            
            if server_id in self.servers:
                return {"success": False, "error": f"Server with ID '{server_id}' already exists"}
            
            # Validate required fields
            required_fields = ['name', 'description', 'command']
            for field in required_fields:
                if field not in server_config:
                    return {"success": False, "error": f"Missing required field: {field}"}
            
            # Create server configuration
            config = MCPServerConfig(
                id=server_config['id'],
                name=server_config['name'],
                description=server_config['description'],
                command=server_config['command'],
                arguments=server_config.get('arguments', []),
                environment=server_config.get('environment', {}),
                working_directory=server_config.get('working_directory'),
                enabled=server_config.get('enabled', True),
                auto_start=server_config.get('auto_start', True),
                health_check_interval=server_config.get('health_check_interval', 30)
            )
            
            self.servers[server_id] = config
            self._save_servers()
            
            return {
                "success": True,
                "server_id": server_id,
                "message": f"MCP server '{config.name}' added successfully"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_server(self, server_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific server"""
        if server_id not in self.servers:
            return None
        
        config = self.servers[server_id]
        return {
            "id": config.id,
            "name": config.name,
            "description": config.description,
            "command": config.command,
            "arguments": config.arguments,
            "environment": config.environment,
            "working_directory": config.working_directory,
            "enabled": config.enabled,
            "auto_start": config.auto_start,
            "health_check_interval": config.health_check_interval,
            "status": config.status,
            "process_id": config.process_id,
            "created_at": config.created_at,
            "updated_at": config.updated_at
        }
    
    def update_server(self, server_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing MCP server configuration"""
        try:
            if server_id not in self.servers:
                return {"success": False, "error": f"Server '{server_id}' not found"}
            
            config = self.servers[server_id]
            
            # Update allowed fields
            updatable_fields = [
                'name', 'description', 'command', 'arguments', 
                'environment', 'working_directory', 'enabled', 
                'auto_start', 'health_check_interval'
            ]
            
            for field in updatable_fields:
                if field in updates:
                    setattr(config, field, updates[field])
            
            config.updated_at = time.time()
            self._save_servers()
            
            return {
                "success": True,
                "message": f"MCP server '{config.name}' updated successfully"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_server(self, server_id: str) -> Dict[str, Any]:
        """Delete an MCP server"""
        try:
            if server_id not in self.servers:
                return {"success": False, "error": f"Server '{server_id}' not found"}
            
            # Stop server if running
            self.stop_server(server_id)
            
            server_name = self.servers[server_id].name
            del self.servers[server_id]
            
            self._save_servers()
            
            return {
                "success": True,
                "message": f"MCP server '{server_name}' deleted successfully"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Server Lifecycle Management
    async def start_server(self, server_id: str) -> Dict[str, Any]:
        """Start an MCP server"""
        try:
            if server_id not in self.servers:
                return {"success": False, "error": f"Server '{server_id}' not found"}
            
            config = self.servers[server_id]
            
            if not config.enabled:
                return {"success": False, "error": f"Server '{config.name}' is disabled"}
            
            if config.status == "running":
                return {"success": False, "error": f"Server '{config.name}' is already running"}
            
            config.status = "starting"
            
            # Prepare command
            cmd = [config.command] + config.arguments
            env = os.environ.copy()
            env.update(config.environment)
            
            # Start process
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                cwd=config.working_directory
            )
            
            # Wait a moment for process to initialize
            await asyncio.sleep(1)
            
            if process.poll() is None:
                # Process is running
                config.process_id = process.pid
                config.status = "running"
                config.updated_at = time.time()
                self.processes[server_id] = process
                
                # Start health checking
                self._start_health_check(server_id)
                
                self._save_servers()
                
                return {
                    "success": True,
                    "message": f"MCP server '{config.name}' started successfully",
                    "process_id": process.pid
                }
            else:
                # Process failed to start
                stdout, stderr = process.communicate()
                config.status = "error"
                config.updated_at = time.time()
                
                return {
                    "success": False,
                    "error": f"Failed to start server '{config.name}': {stderr}"
                }
                
        except Exception as e:
            config.status = "error"
            config.updated_at = time.time()
            return {"success": False, "error": str(e)}
    
    def stop_server(self, server_id: str) -> Dict[str, Any]:
        """Stop an MCP server"""
        try:
            if server_id not in self.servers:
                return {"success": False, "error": f"Server '{server_id}' not found"}
            
            config = self.servers[server_id]
            
            if config.status == "stopped":
                return {"success": False, "error": f"Server '{config.name}' is already stopped"}
            
            # Stop process
            if server_id in self.processes:
                process = self.processes[server_id]
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                
                del self.processes[server_id]
            
            # Stop health checking
            if server_id in self.health_check_tasks:
                self.health_check_tasks[server_id].cancel()
                del self.health_check_tasks[server_id]
            
            config.process_id = None
            config.status = "stopped"
            config.updated_at = time.time()
            
            self._save_servers()
            
            return {
                "success": True,
                "message": f"MCP server '{config.name}' stopped successfully"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def restart_server(self, server_id: str) -> Dict[str, Any]:
        """Restart an MCP server"""
        stop_result = self.stop_server(server_id)
        
        if not stop_result["success"] and "already stopped" not in stop_result["error"]:
            return stop_result
        
        # Wait a moment
        time.sleep(1)
        
        return asyncio.create_task(self.start_server(server_id))
    
    def _start_health_check(self, server_id: str):
        """Start health checking for a server"""
        async def health_check_loop():
            config = self.servers[server_id]
            
            while config.status == "running":
                try:
                    await asyncio.sleep(config.health_check_interval)
                    
                    if server_id in self.processes:
                        process = self.processes[server_id]
                        if process.poll() is not None:
                            # Process has died
                            config.status = "error"
                            config.process_id = None
                            del self.processes[server_id]
                            self._save_servers()
                            break
                    else:
                        config.status = "error"
                        config.process_id = None
                        self._save_servers()
                        break
                        
                except asyncio.CancelledError:
                    break
                except Exception:
                    continue
        
        task = asyncio.create_task(health_check_loop())
        self.health_check_tasks[server_id] = task
    
    # Utility Methods
    def get_running_servers(self) -> List[str]:
        """Get list of running server IDs"""
        return [server_id for server_id, config in self.servers.items() 
                if config.status == "running"]
    
    def get_enabled_servers(self) -> List[str]:
        """Get list of enabled server IDs"""
        return [server_id for server_id, config in self.servers.items() 
                if config.enabled]
    
    async def start_all_enabled(self) -> Dict[str, Any]:
        """Start all enabled servers with auto_start"""
        started = []
        failed = []
        
        for server_id in self.get_enabled_servers():
            config = self.servers[server_id]
            if config.auto_start and config.status != "running":
                result = await self.start_server(server_id)
                if result["success"]:
                    started.append(config.name)
                else:
                    failed.append(f"{config.name}: {result['error']}")
        
        return {
            "success": len(failed) == 0,
            "started": started,
            "failed": failed,
            "message": f"Started {len(started)} servers" + (f", {len(failed)} failed" if failed else "")
        }
    
    def get_tools_from_servers(self) -> List[Dict[str, Any]]:
        """Get all available tools from running servers"""
        all_tools = []
        
        for server_id, config in self.servers.items():
            if config.status == "running" and server_id in self.processes:
                # This would normally query the MCP server for its tools
                # For now, return placeholder tool info
                all_tools.append({
                    "server_id": server_id,
                    "server_name": config.name,
                    "tools": [
                        {
                            "name": f"{config.id}_tool_example",
                            "description": f"Example tool from {config.name}",
                            "parameters": {"type": "object", "properties": {}}
                        }
                    ]
                })
        
        return all_tools
    
    async def shutdown_all(self):
        """Shutdown all running servers"""
        for server_id in list(self.processes.keys()):
            self.stop_server(server_id)
        
        for task in self.health_check_tasks.values():
            task.cancel()
        
        self.health_check_tasks.clear()

# Global instance
mcp_manager = MCPServerManager()
