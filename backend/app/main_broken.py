from fastapi import FastAPI
import os
import sys
import logging

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.core.middleware import setup_middleware
from app.api.api_v1 import api_router
from app.db.database import engine, create_tables, check_db_connection
from app.models import models

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Chatbot API Server",
    description="Z.ai GLM Chatbot API with Knowledge Management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Setup middleware
setup_middleware(app)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("Starting Chatbot API Server...")
    
    # Create database tables
    try:
        create_tables()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Shutting down Chatbot API Server...")


@app.get("/")
def root():
    return {"message": "Chatbot API Server", "version": "1.0.0"}


@app.get("/health")
def health_check():
    """Simple health check"""
    return {"status": "healthy", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)