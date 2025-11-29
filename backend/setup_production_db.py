#!/usr/bin/env python3
"""
Production-ready database initializer for Railway PostgreSQL
"""
import os
import sys
from sqlalchemy import text

def setup_production_database():
    """Set up Railway PostgreSQL database with proper checks"""
    
    # Check we're in production environment
    if os.getenv("ENVIRONMENT") != "production" and not os.getenv("RAILWAY_ENVIRONMENT"):
        print("WARNING: Not in production environment. Use ENVIRONMENT=production or RAILWAY_ENVIRONMENT")
        return False
    
    # Get Railway PostgreSQL URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL not found in environment")
        return False
    
    print(f"Using database: {database_url.split('@')[1] if '@' in database_url else 'Unknown'}")
    
    # Import after environment check
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from app.db.database import engine, SessionLocal
    from app.models import models
    from app.crud import crud
    from app.schemas import schemas
    
    try:
        # Test database connection
        print("Testing database connection...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            db_version = result.fetchone()[0]
            print(f"PostgreSQL version: {db_version.split(',')[0]}")
        
        # Check existing tables and create missing ones only
        print("Checking database tables...")
        with engine.connect() as conn:
            # Check if agents table exists and has data
            try:
                result = conn.execute(text("SELECT COUNT(*) FROM agents"))
                agents_count = result.scalar()
                print(f"Found existing agents: {agents_count}")
            except Exception:
                print("Agents table doesn't exist, will create tables...")
                models.Base.metadata.create_all(bind=engine)
        
        # Create default data
        db = SessionLocal()
        
        try:
            # Check if agents exist
            agents_count = db.execute(text("SELECT COUNT(*) FROM agents")).scalar()
            print(f"Current agents count: {agents_count}")
            
            if agents_count == 0:
                print("Creating default agents...")
                
                # Code Assistant
                code_assistant = {
                    'name': 'Code Assistant',
                    'description': 'Expert in programming, debugging, and code optimization',
                    'system_prompt': 'You are a helpful coding assistant. Provide clear, concise programming advice and help users optimize their code.',
                    'model': 'glm-4.6',
                    'temperature': 0.3,
                    'is_active': True
                }
                db.execute(text("""
                    INSERT INTO agents (name, description, system_prompt, model, temperature, is_active, created_at, updated_at)
                    VALUES (:name, :description, :system_prompt, :model, :temperature, :is_active, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """), code_assistant)
                
                # General Helper  
                general_helper = {
                    'name': 'General Helper',
                    'description': 'Helps with various tasks and general questions',
                    'system_prompt': 'You are a helpful AI assistant. Be friendly, informative, and assist with a wide range of topics.',
                    'model': 'glm-4.5',
                    'temperature': 0.7,
                    'is_active': True
                }
                db.execute(text("""
                    INSERT INTO agents (name, description, system_prompt, model, temperature, is_active, created_at, updated_at)
                    VALUES (:name, :description, :system_prompt, :model, :temperature, :is_active, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """), general_helper)
                
                # Data Analyst
                data_analyst = {
                    'name': 'Data Analyst',
                    'description': 'Specializes in data analysis, visualization, and insights',
                    'system_prompt': 'You are a data analysis expert. Help users analyze data, create insights, and provide recommendations based on data patterns.',
                    'model': 'glm-4.5-air',
                    'temperature': 0.5,
                    'is_active': True
                }
                db.execute(text("""
                    INSERT INTO agents (name, description, system_prompt, model, temperature, is_active, created_at, updated_at)
                    VALUES (:name, :description, :system_prompt, :model, :temperature, :is_active, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """), data_analyst)
                
                print("Created 3 default agents")
            
            # Check if sessions exist
            sessions_count = db.execute(text("SELECT COUNT(*) FROM chat_sessions")).scalar()
            print(f"Current sessions count: {sessions_count}")
            
            if sessions_count == 0:
                # Get first agent
                agent = db.execute(text("SELECT id FROM agents LIMIT 1")).fetchone()
                if agent:
                    db.execute(text("""
                        INSERT INTO chat_sessions (title, agent_id, message_count, is_archived, created_at, updated_at)
                        VALUES ('Default Chat Session', :agent_id, 0, false, NOW(), NOW())
                    """), {'agent_id': agent[0]})
                    print("Created default chat session")
            
            db.commit()
            print("Database setup complete!")
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Database operation failed: {e}")
            return False
        finally:
            db.close()
            
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

if __name__ == "__main__":
    success = setup_production_database()
    if not success:
        sys.exit(1)
    print("✅ Production database ready")