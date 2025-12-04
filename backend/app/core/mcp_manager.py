"""
MCP Server Management System
Provides full CRUD operations for MCP servers in the Z.ai chatbot system
Now backed by PostgreSQL database instead of JSON file
"""

import os
import subprocess
import asyncio
import uuid
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from sqlalchemy import text
from app.db.database import SessionLocal

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
    """Manages MCP servers lifecycle and configuration using Database"""
    
    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.health_check_tasks: Dict[str, asyncio.Task] = {}
        # In-memory cache of server status (since process state is local to this container)
        self.status_cache: Dict[str, str] = {}
        self.pid_cache: Dict[str, int] = {}
        
    def _get_db(self):
        return SessionLocal()

    def list_servers(self) -> List[Dict[str, Any]]:
        """List all MCP servers with their status"""
        db = self._get_db()
        try:
            # Simple fixed query with basic columns that always exist
            result = db.execute(text("""
                SELECT id, name, description, command, enabled, auto_start, 
                       health_check_interval, status, process_id, created_at, updated_at
                FROM mcp_servers
            """)).mappings().all()
            
            servers_info = []
            for row in result:
                server_data = dict(row)
                
                # Try to get JSON columns if they exist
                try:
                    json_result = db.execute(text("""
                        SELECT arguments, environment, working_directory
                        FROM mcp_servers WHERE id = :id
                    """), {"id": server_data['id']}).first()
                    
                    if json_result:
                        server_data['arguments'] = json.loads(json_result[0] or '[]')
                        server_data['environment'] = json.loads(json_result[1] or '{}')
                        server_data['working_directory'] = json_result[2] or ''
                    else:
                        server_data['arguments'] = []
                        server_data['environment'] = {}
                        server_data['working_directory'] = ''
                except:
                    # Fallback values if JSON columns don't exist
                    server_data['arguments'] = []
                    server_data['environment'] = {}
                    server_data['working_directory'] = ''
                
                # Override status from local cache if process is managed by this instance
                sid = server_data['id']
                if sid in self.status_cache:
                    server_data['status'] = self.status_cache[sid]
                if sid in self.pid_cache:
                    server_data['process_id'] = self.pid_cache[sid]
                    
                servers_info.append(server_data)
                
            return servers_info
        except Exception as e:
            print(f"Error listing servers: {e}")
            return []
        finally:
            db.close()
    
    def add_server(self, server_config: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new MCP server"""
        db = self._get_db()
        try:
            # Generate unique ID if not provided
            if 'id' not in server_config:
                server_config['id'] = str(uuid.uuid4())
            
            server_id = server_config['id']
            
            # Check if exists
            exists = db.execute(text("SELECT 1 FROM mcp_servers WHERE id = :id"), {"id": server_id}).scalar()
            if exists:
                return {"success": False, "error": f"Server with ID '{server_id}' already exists"}
            
            # Prepare data
            arguments = json.dumps(server_config.get('arguments', []))
            environment = json.dumps(server_config.get('environment', {}))
            
            query = text("""
                INSERT INTO mcp_servers 
                (id, name, description, command, arguments, environment, working_directory, 
                 enabled, auto_start, health_check_interval, status, created_at, updated_at)
                VALUES 
                (:id, :name, :description, :command, :arguments, :environment, :working_directory,
                 :enabled, :auto_start, :health_check_interval, 'stopped', NOW(), NOW())
            """)
            
            db.execute(query, {
                "id": server_id,
                "name": server_config['name'],
                "description": server_config['description'],
                "command": server_config['command'],
                "arguments": arguments,
                "environment": environment,
                "working_directory": server_config.get('working_directory'),
                "enabled": server_config.get('enabled', True),
                "auto_start": server_config.get('auto_start', True),
                "health_check_interval": server_config.get('health_check_interval', 30)
            })
            db.commit()
            
            return {
                "success": True,
                "server_id": server_id,
                "message": f"MCP server '{server_config['name']}' added successfully"
            }
            
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}
        finally:
            db.close()
    
    def get_server(self, server_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific server"""
        db = self._get_db()
        try:
            result = db.execute(text("SELECT * FROM mcp_servers WHERE id = :id"), {"id": server_id}).mappings().first()
            
            if not result:
                return None
                
            data = dict(result)
            # JSON deserialization
            if isinstance(data.get('arguments'), str):
                try: data['arguments'] = json.loads(data['arguments']) 
                except: data['arguments'] = []
            if isinstance(data.get('environment'), str):
                try: data['environment'] = json.loads(data['environment']) 
                except: data['environment'] = {}
                
            # Sync with local status
            if server_id in self.status_cache:
                data['status'] = self.status_cache[server_id]
            if server_id in self.pid_cache:
                data['process_id'] = self.pid_cache[server_id]
                
            return data
        finally:
            db.close()
    
    def update_server(self, server_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing MCP server configuration"""
        db = self._get_db()
        try:
            # Build update query dynamically
            fields = []
            params = {"id": server_id}
            
            for key, value in updates.items():
                if key in ['arguments', 'environment']:
                    value = json.dumps(value)
                
                fields.append(f"{key} = :{key}")
                params[key] = value
            
            fields.append("updated_at = NOW()")
            
            if not fields:
                return {"success": True, "message": "No changes"}
                
            query = text(f"UPDATE mcp_servers SET {', '.join(fields)} WHERE id = :id")
            
            result = db.execute(query, params)
            db.commit()
            
            if result.rowcount == 0:
                return {"success": False, "error": f"Server '{server_id}' not found"}
                
            return {
                "success": True,
                "message": f"MCP server updated successfully"
            }
            
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}
        finally:
            db.close()
    
    def delete_server(self, server_id: str) -> Dict[str, Any]:
        """Delete an MCP server"""
        # Stop it first
        self.stop_server(server_id)
        
        db = self._get_db()
        try:
            result = db.execute(text("DELETE FROM mcp_servers WHERE id = :id"), {"id": server_id})
            db.commit()
            
            if result.rowcount == 0:
                return {"success": False, "error": f"Server '{server_id}' not found"}
                
            return {"success": True, "message": "Server deleted"}
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}
        finally:
            db.close()
    
    # Server Lifecycle Management
    async def start_server(self, server_id: str) -> Dict[str, Any]:
        """Start an MCP server"""
        server = self.get_server(server_id)
        if not server:
            return {"success": False, "error": "Server not found"}
            
        if not server['enabled']:
            return {"success": False, "error": "Server is disabled"}
            
        # Update local status
        self.status_cache[server_id] = "starting"
        
        try:
            # Prepare command
            cmd = [server['command']] + (server['arguments'] or [])
            env = os.environ.copy()
            if server['environment']:
                env.update(server['environment'])
            
            # Start process
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                cwd=server['working_directory'] or os.getcwd()
            )
            
            # Wait a moment for process to initialize
            await asyncio.sleep(1)
            
            if process.poll() is None:
                # Process is running
                pid = process.pid
                self.processes[server_id] = process
                self.status_cache[server_id] = "running"
                self.pid_cache[server_id] = pid
                
                # Update DB status
                self.update_server(server_id, {"status": "running", "process_id": pid})
                
                # Start health checking
                self._start_health_check(server_id, server.get('health_check_interval', 30))
                
                return {
                    "success": True,
                    "message": f"MCP server '{server['name']}' started successfully",
                    "process_id": pid
                }
            else:
                # Process failed to start
                stdout, stderr = process.communicate()
                self.status_cache[server_id] = "error"
                self.update_server(server_id, {"status": "error"})
                
                return {
                    "success": False,
                    "error": f"Failed to start server: {stderr}"
                }
                
        except Exception as e:
            self.status_cache[server_id] = "error"
            return {"success": False, "error": str(e)}
    
    def stop_server(self, server_id: str) -> Dict[str, Any]:
        """Stop an MCP server"""
        if server_id in self.processes:
            process = self.processes[server_id]
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            
            del self.processes[server_id]
        
        if server_id in self.health_check_tasks:
            self.health_check_tasks[server_id].cancel()
            del self.health_check_tasks[server_id]
            
        self.status_cache[server_id] = "stopped"
        if server_id in self.pid_cache:
            del self.pid_cache[server_id]
            
        # Update DB
        self.update_server(server_id, {"status": "stopped", "process_id": None})
        
        return {"success": True, "message": "Server stopped"}
    
    def _start_health_check(self, server_id: str, interval: int):
        """Start health checking for a server"""
        async def health_check_loop():
            while server_id in self.status_cache and self.status_cache[server_id] == "running":
                try:
                    await asyncio.sleep(interval)
                    
                    if server_id in self.processes:
                        process = self.processes[server_id]
                        if process.poll() is not None:
                            # Process has died
                            self.status_cache[server_id] = "error"
                            if server_id in self.pid_cache:
                                del self.pid_cache[server_id]
                            del self.processes[server_id]
                            self.update_server(server_id, {"status": "error", "process_id": None})
                            break
                    else:
                        break
                        
                except asyncio.CancelledError:
                    break
                except Exception:
                    continue
        
        task = asyncio.create_task(health_check_loop())
        self.health_check_tasks[server_id] = task

    def get_tools_from_servers(self) -> List[Dict[str, Any]]:
        """Get available tools"""
        # TODO: Implement real tool discovery from running servers
        return []
    
    def get_running_servers(self) -> List[str]:
        return [sid for sid, status in self.status_cache.items() if status == "running"]
    
    def get_enabled_servers(self) -> List[str]:
        # This implies a DB query
        servers = self.list_servers()
        return [s['id'] for s in servers if s['enabled']]
    
    async def start_all_enabled(self) -> Dict[str, Any]:
        servers = self.list_servers()
        started = []
        failed = []
        
        for server in servers:
            if server['enabled'] and server['auto_start'] and server['status'] != 'running':
                res = await self.start_server(server['id'])
                if res['success']:
                    started.append(server['name'])
                else:
                    failed.append(f"{server['name']}: {res['error']}")
                    
        return {
            "success": len(failed) == 0,
            "started": started,
            "failed": failed,
            "message": f"Started {len(started)} servers"
        }

# Global instance
mcp_manager = MCPServerManager()
