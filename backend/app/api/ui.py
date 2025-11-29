from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db, engine
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
def health_check():
    """Health check endpoint for Railway monitoring with PostgreSQL status"""
    
    status = "healthy"
    details = {}
    
    # Check database connection with details
    try:
        with engine.connect() as conn:
            # Get database type and version
            db_type = "PostgreSQL"
            
            # Get actual database version
            result = conn.execute(text("SELECT version()"))
            db_version = result.fetchone()[0]
            
            # Check table existence before counting
            inspector_query = text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            tables = [row[0] for row in conn.execute(inspector_query).fetchall()]
            
            table_stats = {}
            if 'agents' in tables:
                table_stats['agents'] = conn.execute(text("SELECT COUNT(*) FROM agents")).scalar()
            if 'chat_sessions' in tables:
                table_stats['sessions'] = conn.execute(text("SELECT COUNT(*) FROM chat_sessions")).scalar()
            if 'chat_messages' in tables:
                table_stats['messages'] = conn.execute(text("SELECT COUNT(*) FROM chat_messages")).scalar()

            details["database"] = {
                "type": db_type,
                "version": db_version.split(",")[0],
                "status": "connected",
                "tables": table_stats
            }
                
    except Exception as e:
        status = "unhealthy"
        details["database"] = {
            "status": "failed",
            "error": str(e)
        }
    
    # Check ZAI API Config
    from app.core.config import settings
    if settings.ZAI_API_KEY:
        details["zai_api"] = {
            "status": "configured",
            "key_length": len(settings.ZAI_API_KEY)
        }
    else:
        status = "unhealthy"
        details["zai_api"] = {
            "status": "missing"
        }
    
    return {
        "status": status,
        "timestamp": datetime.utcnow().isoformat(),
        "details": details
    }