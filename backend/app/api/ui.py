from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db, check_db_connection
from app.schemas.schemas import HealthResponse
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint for Railway monitoring"""
    
    status = "healthy"
    details = []
    
    # Check database connection
    if not check_db_connection():
        status = "unhealthy"
        details.append("Database connection failed")
    else:
        details.append("Database connection OK")
    
    # Check environment variables
    from app.core.config import settings
    if not settings.ZAI_API_KEY:
        status = "unhealthy"
        details.append("ZAI_API_KEY not configured")
    else:
        details.append("ZAI_API_KEY configured")
    
    # Log health check for monitoring
    logger.info(f"Health check: {status} - {', '.join(details)}")
    
    return HealthResponse(
        status=status if status == "healthy" else f"unhealthy: {'; '.join(details)}",
        timestamp=datetime.utcnow()
    )