from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db, check_db_connection
from app.schemas.schemas import HealthResponse
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    from app.db.database import engine
    """Health check endpoint for Railway monitoring with PostgreSQL status"""
    
    status = "healthy"
    details = {}
    
    # Check database connection with details
    try:
        with engine.connect() as conn:
            # Get database type and version
            from app.core.config import settings
            db_type = "PostgreSQL"  # PRODUCTION: Always PostgreSQL
            
            # Get actual database version
            if db_type == "PostgreSQL":
                result = conn.execute(text("SELECT version()"))
                db_version = result.fetchone()[0]
                # Get table counts
                agents_count = conn.execute(text("SELECT COUNT(*) FROM agents")).scalar()
                sessions_count = conn.execute(text("SELECT COUNT(*) FROM chat_sessions")).scalar()
                messages_count = conn.execute(text("SELECT COUNT(*) FROM chat_messages")).scalar()
                
                details["database"] = {
                    "type": db_type,
                    "version": db_version.split(",")[0],
                    "status": "connected",
                    "tables": {
                        "agents": agents_count,
                        "sessions": sessions_count,
                        "messages": messages_count
                    }
                }
            else:
                details["database"] = {
                    "type": db_type,
                    "status": "connected"
                }
                
    except Exception as e:
        status = "unhealthy"
        details["database"] = {
            "status": "failed",
            "error": str(e)
        }
    
    # Check ZAI API
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
    
    # Overall status
    overall_status = "healthy" if status == "healthy" else "unhealthy"
    
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "details": details
    }