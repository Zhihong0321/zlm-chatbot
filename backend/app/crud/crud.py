from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from sqlalchemy.orm import joinedload
from typing import List, Optional
from app.models.models import Agent, ChatSession, ChatMessage, SessionKnowledge, AgentKnowledgeFile
from app.schemas.schemas import AgentCreate, AgentUpdate, ChatSessionCreate, ChatMessageCreate, SessionKnowledgeCreate, AgentKnowledgeFileCreate


def get_agent(db: Session, agent_id: int) -> Optional[Agent]:
    return db.query(Agent).filter(Agent.id == agent_id).first()


def get_agents(db: Session, skip: int = 0, limit: int = 100) -> List[Agent]:
    return db.query(Agent).offset(skip).limit(limit).all()


def create_agent(db: Session, agent: AgentCreate) -> Agent:
    db_agent = Agent(**agent.dict())
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent


def update_agent(db: Session, agent_id: int, agent: AgentUpdate) -> Optional[Agent]:
    db_agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not db_agent:
        return None
    
    update_data = agent.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_agent, key, value)
    
    db.commit()
    db.refresh(db_agent)
    return db_agent


def delete_agent(db: Session, agent_id: int) -> bool:
    db_agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not db_agent:
        return False
    
    db.delete(db_agent)
    safe_commit(db)
    return True


def safe_commit(db: Session):
    """Safely commit database operations"""
    try:
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e

def get_chat_session(db: Session, session_id: int) -> Optional[ChatSession]:
    return db.query(ChatSession).options(joinedload(ChatSession.agent)).filter(ChatSession.id == session_id).first()


def get_chat_sessions(db: Session, skip: int = 0, limit: int = 100, include_archived: bool = False) -> List[ChatSession]:
    # Don't eager load agent here to avoid SQL errors with limited select permissions
    # The schema will handle lazy loading if needed, or we can use join explicitly
    query = db.query(ChatSession)
    if not include_archived:
        query = query.filter(ChatSession.is_archived == False)
    
    # Add explicit join for sorting/filtering if needed, but keep it simple for now
    return query.order_by(desc(ChatSession.updated_at)).offset(skip).limit(limit).all()


def create_chat_session(db: Session, session: ChatSessionCreate) -> ChatSession:
    try:
        db_session = ChatSession(**session.dict())
        db.add(db_session)
        safe_commit(db)
        db.refresh(db_session)
        return db_session
    except Exception as e:
        raise e


def delete_chat_session(db: Session, session_id: int) -> bool:
    db_session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not db_session:
        return False
    
    # Delete associated messages and knowledge files
    db.query(ChatMessage).filter(ChatMessage.session_id == session_id).delete()
    db.query(SessionKnowledge).filter(SessionKnowledge.session_id == session_id).delete()
    
    db.delete(db_session)
    db.commit()
    return True


def archive_session(db: Session, session_id: int) -> Optional[ChatSession]:
    """Archive a session (soft delete)"""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        return None
    
    session.is_archived = True
    session.title = f"[ARCHIVED] {session.title}"
    db.commit()
    db.refresh(session)
    return session


def get_session_analytics(db: Session, session_id: int) -> Optional[dict]:
    """Get detailed analytics for a specific session"""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        return None
    
    # Message statistics
    messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).all()
    user_messages = [m for m in messages if m.role == 'user']
    assistant_messages = [m for m in messages if m.role == 'assistant']
    
    # Token usage
    total_tokens = 0
    for msg in messages:
        if msg.token_usage:
            total_tokens += msg.token_usage.get('total_tokens', 0)
    
    return {
        "session_id": session.id,
        "title": session.title,
        "message_count": len(messages),
        "user_message_count": len(user_messages),
        "assistant_message_count": len(assistant_messages),
        "total_tokens_used": total_tokens,
        "knowledge_files_count": len(session.knowledge_files),
        "created_at": session.created_at,
        "updated_at": session.updated_at
    }


def create_chat_message(db: Session, message: ChatMessageCreate) -> ChatMessage:
    try:
        db_message = ChatMessage(**message.dict())
        db.add(db_message)
        
        # Update session message count and updated_at
        session = db.query(ChatSession).filter(ChatSession.id == message.session_id).first()
        if session:
            session.message_count += 1
        
        db.commit()
        db.refresh(db_message)
        return db_message
    except Exception as e:
        db.rollback()
        raise e


def get_chat_messages(db: Session, session_id: int, skip: int = 0, limit: int = 1000) -> List[ChatMessage]:
    return db.query(ChatMessage).filter(ChatMessage.session_id == session_id).offset(skip).limit(limit).all()


def create_session_knowledge(db: Session, knowledge: SessionKnowledgeCreate) -> SessionKnowledge:
    db_knowledge = SessionKnowledge(**knowledge.dict())
    db.add(db_knowledge)
    db.commit()
    db.refresh(db_knowledge)
    return db_knowledge


def get_session_knowledge(db: Session, session_id: int) -> List[SessionKnowledge]:
    return db.query(SessionKnowledge).filter(SessionKnowledge.session_id == session_id).all()


# Agent Knowledge File Management CRUD
def get_agent_knowledge_file(db: Session, file_id: int) -> Optional[AgentKnowledgeFile]:
    return db.query(AgentKnowledgeFile).filter(AgentKnowledgeFile.id == file_id).first()


def get_agent_knowledge_files(db: Session, agent_id: int) -> List[AgentKnowledgeFile]:
    return db.query(AgentKnowledgeFile).filter(
        AgentKnowledgeFile.agent_id == agent_id,
        AgentKnowledgeFile.status == "active"
    ).order_by(desc(AgentKnowledgeFile.created_at)).all()


def create_agent_knowledge_file(db: Session, file: AgentKnowledgeFileCreate) -> AgentKnowledgeFile:
    db_file = AgentKnowledgeFile(**file.dict())
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file


def delete_agent_knowledge_file(db: Session, file_id: int, agent_id: int) -> bool:
    db_file = db.query(AgentKnowledgeFile).filter(
        AgentKnowledgeFile.id == file_id,
        AgentKnowledgeFile.agent_id == agent_id
    ).first()
    if not db_file:
        return False
    
    # Soft delete - mark as deleted instead of removing
    db_file.status = "deleted"
    db.commit()
    return True


def get_agent_with_files(db: Session, agent_id: int) -> Optional[Agent]:
    return db.query(Agent).filter(Agent.id == agent_id).first()


def upload_file_to_zai(file_content: bytes, filename: str, api_key: str) -> dict:
    """Upload file to Z.ai Main API (only endpoint that supports file upload)"""
    import requests
    from datetime import datetime, timedelta
    
    url = "https://api.z.ai/api/paas/v4/files"  # Use main endpoint for file upload
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    files = {
        'file': (filename, file_content, 'text/plain'),
        'purpose': (None, 'agent')
    }
    
    try:
        response = requests.post(url, headers=headers, files=files)
        
        if response.status_code == 200:
            result = response.json()
            # Calculate expiration date (180 days from now)
            expires_at = datetime.utcnow() + timedelta(days=180)
            
            return {
                "success": True,
                "file_id": result.get('id'),
                "filename": result.get('filename'),
                "size": result.get('bytes'),
                "expires_at": expires_at.isoformat()
            }
        else:
            return {
                "success": False,
                "message": f"Upload failed: {response.status_code} - {response.text}"
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Upload error: {str(e)}"
        }