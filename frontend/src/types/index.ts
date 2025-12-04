export interface Agent {
  id: string;
  name: string;
  description: string;
  model: string;
  system_prompt: string;
  temperature: number;
  created_at: string;
  updated_at: string;
  mcp_servers?: string[];
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
  created_at: string;
  updated_at: string;
}

export interface CreateAgentRequest {
  name: string;
  description: string;
  model: string;
  system_prompt: string;
  temperature: number;
  mcp_servers?: string[];
}

export interface UpdateAgentRequest {
  name?: string;
  description?: string;
  model?: string;
  system_prompt?: string;
  temperature?: number;
  mcp_servers?: string[];
}

export interface CreateSessionRequest {
  title: string;
  agent_id: string;
}

export interface ChatRequest {
  message: string;
  agent_id?: string;
  session_id?: string;
}

export interface ChatResponse {
  message: string;
  session_id?: string;
  model: string;
  token_usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
  reasoning_content?: string;
  tools_used?: string[];
}

export interface FileUploadResponse {
  id: string;
  filename: string;
  url: string;
  size: number;
  type: string;
}
