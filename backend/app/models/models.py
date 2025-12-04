from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, JSON, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), onupdate=func.current_timestamp())


class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    system_prompt = Column(Text, nullable=False)
    model = Column(String(50), nullable=False, default="glm-4.5")
    temperature = Column(Float, default=0.7)
    is_active = Column(Boolean, default=True)
    mcp_servers = Column(JSON, nullable=True, comment='List of MCP server IDs associated with this agent')
    created_at = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), onupdate=func.current_timestamp())
    
    chat_sessions = relationship("ChatSession", back_populates="agent")
    knowledge_files = relationship("AgentKnowledgeFile", back_populates="agent", cascade="all, delete-orphan")
    mcp_server_assignments = relationship("AgentMCPServer", back_populates="agent", cascade="all, delete-orphan")


class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    message_count = Column(Integer, default=0)
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), onupdate=func.current_timestamp())
    
    agent = relationship("Agent", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    knowledge_files = relationship("SessionKnowledge", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    model = Column(String(50))
    reasoning_content = Column(Text)
    token_usage = Column(JSON)
    tools_used = Column(JSON, nullable=True, comment='List of MCP tools used in this message')
    mcp_server_responses = Column(JSON, nullable=True, comment='MCP server responses associated with this message')
    created_at = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    
    session = relationship("ChatSession", back_populates="messages")


class SessionKnowledge(Base):
    __tablename__ = "session_knowledge"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    file_size = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    
    session = relationship("ChatSession", back_populates="knowledge_files")


class AgentKnowledgeFile(Base):
    __tablename__ = "agent_knowledge_files"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    zai_file_id = Column(String(255), nullable=False, unique=True)  # Z.ai file ID
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_size = Column(Integer)
    file_type = Column(String(10))  # txt, pdf, doc, etc.
    purpose = Column(String(20), default="agent")  # agent, assistant, etc.
    status = Column(String(20), default="active")  # active, deleted, expired
    file_metadata = Column(JSON)  # Additional file metadata
    created_at = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), onupdate=func.current_timestamp())
    expires_at = Column(DateTime(timezone=True))  # When Z.ai file expires (180 days)
    
    agent = relationship("Agent", back_populates="knowledge_files")


# MCP Model Classes

class MCPServer(Base):
    __tablename__ = "mcp_servers"
    
    id = Column(String(255), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    command = Column(String(500), nullable=False)
    arguments = Column(JSON, nullable=True)
    environment = Column(JSON, nullable=True)
    working_directory = Column(String(1000), nullable=True)
    enabled = Column(Boolean, nullable=True, default=True)
    auto_start = Column(Boolean, nullable=True, default=True)
    health_check_interval = Column(Integer, nullable=True, default=30)
    status = Column(String(20), nullable=True, default='stopped')  # running, stopped, error, starting
    process_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), onupdate=func.current_timestamp())
    
    # Relationships
    agent_assignments = relationship("AgentMCPServer", back_populates="server", cascade="all, delete-orphan")
    logs = relationship("MCPServerLog", back_populates="server", cascade="all, delete-orphan")
    tool_usage = relationship("MCPToolUsage", back_populates="server", cascade="all, delete-orphan")


class MCPServerLog(Base):
    __tablename__ = "mcp_server_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    server_id = Column(String(255), ForeignKey("mcp_servers.id", ondelete='CASCADE'), nullable=False)
    level = Column(String(10), nullable=False)  # info, warning, error
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    
    server = relationship("MCPServer", back_populates="logs")


class AgentMCPServer(Base):
    __tablename__ = "agent_mcp_servers"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete='CASCADE'), nullable=False)
    server_id = Column(String(255), ForeignKey("mcp_servers.id", ondelete='CASCADE'), nullable=False)
    is_enabled = Column(Boolean, nullable=True, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), onupdate=func.current_timestamp())
    
    agent = relationship("Agent", back_populates="mcp_server_assignments")
    server = relationship("MCPServer", back_populates="agent_assignments")


class MCPToolUsage(Base):
    __tablename__ = "mcp_tool_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    server_id = Column(String(255), ForeignKey("mcp_servers.id", ondelete='CASCADE'), nullable=False)
    tool_name = Column(String(255), nullable=False)
    parameters = Column(JSON, nullable=True)
    response = Column(JSON, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    status = Column(String(20), nullable=True, default='success')  # success, error, timeout
    error_message = Column(Text, nullable=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete='SET NULL'), nullable=True)
    message_id = Column(Integer, ForeignKey("chat_messages.id", ondelete='SET NULL'), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    
    server = relationship("MCPServer", back_populates="tool_usage")
    session = relationship("ChatSession")


class MCPSystemMetrics(Base):
    __tablename__ = "mcp_system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_type = Column(String(50), nullable=False)  # server_count, running_count, tool_usage, response_time
    metric_value = Column(Float, nullable=False)
    metrics_data = Column(JSON, nullable=True)  # Additional metric details
    timestamp = Column(DateTime(timezone=True), server_default=func.current_timestamp())