from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, JSON, Boolean
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
    created_at = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), onupdate=func.current_timestamp())
    
    chat_sessions = relationship("ChatSession", back_populates="agent")
    knowledge_files = relationship("AgentKnowledgeFile", back_populates="agent", cascade="all, delete-orphan")


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
    metadata = Column(JSON)  # Additional file metadata
    created_at = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), onupdate=func.current_timestamp())
    expires_at = Column(DateTime(timezone=True))  # When Z.ai file expires (180 days)
    
    agent = relationship("Agent", back_populates="knowledge_files")