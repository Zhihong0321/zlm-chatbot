import axios from 'axios';

// Use relative path by default for production
// Only use localhost for local development if explicitly set
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 300000, // 5 minutes timeout to handle long reasoning models
});

// Request interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// API endpoints
export const api = {
  // Health check
  health: () => apiClient.get('/api/v1/ui/health'),
  
  // Agents
  getAgents: () => apiClient.get('/api/v1/agents/'),
  getAgent: (id: string) => apiClient.get(`/api/v1/agents/${id}`),
  createAgent: (data: any) => apiClient.post('/api/v1/agents/', data),
  updateAgent: (id: string, data: any) => apiClient.put(`/api/v1/agents/${id}`, data),
  deleteAgent: (id: string) => apiClient.delete(`/api/v1/agents/${id}`),
  
  // Agent File Management
  getAgentWithFiles: (id: string) => apiClient.get(`/api/v1/agents/${id}/with-files`),
  getAgentFiles: (id: string) => apiClient.get(`/api/v1/agents/${id}/files`),
  uploadAgentFile: (agentId: string, file: File, purpose?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    if (purpose) {
      formData.append('purpose', purpose);
    }
    return apiClient.post(`/api/v1/agents/${agentId}/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  deleteAgentFile: (agentId: string, fileId: string) => apiClient.delete(`/api/v1/agents/${agentId}/files/${fileId}`),
  
  // Sessions
  getSessions: () => apiClient.get('/api/v1/sessions/'),
  getSession: (id: string) => apiClient.get(`/api/v1/sessions/${id}`),
  createSession: (data: any) => apiClient.post('/api/v1/sessions/', data),
  updateSession: (id: string, data: any) => apiClient.put(`/api/v1/sessions/${id}`, data),
  deleteSession: (id: string) => apiClient.delete(`/api/v1/sessions/${id}`),
  getSessionHistory: (id: string) => apiClient.get(`/api/v1/sessions/${id}/history`),
  
  // Chat
  sendMessage: (sessionId: string, data: any) => apiClient.post(`/api/v1/chat/${sessionId}/messages`, data),
  
  // Knowledge
  uploadFile: (sessionId: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.post(`/api/v1/chat/${sessionId}/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // Advanced Session Management
  searchSessions: (params: any) => apiClient.get('/api/v1/sessions/search', { params }),
  bulkDeleteSessions: (sessionIds: string[]) => apiClient.post('/api/v1/sessions/bulk-delete', { session_ids: sessionIds.map(id => parseInt(id)) }),
  archiveSession: (sessionId: string) => apiClient.post(`/api/v1/sessions/${sessionId}/archive`),
  getSessionAnalytics: () => apiClient.get('/api/v1/sessions/analytics/summary'),
  getActivityTimeline: (days?: number) => apiClient.get('/api/v1/sessions/activity/timeline', { params: { days } }),
  getSessionAnalyticsDetail: (sessionId: string) => apiClient.get(`/api/v1/sessions/${sessionId}/analytics`),
};

export default apiClient;