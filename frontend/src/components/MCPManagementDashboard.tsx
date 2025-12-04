import React, { useState } from 'react';
import {
  useMCPServers,
  useMCPServerActions,
  useMCPServerTemplates,
  useMCPSystemStatus,
  ServerStatusBadge,
  ServerActions,
  ServerForm
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

export default function MCPManagementDashboard() {
  const { servers, loading, error, refetch } = useMCPServers();
  const { templates } = useMCPServerTemplates();
  const { status: systemStatus } = useMCPSystemStatus();
  const { startServer, stopServer, restartServer } = useMCPServerActions();

  const [showAddForm, setShowAddForm] = useState(false);
  const [editingServer, setEditingServer] = useState<MCPServer | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [activeTab, setActiveTab] = useState<'servers' | 'status' | 'templates'>('servers');
  const [testResults, setTestResults] = useState<any>(null);
  const [isTesting, setIsTesting] = useState(false);

  const handleStartServer = async (serverId: string) => {
    const success = await startServer(serverId);
    if (success) {
      refetch();
    }
  };

  const handleStopServer = async (serverId: string) => {
    const success = await stopServer(serverId);
    if (success) {
      refetch();
    }
  };

  const handleRestartServer = async (serverId: string) => {
    const success = await restartServer(serverId);
    if (success) {
      refetch();
    }
  };

  const handleAddServer = () => {
    setEditingServer(null);
    setShowAddForm(true);
  };

  const handleEditServer = (server: MCPServer) => {
    setEditingServer(server);
    setShowAddForm(true);
  };

  const handleFormSubmit = async (serverData: Partial<MCPServer>) => {
    setIsSubmitting(true);
    try {
      const url = editingServer?.id
        ? `http://localhost:8001/api/v1/mcp/servers/${editingServer.id}`
        : 'http://localhost:8001/api/v1/mcp/servers';

      const method = editingServer?.id ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(serverData)
      });

      const result = await response.json();

      if (response.ok) {
        setShowAddForm(false);
        setEditingServer(null);
        refetch();
        alert(editingServer?.id ? 'Server updated successfully!' : 'Server added successfully!');
      } else {
        alert(result.error || 'Failed to save server');
      }
    } catch (err) {
      alert('Network error. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteServer = async (serverId: string, serverName: string) => {
    if (!confirm(`Are you sure you want to delete the server "${serverName}"?`)) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:8001/api/v1/mcp/servers/${serverId}`, {
        method: 'DELETE'
      });

      const result = await response.json();

      if (response.ok) {
        refetch();
        alert(result.message || 'Server deleted successfully!');
      } else {
        alert(result.error || 'Failed to delete server');
      }
    } catch (err) {
      alert('Network error. Please try again.');
    }
  };

  const handleStartAll = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/v1/mcp/start-all', {
        method: 'POST'
      });
      
      const result = await response.json();
      
      if (response.ok) {
        alert(result.message);
        refetch();
      } else {
        alert('Failed to start servers');
      }
    } catch (err) {
      alert('Network error. Please try again.');
    }
  };

  const handleStopAll = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/v1/mcp/stop-all', {
        method: 'POST'
      });
      
      const result = await response.json();
      
      if (response.ok) {
        alert(result.message);
        refetch();
      } else {
        alert('Failed to stop servers');
      }
    } catch (err) {
      alert('Network error. Please try again.');
    }
  };

  const handleTestMCPHealth = async () => {
    setIsTesting(true);
    setTestResults(null);
    
    try {
      // Test the MCP API health endpoint
      const healthResponse = await fetch('http://localhost:8001/api/v1/mcp/health');
      const healthData = await healthResponse.json();
      
      // Test tool availability
      const toolsResponse = await fetch('http://localhost:8001/api/v1/mcp/tools');
      const toolsData = await toolsResponse.json();
      
      // Test a simple server operation
      const demoResponse = await fetch('http://localhost:8001/api/v1/demo');
      const demoData = await demoResponse.json();
      
      // Test Z.ai API MCP compatibility
      const compatibilityTest = await fetch('/api/v1/system/test-mcp-compatibility', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const compatibilityData = await compatibilityTest.json();
      
      const results = {
        mcp_api_health: {
          status: healthResponse.ok ? 'PASS' : 'FAIL',
          data: healthData
        },
        tools_available: {
          status: toolsResponse.ok ? 'PASS' : 'FAIL',
          count: toolsData.length,
          data: toolsData.slice(0, 3) // Show first 3 tools
        },
        demo_functionality: {
          status: demoResponse.ok ? 'PASS' : 'FAIL',
          data: demoData.status
        },
        zai_compatibility: {
          status: compatibilityTest.success ? 'PASS' : 'FAIL',
          data: compatibilityTest.message
        },
        overall_status: (healthResponse.ok && toolsResponse.ok && demoResponse.ok && compatibilityTest.success) ? 'HEALTHY' : 'ISSUES Detected'
      };
      
      setTestResults(results);
      
    } catch (error) {
      setTestResults({
        error: 'Test failed to connect to MCP services',
        details: error instanceof Error ? error.message : 'Unknown error',
        overall_status: 'CRITICAL ERROR'
      });
    } finally {
      setIsTesting(false);
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
              className="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 disabled:opacity-50 transition-colors flex items-center"
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
              className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors"
            >
              Start All
            </button>
            <button
              onClick={handleStopAll}
              className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition-colors"
            >
              Stop All
            </button>
            <button
              onClick={handleAddServer}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
            >
              Add Server
            </button>
          </div>
        </div>

        {/* Test Results */}
        {testResults && (
          <div className={`border-l-4 p-4 mb-6 ${
            testResults.overall_status === 'HEALTHY' 
              ? 'bg-green-50 border-green-400' 
              : testResults.overall_status === 'CRITICAL ERROR'
              ? 'bg-red-50 border-red-400'
              : 'bg-yellow-50 border-yellow-400'
          }`}>
            <div className="flex">
              <div className="ml-3">
                <h3 className={`text-lg font-medium ${
                  testResults.overall_status === 'HEALTHY'
                    ? 'text-green-800'
                    : testResults.overall_status === 'CRITICAL ERROR'
                    ? 'text-red-800'
                    : 'text-yellow-800'
                }`}>
                  MCP Health Test Results
                </h3>
                <div className="mt-4 space-y-3">
                  {testResults.error ? (
                    <p className="text-red-700">{testResults.error}: {testResults.details}</p>
                  ) : (
                    <>
                      <div className="flex items-center">
                        <span className={`inline-block w-3 h-3 rounded-full mr-2 ${
                          testResults.mcp_api_health.status === 'PASS' ? 'bg-green-500' : 'bg-red-500'
                        }`}></span>
                        <span className="text-sm font-medium">MCP API Health:</span>
                        <span className={`ml-2 text-sm ${
                          testResults.mcp_api_health.status === 'PASS' ? 'text-green-700' : 'text-red-700'
                        }`}>
                          {testResults.mcp_api_health.status}
                        </span>
                      </div>
                      <div className="flex items-center">
                        <span className={`inline-block w-3 h-3 rounded-full mr-2 ${
                          testResults.tools_available.status === 'PASS' ? 'bg-green-500' : 'bg-red-500'
                        }`}></span>
                        <span className="text-sm font-medium">Tools Available:</span>
                        <span className={`ml-2 text-sm ${
                          testResults.tools_available.status === 'PASS' ? 'text-green-700' : 'text-red-700'
                        }`}>
                          {testResults.tools_available.count} tools found
                        </span>
                      </div>
                      <div className="flex items-center">
                        <span className={`inline-block w-3 h-3 rounded-full mr-2 ${
                          testResults.demo_functionality.status === 'PASS' ? 'bg-green-500' : 'bg-red-500'
                        }`}></span>
                        <span className="text-sm font-medium">Demo Functionality:</span>
                        <span className={`ml-2 text-sm ${
                          testResults.demo_functionality.status === 'PASS' ? 'text-green-700' : 'text-red-700'
                        }`}>
                          {testResults.demo_functionality.status} ({testResults.demo_functionality.data})
                        </span>
                      </div>
                      <div className="flex items-center">
                        <span className={`inline-block w-3 h-3 rounded-full mr-2 ${
                          testResults.zai_compatibility.status === 'PASS' ? 'bg-green-500' : 'bg-red-500'
                        }`}></span>
                        <span className="text-sm font-medium">Z.ai API Compatibility:</span>
                        <span className={`ml-2 text-sm ${
                          testResults.zai_compatibility.status === 'PASS' ? 'text-green-700' : 'text-red-700'
                        }`}>
                          {testResults.zai_compatibility.status}
                        </span>
                      </div>
                      <div className="mt-3 pt-3 border-t border-gray-200">
                        <span className="text-sm font-medium">Overall Status: </span>
                        <span className={`ml-2 font-bold ${
                          testResults.overall_status === 'HEALTHY'
                            ? 'text-green-700'
                            : testResults.overall_status === 'CRITICAL ERROR'
                            ? 'text-red-700'
                            : 'text-yellow-700'
                        }`}>
                          {testResults.overall_status}
                        </span>
                      </div>
                    </>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

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

        {/* Tabs */}
        <div className="border-b border-gray-200 mb-6">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('servers')}
              className={`${
                activeTab === 'servers'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm`}
            >
              Servers ({servers.length})
            </button>
            <button
              onClick={() => setActiveTab('status')}
              className={`${
                activeTab === 'status'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm`}
            >
              System Status
            </button>
            <button
              onClick={() => setActiveTab('templates')}
              className={`${
                activeTab === 'templates'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm`}
            >
              Templates ({templates.length})
            </button>
          </nav>
        </div>

        {/* Content */}
        {activeTab === 'servers' && (
          <div className="space-y-4">
            {showAddForm && (
              <div className="bg-gray-50 rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  {editingServer ? 'Edit Server' : 'Add New Server'}
                </h3>
                <ServerForm
                  server={editingServer || undefined}
                  templates={templates}
                  onSubmit={handleFormSubmit}
                  onCancel={() => {
                    setShowAddForm(false);
                    setEditingServer(null);
                  }}
                  isSubmitting={isSubmitting}
                />
              </div>
            )}

            {servers.length === 0 ? (
              <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
                <div className="text-gray-400 mb-4">
                  <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M12 5l7 7-7 7" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No MCP servers configured</h3>
                <p className="text-gray-600 mb-4">Get started by adding your first MCP server.</p>
                <button
                  onClick={handleAddServer}
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
                >
                  Add Your First Server
                </button>
              </div>
            ) : (
              <div className="grid gap-4">
                {servers.map((server) => (
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
                        <button
                          onClick={() => handleEditServer(server)}
                          className="text-sm text-blue-600 hover:text-blue-800 px-2 py-1 rounded hover:bg-blue-50 transition-colors"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDeleteServer(server.id, server.name)}
                          className="text-sm text-red-600 hover:text-red-800 px-2 py-1 rounded hover:bg-red-50 transition-colors"
                        >
                          Delete
                        </button>
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

                    <div className="flex items-center space-x-4 mt-4 text-sm text-gray-600">
                      <label className="flex items-center">
                        <input
                          type="checkbox"
                          checked={server.enabled}
                          className="mr-2"
                          readOnly
                        />
                        Enabled
                      </label>
                      <label className="flex items-center">
                        <input
                          type="checkbox"
                          checked={server.auto_start}
                          className="mr-2"
                          readOnly
                        />
                        Auto Start
                      </label>
                      <span>Health Check: {server.health_check_interval}s</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'status' && systemStatus && (
          <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Detailed System Status</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Server Statistics</h4>
                <dl className="space-y-2">
                  <div className="flex justify-between">
                    <dt className="text-sm text-gray-600">Total Servers:</dt>
                    <dd className="text-sm font-medium">{systemStatus.total_servers}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-sm text-gray-600">Running:</dt>
                    <dd className="text-sm font-medium text-green-600">{systemStatus.running_servers}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-sm text-gray-600">Stopped:</dt>
                    <dd className="text-sm font-medium text-gray-600">{systemStatus.stopped_servers}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-sm text-gray-600">Error:</dt>
                    <dd className="text-sm font-medium text-red-600">{systemStatus.error_servers}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-sm text-gray-600">Enabled:</dt>
                    <dd className="text-sm font-medium text-blue-600">{systemStatus.enabled_servers}</dd>
                  </div>
                </dl>
              </div>

              <div>
                <h4 className="font-medium text-gray-900 mb-3">Tools & Capabilities</h4>
                <dl className="space-y-2">
                  <div className="flex justify-between">
                    <dt className="text-sm text-gray-600">Total Tools Available:</dt>
                    <dd className="text-sm font-medium">{systemStatus.total_tools}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-sm text-gray-600">Server Types:</dt>
                    <dd className="text-sm font-medium">
                      {servers.length > 0 && [...new Set(servers.map(s => s.command.split(' ')[0]))].join(', ')}
                    </dd>
                  </div>
                </dl>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'templates' && (
          <div className="grid gap-4 md:grid-cols-2">
            {templates.map((template, index) => (
              <div key={index} className="bg-white rounded-lg border border-gray-200 shadow-sm p-4">
                <h3 className="font-medium text-gray-900">{template.name}</h3>
                <p className="text-sm text-gray-600 mt-1">{template.description}</p>
                <div className="mt-3">
                  <span className="text-sm font-medium text-gray-700">Command:</span>
                  <div className="font-mono bg-gray-100 px-2 py-1 rounded text-sm mt-1">
                    {template.template.command} {template.template.arguments.join(' ')}
                  </div>
                </div>
                <button
                  onClick={() => {
                    // This would populate the form with the template data
                    setEditingServer({
                      name: template.name,
                      description: template.description,
                      command: template.template.command,
                      arguments: template.template.arguments,
                      environment: template.template.environment,
                      working_directory: template.template.working_directory,
                      enabled: template.template.enabled,
                      auto_start: template.template.auto_start,
                      health_check_interval: template.template.health_check_interval,
                    } as MCPServer);
                    setShowAddForm(true);
                    setActiveTab('servers');
                  }}
                  className="mt-3 text-sm bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 transition-colors"
                >
                  Use Template
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
