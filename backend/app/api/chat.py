from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import ChatMessage
from app.schemas.schemas import ChatMessageCreate, ChatMessage as ChatMessageSchema, ChatResponse, ChatRequest, MessageRequest
from app.crud.crud import create_chat_message, get_chat_session, get_session_knowledge
from app.core.zai_client import chat_with_zai
from typing import Dict, Any
import json

from fastapi import HTTPException

router = APIRouter()


@router.post("/{session_id}/messages", response_model=ChatMessageSchema)
def send_message(
    session_id: int, 
    request: MessageRequest,
    db: Session = Depends(get_db)
):
    try:
        # Explicitly query session and agent separately to avoid lazy loading issues
        from app.models.models import ChatSession, Agent
        
        db_session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if db_session is None:
            raise HTTPException(status_code=404, detail="Session not found")
            
        # Get agent explicitly
        agent = db.query(Agent).filter(Agent.id == db_session.agent_id).first()
        if not agent:
             raise HTTPException(status_code=404, detail="Agent for session not found")
        
        message = request.message
        
        # Create user message
        user_message = ChatMessageCreate(
            session_id=session_id,
            role="user",
            content=message
        )
        db_message = create_chat_message(db=db, message=user_message)
        
        # Get knowledge context  
        knowledge_files = get_session_knowledge(db, session_id=session_id)
        
        # Build context
        context = f"Agent: {agent.name}\nSystem Prompt: {agent.system_prompt}"
        
        if knowledge_files:
            context += "\n\nKnowledge Context:\n"
            for kf in knowledge_files:
                context += f"\n--- {kf.filename} ---\n{kf.content}\n"
        
        # Get AI response
        try:
            ai_response = chat_with_zai(
                message=message,
                system_prompt=context,
                model=agent.model,
                temperature=agent.temperature
            )
            
            # Create assistant message
            assistant_message = ChatMessageCreate(
                session_id=session_id,
                role="assistant",
                content=ai_response["content"],
                reasoning_content=ai_response.get("reasoning_content"),
                model=ai_response["model"],
                token_usage=ai_response["token_usage"]
            )
            db_assistant_message = create_chat_message(db=db, message=assistant_message)
            
            return db_assistant_message
        except Exception as e:
            # Rollback is handled by global exception handler or dependency if not done here
            # But explicit is better for transaction errors
            db.rollback()
            import logging
            logging.getLogger(__name__).error(f"Chat error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Chat processing error: {str(e)}")
    except HTTPException:
        # HTTP exceptions are fine, just re-raise
        raise
    except Exception as e:
        # Fallback for any other error in the route
        db.rollback()
        import logging
        logging.getLogger(__name__).error(f"Internal chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{session_id}/upload")
async def upload_knowledge_file(
    session_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Verify session exists
    db_session = get_chat_session(db, session_id=session_id)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check file size (50KB limit)
    max_size = 50 * 1024  # 50KB
    content = await file.read()
    
    if len(content) > max_size:
        raise HTTPException(
            status_code=413, 
            detail="File size exceeds 50KB limit"
        )
    
    # Decode content
    try:
        text_content = content.decode('utf-8')
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="File must be text-based (UTF-8 encoded)"
        )
    
    # Create knowledge record
    from app.schemas.schemas import SessionKnowledgeCreate
    from app.crud.crud import create_session_knowledge
    
    knowledge = SessionKnowledgeCreate(
        session_id=session_id,
        filename=file.filename,
        content=text_content,
        file_size=len(content)
    )
    
    db_knowledge = create_session_knowledge(db=db, knowledge=knowledge)
    
    return {
        "message": "File uploaded successfully",
        "knowledge": db_knowledge
    }


@router.post("/chat", response_model=ChatResponse)
def chat_with_agent(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        # Verify session exists
        from app.models.models import ChatSession, Agent
        db_session = db.query(ChatSession).filter(ChatSession.id == request.session_id).first()
        
        if db_session is None:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get agent info
        agent = None
        if request.agent_id:
             agent = db.query(Agent).filter(Agent.id == request.agent_id).first()
             if not agent:
                raise HTTPException(status_code=404, detail="Agent not found")
        else:
             # Explicitly load agent from session relation ID
             agent = db.query(Agent).filter(Agent.id == db_session.agent_id).first()
             if not agent:
                # Fallback if data is corrupted
                 raise HTTPException(status_code=404, detail="Agent for session not found")
        
        # Get knowledge context
        knowledge_files = get_session_knowledge(db, session_id=request.session_id)
        
        # Build context
        context = f"Agent: {agent.name}\nSystem Prompt: {agent.system_prompt}"
        
        if knowledge_files:
            context += "\n\nKnowledge Context:\n"
            for kf in knowledge_files:
                context += f"\n--- {kf.filename} ---\n{kf.content}\n"
        
        # Get AI response
        try:
            import time
            import logging
            logger = logging.getLogger(__name__)
            
            start_time = time.time()
            
            ai_response = chat_with_zai(
                message=request.message,
                system_prompt=context,
                model=agent.model,
                temperature=agent.temperature
            )
            
            end_time = time.time()
            duration = end_time - start_time
            logger.info(f"Z.ai API Latency: {duration:.2f}s. Model: {agent.model}")
            
            # Store user message
            user_message = ChatMessageCreate(
                session_id=request.session_id,
                role="user",
                content=request.message
            )
            create_chat_message(db=db, message=user_message)
            
            # Store assistant message
            assistant_message = ChatMessageCreate(
                session_id=request.session_id,
                role="assistant",
                content=ai_response["content"],
                model=ai_response["model"],
                token_usage=ai_response["token_usage"]
            )
            create_chat_message(db=db, message=assistant_message)
            
            return ChatResponse(
                message=ai_response["content"],
                reasoning_content=ai_response.get("reasoning_content"),
                model=ai_response["model"],
                token_usage=ai_response["token_usage"] or {}
            )
            
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import logging
        logging.getLogger(__name__).error(f"Internal chat error (playground): {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")