import os
import sys
import logging
from sqlalchemy import create_engine, text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def emergency_zero_fallback():
    """
    EMERGENCY ZERO FALLBACK - API DOWN
    If the API is down, this script will attempt to fix the database schema by dropping all tables and recreating them.
    """
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL not found")
        sys.exit(1)

    # Clean DB URL for psycopg2/SQLAlchemy
    if "?" in database_url and "schema=" in database_url:
        database_url = database_url.split("?")[0]

    logger.warning(f"CONNECTING TO: {database_url.split('@')[1] if '@' in database_url else 'DB'}")
    logger.warning("!!! THIS WILL DELETE ALL DATA !!!")
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # 1. Drop all tables in correct order
            logger.info("Dropping tables...")
            conn.execute(text("DROP TABLE IF EXISTS chat_messages CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS session_knowledge CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS chat_sessions CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS agents CASCADE"))
            
            # 2. Recreate tables with minimal valid schema
            logger.info("Creating agents table...")
            conn.execute(text("""
                CREATE TABLE agents (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    system_prompt TEXT NOT NULL,
                    model VARCHAR(50) NOT NULL DEFAULT 'glm-4.5',
                    temperature FLOAT DEFAULT 0.7,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE
                )
            """))

            logger.info("Creating chat_sessions table...")
            conn.execute(text("""
                CREATE TABLE chat_sessions (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    agent_id INTEGER NOT NULL REFERENCES agents(id),
                    message_count INTEGER DEFAULT 0,
                    is_archived BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE
                )
            """))

            logger.info("Creating chat_messages table...")
            conn.execute(text("""
                CREATE TABLE chat_messages (
                    id SERIAL PRIMARY KEY,
                    session_id INTEGER NOT NULL REFERENCES chat_sessions(id),
                    role VARCHAR(20) NOT NULL,
                    content TEXT NOT NULL,
                    model VARCHAR(50),
                    reasoning_content TEXT,
                    token_usage JSON,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """))

            logger.info("Creating session_knowledge table...")
            conn.execute(text("""
                CREATE TABLE session_knowledge (
                    id SERIAL PRIMARY KEY,
                    session_id INTEGER NOT NULL REFERENCES chat_sessions(id),
                    filename VARCHAR(255) NOT NULL,
                    content TEXT NOT NULL,
                    file_size INTEGER,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            conn.commit()
            logger.info("✅ Database schema hard-reset successful")
            
    except Exception as e:
        logger.error(f"Database reset failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    emergency_zero_fallback()
