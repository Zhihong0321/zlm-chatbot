# MCP Management Page

## Overview
The MCP Management page provides a comprehensive interface for managing Model Context Protocol (MCP) servers in your Z.ai chatbot system.

## Access
Navigate to `/mcp` in the application or click the "🛠️ MCP" link in the navigation bar.

## Features

### 1. Quick Test MCP Health
- **Purpose**: Instantly verify the health and compatibility of your MCP integration
- **Functionality**:
  - Tests MCP API connectivity
  - Verifies tool availability
  - Checks demo functionality
  - Validates Z.ai API compatibility
  - Provides overall status (HEALTHY/ISSUES/CRITICAL ERROR)

### 2. Server Management
- **View Servers**: List all configured MCP servers with status indicators
- **Server Actions**: Start, stop, and restart individual servers
- **Bulk Operations**: Start all enabled servers or stop all running servers
- **Real-time Status**: Auto-refresh every 5 seconds

### 3. Server Configuration
- **Add New Server**: Create custom MCP server configurations
- **Edit Existing**: Modify server settings, commands, and parameters
- **Delete Servers**: Remove unused server configurations
- **Templates**: Use predefined templates for common server types

### 4. Server Templates
Predefined templates available:
- **File System Server**: Local file operations (list, read, search)
- **Database Server**: Database query and management tools
- **Git Server**: Git repository operations and version control
- **Web Fetch Server**: Web content fetching and HTTP requests
- **Memory Server**: Knowledge graph and memory storage

### 5. System Monitoring
- **Real-time Statistics**: Total servers, running, stopped, error states
- **Tool Count**: Number of available tools across all servers
- **Health Indicators**: Visual status badges and metrics
- **Detailed Logs**: Server logs and activity tracking

## Usage Instructions

### Testing MCP Integration
1. Click the purple "🔗 Test MCP Health" button
2. Wait for the test to complete (typically 10-15 seconds)
3. Review the results section for detailed status information
4. Address any issues indicated by the test results

### Managing Servers
1. **To add a server**: Click "Add Server" → Choose template or fill in custom configuration → Save
2. **To start a server**: Click the green "Start" button next to the server
3. **To stop a server**: Click the red "Stop" button next to the server
4. **To manage servers**: Use the "Start All" or "Stop All" buttons for bulk operations

### Server Configuration
- **Command**: Executable command (python, npx, node, etc.)
- **Arguments**: Command-line arguments for the server
- **Environment Variables**: KEY=VALUE pairs (one per line)
- **Working Directory**: Directory where the server runs
- **Health Check**: Interval in seconds for health monitoring

## Status Indicators

### Server Status
- 🟢 **Running**: Server is operational and responding
- ⚪ **Stopped**: Server is not running
- 🔴 **Error**: Server encountered an error
- 🟡 **Starting**: Server is starting up

### Test Results
- 🟢 **PASS**: Component is functioning correctly
- 🔔 **FAIL**: Component has issues that need attention
- 🔴 **CRITICAL ERROR**: Major problem preventing proper operation

## Troubleshooting

### Common Issues
1. **Server won't start**: Check command, arguments, and working directory
2. **MCP API unreachable**: Ensure MCP management server is running on port 8001
3. **Tools not available**: Start the required MCP servers
4. **Z.ai compatibility**: Verify API key configuration and endpoint access

### Support
- Check the system diagnostic logs for detailed error information
- Use the "System Status" tab to see detailed metrics
- Refer to the MCP integration documentation for setup instructions

## Technical Details

### API Endpoints Used
- `GET /api/v1/mcp/health` - Health check
- `GET /api/v1/mcp/servers` - List servers  
- `GET /api/v1/mcp/tools` - List available tools
- `GET /api/v1/demo` - Demo functionality test
- `POST /api/v1/system/test-mcp-compatibility` - Z.ai API compatibility test

### Database Integration
- Server configurations stored in `mcp_servers` table
- Usage tracking in `mcp_tool_usage` table
- Agent-server relationships in `agent_mcp_servers` table
- System metrics in `mcp_system_metrics` table

This management interface provides full control over your MCP integration, ensuring reliable and efficient operation of the enhanced chatbot system.
