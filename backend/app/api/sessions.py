from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, or_, and_
from typing import List, Optional, Dict, Any
from app.db.database import get_db
from app.models.models import ChatSession, ChatMessage
from app.schemas.schemas import (
    ChatSession as ChatSessionSchema, ChatSessionCreate, ChatMessage as ChatMessageSchema, SessionKnowledge,
    SessionAnalyticsResponse, ActivityTimelineItem, BulkDeleteRequest, BulkDeleteResponse
)
from app.crud.crud import (
    create_chat_session, get_chat_session, get_chat_sessions, delete_chat_session,
    get_chat_messages, create_chat_message, get_session_knowledge, archive_session,
    get_session_analytics
)

router = APIRouter()


@router.post("/", response_model=ChatSessionSchema)
def create_session_endpoint(session: ChatSessionCreate, db: Session = Depends(get_db)):
    return create_chat_session(db=db, session=session)


@router.get("/", response_model=List[ChatSessionSchema])
def read_sessions(
    skip: int = 0, 
    limit: int = 100, 
    agent_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    try:
        if agent_id:
            sessions = db.query(ChatSession).options(joinedload(ChatSession.agent)).filter(ChatSession.agent_id == agent_id).offset(skip).limit(limit).all()
        else:
            sessions = get_chat_sessions(db, skip=skip, limit=limit)
        
        # Add last AI response to session data for frontend display
        for session in sessions:
            # Get last assistant message as session title fallback
            last_messages = db.query(ChatMessage).filter(
                ChatMessage.session_id == session.id,
                ChatMessage.role == 'assistant'
            ).order_by(ChatMessage.created_at.desc()).limit(1).first()
            
            session.last_ai_response = last_messages.content[:100] if last_messages else None
        
        return sessions
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/search", response_model=List[ChatSessionSchema])
def search_sessions(
    q: str = Query(..., description="Search query"),
    agent_id: Optional[int] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    min_messages: Optional[int] = Query(None),
    skip: int = Query(0),
    limit: int = Query(100),
    db: Session = Depends(get_db)
):
    """Search sessions with advanced filters"""
    query = db.query(ChatSession)
    
    # Text search in title and messages
    if q:
        # Join with messages for content search
        query = query.join(ChatMessage, ChatSession.id == ChatMessage.session_id, isouter=True)
        query = query.filter(
            or_(
                ChatSession.title.ilike(f"%{q}%"),
                ChatMessage.content.ilike(f"%{q}%")
            )
        ).distinct()
    
    # Agent filter
    if agent_id:
        query = query.filter(ChatSession.agent_id == agent_id)
    
    # Date range filter
    if date_from:
        query = query.filter(ChatSession.created_at >= date_from)
    if date_to:
        query = query.filter(ChatSession.created_at <= date_to)
    
    # Message count filter
    if min_messages:
        query = query.filter(ChatSession.message_count >= min_messages)
    
    return query.offset(skip).limit(limit).all()


@router.get("/analytics/summary", response_model=SessionAnalyticsResponse)
def get_sessions_analytics(db: Session = Depends(get_db)):
    """Get analytics summary for all sessions"""
    # Total sessions
    total_sessions = db.query(func.count(ChatSession.id)).filter(ChatSession.is_archived == False).scalar() or 0
    
    # Total messages
    total_messages = db.query(func.count(ChatMessage.id)).scalar() or 0
    
    # Messages per session
    avg_messages_per_session = (
        db.query(func.avg(ChatSession.message_count))
        .filter(ChatSession.is_archived == False)
        .scalar() or 0
    )
    
    # Sessions by agent
    sessions_by_agent = db.query(
        ChatSession.agent_id,
        func.count(ChatSession.id).label('count')
    ).filter(ChatSession.is_archived == False).group_by(ChatSession.agent_id).all()
    
    # Recent activity (sessions in last 7 days) - PostgreSQL compatible
    from sqlalchemy import text
    recent_sessions = db.execute(text("""
        SELECT COUNT(*) FROM chat_sessions 
        WHERE created_at >= NOW() - INTERVAL '7 days' 
        AND is_archived = false
    """)).scalar() or 0
    
    return SessionAnalyticsResponse(
        total_sessions=total_sessions,
        total_messages=total_messages,
        avg_messages_per_session=round(avg_messages_per_session, 2),
        sessions_by_agent=[{"agent_id": aid, "count": count} for aid, count in sessions_by_agent],
        recent_sessions_7_days=recent_sessions
    )


@router.get("/activity/timeline", response_model=List[ActivityTimelineItem])
def get_activity_timeline(
    days: int = Query(30, description="Number of days to look back"),
    db: Session = Depends(get_db)
):
    """Get activity timeline showing session creation over time"""
    timeline = (
        db.query(
            func.date(ChatSession.created_at).label('date'),
            func.count(ChatSession.id).label('sessions'),
            func.sum(ChatSession.message_count).label('messages')
        )
        .filter(ChatSession.created_at >= text(f"NOW() - INTERVAL '{days} days'"))
        .filter(ChatSession.is_archived == False)
        .group_by(func.date(ChatSession.created_at))
        .order_by(func.date(ChatSession.created_at))
        .all()
    )
    
    return [
        ActivityTimelineItem(
            date=str(date),
            sessions_created=sessions,
            messages_sent=messages or 0
        )
        for date, sessions, messages in timeline
    ]


@router.get("/{session_id}", response_model=ChatSessionSchema)
def read_session(session_id: int, db: Session = Depends(get_db)):
    db_session = get_chat_session(db, session_id=session_id)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_session


@router.delete("/{session_id}")
def delete_session_endpoint(session_id: int, db: Session = Depends(get_db)):
    if not delete_chat_session(db, session_id=session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session deleted successfully"}


@router.get("/{session_id}/history", response_model=List[ChatMessageSchema])
def get_session_history(session_id: int, db: Session = Depends(get_db)):
    # Verify session exists
    db_session = get_chat_session(db, session_id=session_id)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = get_chat_messages(db, session_id=session_id)
    return messages


@router.get("/{session_id}/knowledge", response_model=List[SessionKnowledge])
def get_session_knowledge_endpoint(session_id: int, db: Session = Depends(get_db)):
    # Verify session exists
    db_session = get_chat_session(db, session_id=session_id)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return get_session_knowledge(db, session_id=session_id)


# Moved /search, /analytics/summary, /activity/timeline to top to avoid path conflict


@router.post("/bulk-delete", response_model=BulkDeleteResponse)
def bulk_delete_sessions(request: BulkDeleteRequest, db: Session = Depends(get_db)):
    """Delete multiple sessions at once"""
    deleted_count = db.query(ChatSession).filter(ChatSession.id.in_(request.session_ids)).delete(synchronize_session=False)
    db.commit()
    return BulkDeleteResponse(message=f"Successfully deleted {deleted_count} sessions")


@router.post("/{session_id}/archive")
def archive_session_endpoint(session_id: int, db: Session = Depends(get_db)):
    """Archive a session (soft delete)"""
    session = archive_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"message": "Session archived successfully"}


@router.get("/{session_id}/analytics")
def get_session_analytics_endpoint(session_id: int, db: Session = Depends(get_db)):
    """Get detailed analytics for a specific session"""
    analytics = get_session_analytics(db, session_id)
    if not analytics:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return analytics