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
            conn.execute(text("SELECT 1"))
        logger.info("Database connection healthy")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False