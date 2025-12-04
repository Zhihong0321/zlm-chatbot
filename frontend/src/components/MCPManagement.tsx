import React, { useState, useEffect } from 'react';

// Simple types
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

// Simple API calls
const API_BASE = 'http://localhost:8001/api/v1/mcp';

export const useMCPServers = () => {
  const [servers, setServers] = useState<MCPServer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchServers = async () => {
    try {
      const response = await fetch(`${API_BASE}/servers`);
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
    const interval = setInterval(fetchServers, 5000);
    return () => clearInterval(interval);
  }, []);

  return { servers, loading, error, refetch: fetchServers };
};

export const useMCPServerActions = () => {
  const startServer = async (serverId: string) => {
    try {
      const response = await fetch(`${API_BASE}/servers/${serverId}/start`, { method: 'POST' });
      const result = await response.json();
      
      if (response.ok) {
        alert(result.message);
        return true;
      } else {
        alert(result.error || 'Failed to start server');
        return false;
      }
    } catch (err) {
      alert('Network error starting server');
      return false;
    }
  };

  const stopServer = async (serverId: string) => {
    try {
      const response = await fetch(`${API_BASE}/servers/${serverId}/stop`, { method: 'POST' });
      const result = await response.json();
      
      if (response.ok) {
        alert(result.message);
        return true;
      } else {
        alert(result.error || 'Failed to stop server');
        return false;
      }
    } catch (err) {
      alert('Network error stopping server');
      return false;
    }
  };

  const restartServer = async (serverId: string) => {
    try {
      const response = await fetch(`${API_BASE}/servers/${serverId}/restart`, { method: 'POST' });
      const result = await response.json();
      
      if (response.ok) {
        alert(result.message);
        return true;
      } else {
        alert(result.error || 'Failed to restart server');
        return false;
      }
    } catch (err) {
      alert('Network error restarting server');
      return false;
    }
  };

  return { startServer, stopServer, restartServer };
};

// Status Badge
export const ServerStatusBadge = ({ status }: { status: string }) => {
  const getColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'running': return 'bg-green-100 text-green-800';
      case 'stopped': return 'bg-gray-100 text-gray-800';
      case 'error': return 'bg-red-100 text-red-800';
      case 'starting': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getText = (status: string) => {
    switch (status.toLowerCase()) {
      case 'running': return '🟢 Running';
      case 'stopped': return '⚪ Stopped';
      case 'error': return '🔴 Error';
      case 'starting': return '🟡 Starting';
      default: return '❓ Unknown';
    }
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getColor(status)}`}>
      {getText(status)}
    </span>
  );
};

// Server Actions
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
          className="text-sm bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700 disabled:opacity-50"
        >
          {isLoading ? 'Starting...' : 'Start'}
        </button>
      ) : (
        <button
          onClick={() => onStop(server.id)}
          className="text-sm bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700"
        >
          Stop
        </button>
      )}
      
      <button
        onClick={() => onRestart(server.id)}
        disabled={isLoading}
        className="text-sm bg-yellow-600 text-white px-3 py-1 rounded hover:bg-yellow-700 disabled:opacity-50"
      >
        {isLoading ? 'Restarting...' : 'Restart'}
      </button>
    </div>
  );
};
