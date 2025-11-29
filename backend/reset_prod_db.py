import os
import sys
import logging
from sqlalchemy import create_engine, text, MetaData
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.models import Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reset_production_database():
    """
    DANGER: This script will DROP ALL TABLES in the production database 
    and recreate them from the current SQLAlchemy models.
    """
    db_url = settings.DATABASE_URL
    # Clean DB URL for psycopg2 if needed (e.g. remove query params not supported)
    if "?" in db_url and "schema=" in db_url:
        db_url = db_url.split("?")[0]
    
    if not db_url:
        logger.error("DATABASE_URL not set")
        sys.exit(1)
        
    if "postgresql" not in db_url:
        logger.error(f"This script is intended for PostgreSQL, but got: {db_url.split(':')[0]}")
        # Proceeding anyway if it's what the user wants, but warning logged.

    logger.warning(f"CONNECTING TO: {db_url.split('@')[1] if '@' in db_url else 'DB'}")
    logger.warning("!!! THIS WILL DELETE ALL DATA !!!")
    
    try:
        engine = create_engine(db_url)
        
        # 1. Drop all existing tables
        logger.info("Dropping all tables...")
        meta = MetaData()
        meta.reflect(bind=engine)
        meta.drop_all(bind=engine)
        logger.info("All tables dropped.")

        # 2. Create new tables from models
        logger.info("Creating new schema from models...")
        Base.metadata.create_all(bind=engine)
        logger.info("Schema created successfully.")
        
        # 3. Verify creation
        with engine.connect() as conn:
            inspector_query = text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            tables = [row[0] for row in conn.execute(inspector_query).fetchall()]
            logger.info(f"Created tables: {tables}")
            
            if 'agents' in tables:
                # Check for is_active column
                col_query = text("SELECT column_name FROM information_schema.columns WHERE table_name = 'agents' AND column_name = 'is_active'")
                if conn.execute(col_query).fetchone():
                    logger.info("✅ 'is_active' column confirmed in 'agents' table")
                else:
                    logger.error("❌ 'is_active' column MISSING in 'agents' table")
        
    except Exception as e:
        logger.error(f"Database reset failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    reset_production_database()
