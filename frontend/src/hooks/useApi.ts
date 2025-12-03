import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';
import type { Agent, Session, Message, CreateAgentRequest, UpdateAgentRequest, CreateSessionRequest } from '../types';

export function useAgents() {
  return useQuery({
    queryKey: ['agents'],
    queryFn: () => api.getAgents().then(res => res.data),
  });
}

export function useCreateAgent() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: CreateAgentRequest) => api.createAgent(data).then(res => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] });
    },
  });
}

export function useUpdateAgent() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateAgentRequest }) => 
      api.updateAgent(id, data).then(res => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] });
    },
  });
}

export function useDeleteAgent() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: string) => api.deleteAgent(id).then(res => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] });
    },
  });
}

export function useSessions() {
  return useQuery({
    queryKey: ['sessions'],
    queryFn: () => api.getSessions().then(res => res.data),
  });
}

export function useCreateSession() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: CreateSessionRequest) => api.createSession(data).then(res => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sessions'] });
    },
  });
}

export function useDeleteSession() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: string) => api.deleteSession(id).then(res => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sessions'] });
    },
  });
}

export function useSession(id: string) {
  return useQuery({
    queryKey: ['session', id],
    queryFn: () => api.getSession(id).then(res => res.data),
    enabled: !!id,
  });
}

export function useSessionHistory(id: string) {
  return useQuery({
    queryKey: ['session', id, 'history'],
    queryFn: () => api.getSessionHistory(id).then(res => res.data),
    enabled: !!id,
  });
}

export function useSendMessage() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ sessionId, message }: { sessionId: string; message: string }) => 
      api.sendMessage(sessionId, { message }).then(res => res.data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['session', variables.sessionId, 'history'] });
    },
  });
}

export function useUpdateSession() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, ...data }: { id: string; [key: string]: any }) => 
      api.updateSession(id, data).then(res => res.data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['sessions'] });
      queryClient.invalidateQueries({ queryKey: ['session', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['session', variables.id, 'history'] });
    },
  });
}

export function useUploadFile() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ sessionId, file }: { sessionId: string; file: File }) => 
      api.uploadFile(sessionId, file).then(res => res.data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['session', variables.sessionId, 'history'] });
    },
  });
}

export function useSearchSessions() {
  return useMutation({
    mutationFn: (params: {
      q?: string;
      agent_id?: number;
      date_from?: string;
      date_to?: string;
      min_messages?: number;
      skip?: number;
      limit?: number;
    }) => api.searchSessions(params).then(res => res.data),
  });
}

export function useBulkDeleteSessions() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (sessionIds: string[]) => api.bulkDeleteSessions(sessionIds).then(res => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sessions'] });
    },
  });
}

export function useArchiveSession() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (sessionId: string) => api.archiveSession(sessionId).then(res => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sessions'] });
    },
  });
}

export function useSessionAnalytics() {
  return useQuery({
    queryKey: ['session-analytics'],
    queryFn: () => api.getSessionAnalytics().then(res => res.data),
  });
}

export function useActivityTimeline(days: number = 30) {
  return useQuery({
    queryKey: ['activity-timeline', days],
    queryFn: () => api.getActivityTimeline(days).then(res => res.data),
  });
}

export function useSessionAnalyticsDetail(sessionId: string) {
  return useQuery({
    queryKey: ['session-analytics', sessionId],
    queryFn: () => api.getSessionAnalyticsDetail(sessionId).then(res => res.data),
    enabled: !!sessionId,
  });
}