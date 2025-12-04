import React, { useState, useEffect } from 'react';
import { useAppToast } from '../AppProviderWithToast';

// API Types
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

interface MCPServerTemplate {
  name: string;
  description: string;
  template: {
    command: string;
    arguments: string[];
    environment: Record<string, string>;
    working_directory: string | null;
    enabled: boolean;
    auto_start: boolean;
    health_check_interval: number;
  };
}

interface MCPSystemStatus {
  total_servers: number;
  running_servers: number;
  enabled_servers: number;
  stopped_servers: number;
  error_servers: number;
  total_tools: number;
}

// API Functions
const MCP_API_BASE = 'http://localhost:8001/api/v1/mcp';

export const useMCPServers = () => {
  const [servers, setServers] = useState<MCPServer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchServers = async () => {
    try {
      const response = await fetch(`${MCP_API_BASE}/servers`);
      if (!response.ok) throw new Error('Failed to fetch servers');
      const data = await response.json();
      setServers(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchServers();
    const interval = setInterval(fetchServers, 5000); // Auto-refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  return { servers, loading, error, refetch: fetchServers };
};

export const useMCPServerActions = () => {
  const notify = useAppToast();

  const startServer = async (serverId: string) => {
    try {
      const response = await fetch(`${MCP_API_BASE}/servers/${serverId}/start`, {
        method: 'POST'
      });
      const result = await response.json();
      
      if (response.ok) {
        notify(result.message);
        return true;
      } else {
        notify(result.error || 'Failed to start server');
        return false;
      }
    } catch (err) {
      notify('Network error starting server');
      return false;
    }
  };

  const stopServer = async (serverId: string) => {
    try {
      const response = await fetch(`${MCP_API_BASE}/servers/${serverId}/stop`, {
        method: 'POST'
      });
      const result = await response.json();
      
      if (response.ok) {
        notify(result.message);
        return true;
      } else {
        notify(result.error || 'Failed to stop server');
        return false;
      }
    } catch (err) {
      notify('Network error stopping server');
      return false;
    }
  };

  const restartServer = async (serverId: string) => {
    try {
      const response = await fetch(`${MCP_API_BASE}/servers/${serverId}/restart`, {
        method: 'POST'
      });
      const result = await response.json();
      
      if (response.ok) {
        notify(result.message);
        return true;
      } else {
        notify(result.error || 'Failed to restart server');
        return false;
      }
    } catch (err) {
      notify('Network error restarting server');
      return false;
    }
  };

  return { startServer, stopServer, restartServer };
};

export const useMCPServerTemplates = () => {
  const [templates, setTemplates] = useState<MCPServerTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTemplates = async () => {
      try {
        const response = await fetch(`${MCP_API_BASE}/templates`);
        if (!response.ok) throw new Error('Failed to fetch templates');
        const data = await response.json();
        setTemplates(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchTemplates();
  }, []);

  return { templates, loading, error };
};

export const useMCPSystemStatus = () => {
  const [status, setStatus] = useState<MCPSystemStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch(`${MCP_API_BASE}/status`);
        if (!response.ok) throw new Error('Failed to fetch status');
        const data = await response.json();
        setStatus(data);
      } catch (err) {
        console.error('Failed to fetch MCP status:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 10000); // Update every 10 seconds
    return () => clearInterval(interval);
  }, []);

  return { status, loading };
};

// Status Badge Component
export const ServerStatusBadge = ({ status }: { status: string }) => {
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'running':
        return 'bg-green-100 text-green-800';
      case 'stopped':
        return 'bg-gray-100 text-gray-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      case 'starting':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status: string) => {
    switch (status.toLowerCase()) {
      case 'running':
        return '🟢 Running';
      case 'stopped':
        return '⚪ Stopped';
      case 'error':
        return '🔴 Error';
      case 'starting':
        return '🟡 Starting';
      default:
        return '❓ Unknown';
    }
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(status)}`}>
      {getStatusText(status)}
    </span>
  );
};

// Server Actions Component
export const ServerActions = ({ server, onStart, onStop, onRestart }: { 
  server: MCPServer;
  onStart: (id: string) => void;
  onStop: (id: string) => void;
  onRestart: (id: string) => void;
}) => {
  const isRunning = server.status === 'running';
  const isLoading = server.status === 'starting';

  return (
    <div className="flex space-x-2">
      {!isRunning ? (
        <button
          onClick={() => onStart(server.id)}
          disabled={isLoading}
          className="text-sm bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isLoading ? 'Starting...' : 'Start'}
        </button>
      ) : (
        <button
          onClick={() => onStop(server.id)}
          className="text-sm bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700 transition-colors"
        >
          Stop
        </button>
      )}
      
      <button
        onClick={() => onRestart(server.id)}
        disabled={isLoading}
        className="text-sm bg-yellow-600 text-white px-3 py-1 rounded hover:bg-yellow-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {isLoading ? 'Restarting...' : 'Restart'}
      </button>
    </div>
  );
};

// Add/Edit Server Form Component
export const ServerForm = ({ 
  server, 
  templates, 
  onSubmit, 
  onCancel,
  isSubmitting 
}: {
  server?: Partial<MCPServer>;
  templates: MCPServerTemplate[];
  onSubmit: (data: Partial<MCPServer>) => void;
  onCancel: () => void;
  isSubmitting: boolean;
}) => {
  const [formData, setFormData] = useState({
    name: server?.name || '',
    description: server?.description || '',
    command: server?.command || '',
    arguments: server?.arguments?.join(' ') || '',
    environment: server?.environment ? Object.entries(server.environment)
      .map(([key, value]) => `${key}=${value}`)
      .join('\n') : '',
    working_directory: server?.working_directory || '',
    enabled: server?.enabled !== false,
    auto_start: server?.auto_start !== false,
    health_check_interval: server?.health_check_interval || 30
  });

  const [selectedTemplate, setSelectedTemplate] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value
    }));
  };

  const handleTemplateChange = (templateName: string) => {
    const template = templates.find(t => t.name === templateName);
    if (template) {
      setFormData({
        name: template.name,
        description: template.description,
        command: template.template.command,
        arguments: template.template.arguments.join(' '),
        environment: Object.entries(template.template.environment)
          .map(([key, value]) => `${key}=${value}`)
          .join('\n'),
        working_directory: template.template.working_directory || '',
        enabled: template.template.enabled,
        auto_start: template.template.auto_start,
        health_check_interval: template.template.health_check_interval
      });
      setSelectedTemplate(templateName);
    }
  };

  const parseEnvironment = (envText: string): Record<string, string> => {
    const env: Record<string, string> = {};
    envText.split('\n').forEach(line => {
      const trimmed = line.trim();
      if (trimmed) {
        const [key, ...valueParts] = trimmed.split('=');
        if (key && valueParts.length > 0) {
          env[key.trim()] = valueParts.join('=').trim();
        }
      }
    });
    return env;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const serverData = {
      ...formData,
      arguments: formData.arguments.split(' ').filter(arg => arg.trim()),
      environment: parseEnvironment(formData.environment)
    };

    if (server?.id) {
      serverData.id = server.id;
    }

    onSubmit(serverData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Template (Optional)
        </label>
        <select
          value={selectedTemplate}
          onChange={(e) => handleTemplateChange(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Choose a template...</option>
          {templates.map(template => (
            <option key={template.name} value={template.name}>
              {template.name}
            </option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Server Name*
          </label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Command*
          </label>
          <input
            type="text"
            name="command"
            value={formData.command}
            onChange={handleChange}
            required
            placeholder="python, npx, node..."
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Description*
        </label>
        <input
          type="text"
          name="description"
          value={formData.description}
          onChange={handleChange}
          required
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Arguments (space-separated)
        </label>
        <input
          type="text"
          name="arguments"
          value={formData.arguments}
          onChange={handleChange}
          placeholder="mcp_file_server.py --port 8080"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Environment Variables (one per line: KEY=VALUE)
        </label>
        <textarea
          name="environment"
          value={formData.environment}
          onChange={handleChange}
          rows={3}
          placeholder="API_KEY=your_key_here&#10;DEBUG=true"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Working Directory
        </label>
        <input
          type="text"
          name="working_directory"
          value={formData.working_directory}
          onChange={handleChange}
          placeholder="/path/to/directory"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Health Check Interval (seconds)
          </label>
          <input
            type="number"
            name="health_check_interval"
            value={formData.health_check_interval}
            onChange={handleChange}
            min="5"
            max="300"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="flex items-center space-x-4">
          <label className="flex items-center">
            <input
              type="checkbox"
              name="enabled"
              checked={formData.enabled}
              onChange={handleChange}
              className="mr-2"
            />
            <span className="text-sm text-gray-700">Enabled</span>
          </label>

          <label className="flex items-center">
            <input
              type="checkbox"
              name="auto_start"
              checked={formData.auto_start}
              onChange={handleChange}
              className="mr-2"
            />
            <span className="text-sm text-gray-700">Auto Start</span>
          </label>
        </div>
      </div>

      <div className="flex justify-end space-x-3 pt-4">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={isSubmitting}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          {isSubmitting ? 'Saving...' : (server?.id ? 'Update Server' : 'Create Server')}
        </button>
      </div>
    </form>
  );
};
