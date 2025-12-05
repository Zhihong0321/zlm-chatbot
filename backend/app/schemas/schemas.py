from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class AgentBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    system_prompt: str
    model: str = "glm-4.5"
    temperature: float = Field(0.7, ge=0, le=2)


class AgentCreate(AgentBase):
    pass


class AgentUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0, le=2)


class Agent(AgentBase):
    id: int
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ChatSessionBase(BaseModel):
    title: str = Field(..., max_length=200)
    agent_id: int


class ChatSessionCreate(ChatSessionBase):
    pass


class ChatSession(ChatSessionBase):
    id: int
    message_count: int = 0
    is_archived: bool = False
    created_at: datetime
    updated_at: Optional[datetime]
    agent: Agent
    last_ai_response: Optional[str] = None
    
    class Config:
        from_attributes = True


class ChatMessageBase(BaseModel):
    role: str
    content: str
    model: Optional[str] = None
    reasoning_content: Optional[str] = None
    token_usage: Optional[Dict[str, Any]] = None
    tools_used: Optional[List[Dict[str, Any]]] = None
    mcp_server_responses: Optional[Dict[str, Any]] = None


class ChatMessageCreate(ChatMessageBase):
    session_id: int


class ChatMessage(ChatMessageBase):
    id: int
    session_id: int
    token_usage: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class SessionKnowledgeBase(BaseModel):
    filename: str
    content: str
    file_size: Optional[int] = None


class SessionKnowledgeCreate(SessionKnowledgeBase):
    session_id: int


class SessionKnowledge(SessionKnowledgeBase):
    id: int
    session_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    message: str
    session_id: int
    agent_id: Optional[int] = None


class MessageRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    message: str
    reasoning_content: Optional[str] = None
    model: str
    token_usage: Optional[Dict[str, Any]] = None  # CRITICAL: Made optional to prevent serialization errors


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str = "1.0.0"


class SessionAnalytics(BaseModel):
    session_id: int
    title: str
    message_count: int
    user_message_count: int
    assistant_message_count: int
    total_tokens_used: int
    knowledge_files_count: int
    created_at: datetime
    updated_at: Optional[datetime]


class SessionAnalyticsResponse(BaseModel):
    total_sessions: int
    total_messages: int
    avg_messages_per_session: float
    sessions_by_agent: List[Dict[str, Any]]
    recent_sessions_7_days: int


class ActivityTimelineItem(BaseModel):
    date: str
    sessions_created: int
    messages_sent: int


class BulkDeleteRequest(BaseModel):
    session_ids: List[int]


class BulkDeleteResponse(BaseModel):
    message: str


# File Management Schemas
class AgentKnowledgeFileBase(BaseModel):
    zai_file_id: str
    filename: str
    original_filename: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    purpose: str = "agent"
    status: str = "active"
    file_metadata: Optional[Dict[str, Any]] = None


class AgentKnowledgeFileCreate(AgentKnowledgeFileBase):
    agent_id: int


class AgentKnowledgeFileUpload(BaseModel):
    agent_id: int
    purpose: str = "agent"


class AgentKnowledgeFileResponse(AgentKnowledgeFileBase):
    id: int
    agent_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    expires_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class FileUploadResponse(BaseModel):
    success: bool
    file_id: Optional[str] = None
    filename: Optional[str] = None
    message: str
    size: Optional[int] = None


class AgentWithFiles(Agent):
    knowledge_files: List[AgentKnowledgeFileResponse] = []
    
    class Config:
        from_attributes = True


class ChatWithKnowledgeRequest(BaseModel):
    message: str
    session_id: int
    agent_id: Optional[int] = None
    use_knowledge: bool = True
    file_context: Optional[str] = None  # Optional specific file to reference