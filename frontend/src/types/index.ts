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
    id: string;
    filename: string;
    original_filename: string;
    file_size: number;
    file_type: string;
    status: string;
  }>;
  message_files?: Array<{
    id: string;
    file_id: string;
    message_id: string;
  }>;
  token_usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
  tools_used?: string[];
  mcp_server_responses?: any;
}
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

export interface UpdateAgentRequest {
  name?: string;
  description?: string;
  model?: string;
  system_prompt?: string;
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

// File Management Types
export interface AgentKnowledgeFile {
  id: string;
  agent_id: string;
  zai_file_id: string;
  filename: string;
  original_filename: string;
  file_size: number;
  file_type: string;
  purpose: string;
  status: string;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at?: string;  
  expires_at?: string;
}

export interface AgentWithFiles extends Agent {
  knowledge_files: AgentKnowledgeFile[];
}

export interface FileUploadResponse {
  success: boolean;
  file_id?: string;
  filename?: string;
  message: string;
  size?: number;
}

export interface FileUploadRequest {
  agent_id: string;
  purpose?: string;
}