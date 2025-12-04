import React, { useState } from 'react';
import {
  useMCPServers,
  useMCPServerActions,
  ServerStatusBadge,
  ServerActions
} from './MCPManagement';

interface MCPServer {
  id: string;
  name: string;
  description: string;
  status: 'running' | 'stopped' | 'error' | 'starting';
  enabled: boolean;
  auto_start: boolean;
  process_id: number | null;
  created_at: number;
  updated_at: number;
  command: string;
  arguments: string[];
  environment: Record<string, string>;
  working_directory: string | null;
  health_check_interval: number;
}

interface MCPSystemStatus {
  total_servers: number;
  running_servers: number;
  enabled_servers: number;
  stopped_servers: number;
  error_servers: number;
  total_tools: number;
}

export default function MCPManagementDashboard() {
  const { servers, loading, error, refetch } = useMCPServers();
  const { startServer, stopServer, restartServer } = useMCPServerActions();
  const [systemStatus, setSystemStatus] = useState<MCPSystemStatus | null>(null);
  const [isTesting, setIsTesting] = useState(false);

  // Simple status fetch
  React.useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch('http://localhost:8001/api/v1/mcp/status');
        if (response.ok) {
          const data = await response.json();
          setSystemStatus(data);
        }
      } catch (err) {
        console.error('Failed to fetch status');
      }
    };
    fetchStatus();
    const interval = setInterval(fetchStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  // Quick health test
  const handleTestMCPHealth = async () => {
    setIsTesting(true);
    
    try {
      const responses = await Promise.allSettled([
        fetch('http://localhost:8001/api/v1/mcp/health'),
        fetch('http://localhost:8001/api/v1/mcp/tools'),
        fetch('http://localhost:8001/api/v1/demo'),
        fetch('/api/v1/system/test-mcp-compatibility', { method: 'POST', headers: { 'Content-Type': 'application/json' } })
      ]);

      const results = {
        mcp_health: responses[0].status === 'fulfilled' ? 'PASS' : 'FAIL',
        mcp_tools: responses[1].status === 'fulfilled' ? 'PASS' : 'FAIL',
        demo_functionality: responses[2].status === 'fulfilled' ? 'PASS' : 'FAIL',
        zai_compatibility: responses[3].status === 'fulfilled' ? 'PASS' : 'FAIL'
      };

      const allPassed = Object.values(results).every(r => r === 'PASS');
      alert(`MCP Health Test Results:\n${Object.entries(results).map(([k, v]) => `${k}: ${v}`).join('\n')}\n\nOverall: ${allPassed ? 'HEALTHY' : 'ISSUES DETECTED'}`);
      
    } catch (error) {
      alert('MCP Health Test Failed: Connection error');
    } finally {
      setIsTesting(false);
    }
  };

  // Server action handlers
  const handleStartServer = async (serverId: string) => {
    const success = await startServer(serverId);
    if (success) refetch();
  };

  const handleStopServer = async (serverId: string) => {
    const success = await stopServer(serverId);
    if (success) refetch();
  };

  const handleRestartServer = async (serverId: string) => {
    const success = await restartServer(serverId);
    if (success) refetch();
  };

  // Bulk operations
  const handleStartAll = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/v1/mcp/start-all', { method: 'POST' });
      const result = await response.json();
      alert(result.message);
      refetch();
    } catch (err) {
      alert('Failed to start servers');
    }
  };

  const handleStopAll = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/v1/mcp/stop-all', { method: 'POST' });
      const result = await response.json();
      alert(result.message);
      refetch();
    } catch (err) {
      alert('Failed to stop servers');
    }
  };

  const formatDate = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleString();
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4 m-4">
        <p className="text-red-700">Error loading MCP servers: {error}</p>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">MCP Management</h1>
            <p className="text-gray-600 mt-1">Manage Model Context Protocol servers</p>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={handleTestMCPHealth}
              disabled={isTesting}
              className="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 disabled:opacity-50 flex items-center"
            >
              {isTesting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Testing...
                </>
              ) : (
                <>
                  🔗 Test MCP Health
                </>
              )}
            </button>
            <button
              onClick={handleStartAll}
              className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
            >
              Start All
            </button>
            <button
              onClick={handleStopAll}
              className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700"
            >
              Stop All
            </button>
          </div>
        </div>

        {/* System Status */}
        {systemStatus && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">System Status</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">{systemStatus.total_servers}</div>
                <div className="text-sm text-gray-600">Total Servers</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{systemStatus.running_servers}</div>
                <div className="text-sm text-gray-600">Running</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-600">{systemStatus.stopped_servers}</div>
                <div className="text-sm text-gray-600">Stopped</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">{systemStatus.error_servers}</div>
                <div className="text-sm text-gray-600">Error</div>
              </div>
            </div>
          </div>
        )}

        {/* Servers List */}
        <div className="space-y-4">
          {servers.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
              <p className="text-gray-600 mb-4">No MCP servers configured</p>
            </div>
          ) : (
            servers.map((server) => (
              <div key={server.id} className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-medium text-gray-900">{server.name}</h3>
                    <p className="text-sm text-gray-600 mt-1">{server.description}</p>
                    <div className="flex items-center space-x-4 mt-3">
                      <ServerStatusBadge status={server.status} />
                      <span className="text-sm text-gray-500">
                        PID: {server.process_id || 'N/A'}
                      </span>
                      <span className="text-sm text-gray-500">
                        Created: {formatDate(server.created_at)}
                      </span>
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <ServerActions
                      server={server}
                      onStart={handleStartServer}
                      onStop={handleStopServer}
                      onRestart={handleRestartServer}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium text-gray-700">Command:</span>
                    <div className="font-mono bg-gray-100 px-2 py-1 rounded mt-1">
                      {server.command} {server.arguments.join(' ')}
                    </div>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Working Directory:</span>
                    <div className="font-mono bg-gray-100 px-2 py-1 rounded mt-1">
                      {server.working_directory || 'Default'}
                    </div>
                  </div>
                </div>

                {Object.keys(server.environment).length > 0 && (
                  <div className="mt-4">
                    <span className="font-medium text-gray-700 text-sm">Environment Variables:</span>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {Object.entries(server.environment).map(([key, value]) => (
                        <span
                          key={key}
                          className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
                        >
                          {key}={value}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
