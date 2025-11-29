export interface Agent {
  id: string;
  name: string;
  description: string;
  model: string;
  system_prompt: string;
  temperature: number;
  created_at: string;
  updated_at: string;
}

export interface Session {
  id: string;
  title: string;
  agent_id: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface Message {
  id: string;
  session_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  created_at: string;
  model?: string;
  reasoning_content?: string;
  files?: Array<{
    filename: string;
    size: number;
    type: string;
  }>;
  token_usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
    cached_tokens?: number;
  };
}

export interface ChatRequest {
  message: string;
  agent_id?: string;
}

export interface ChatResponse {
  id: string;
  session_id: string;
  role: 'assistant';
  content: string;
  created_at: string;
  token_usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

export interface CreateAgentRequest {
  name: string;
  description: string;
  model: string;
  system_prompt: string;
  temperature?: number;
}

export interface CreateSessionRequest {
  title?: string;
  agent_id?: string;
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  version: string;
  database: string;
}