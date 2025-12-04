from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sys
import os
import logging

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

# Configure database - PostgreSQL ONLY for production
logger = logging.getLogger(__name__)

# Validate DATABASE_URL is PostgreSQL
if not settings.DATABASE_URL.startswith("postgresql"):
    raise ValueError("DATABASE_URL must be a PostgreSQL connection string for production")

# PostgreSQL configuration
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=5,
    max_overflow=10
)
logger.info("Using PostgreSQL database")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        db.close()
        raise
    finally:
        db.close()


def create_tables():
    """Create database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def check_db_connection():
    """Check database connection health"""
    try:
        with engine.connect() as conn:
            from sqlalchemy import text
            # Test basic connection
            conn.execute(text("SELECT 1"))
            logger.info("Database connection healthy")
            
            # Test MCP schema exists
            try:
                mcp_tables_result = conn.execute(text("""
                    SELECT COUNT(*) FROM information_schema.tables 
                    WHERE table_schema='public' 
                    AND table_name LIKE 'mcp_%'
                """)).scalar()
                logger.info(f"MCP tables found: {mcp_tables_result}")
                
                # Test critical MCP columns exist
                tools_column = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_name='chat_messages' 
                        AND column_name='tools_used'
                    )
                """)).scalar()
                
                mcp_responses_column = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_name='chat_messages' 
                        AND column_name='mcp_server_responses'
                    )
                """)).scalar()
                
                logger.info(f"MCP tools_used column exists: {tools_column}")
                logger.info(f"MCP mcp_server_responses column exists: {mcp_responses_column}")
                
                # Validate MCP schema completeness
                schema_ready = mcp_tables_result >= 4 and tools_column and mcp_responses_column
                if schema_ready:
                    logger.info("✅ MCP database schema is ready")
                else:
                    logger.warning("⚠️ MCP database schema is incomplete")
                
            except Exception as e:
                logger.warning(f"MCP schema validation failed: {e}")
                
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False