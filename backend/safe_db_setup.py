#!/usr/bin/env python3
"""
Safe production database initializer - preserves existing data
"""
import os
import sys
from sqlalchemy import text

def safe_database_setup():
    """Set up Railway PostgreSQL without wiping existing data"""
    
    # Check environment
    if not (os.getenv("ENVIRONMENT") == "production" or os.getenv("RAILWAY_ENVIRONMENT")):
        print("WARNING: Not in production environment")
        return False
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL not found")
        return False
    
    print(f"Connecting to existing PostgreSQL database...")
    
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from app.db.database import engine, SessionLocal
    from app.models import models
    
    try:
        with engine.connect() as conn:
            # Test connection and get version
            result = conn.execute(text("SELECT version()"))
            db_version = result.fetchone()[0]
            print(f"Connected to PostgreSQL: {db_version.split(',')[0]}")
            
            # Check existing tables
            tables = conn.execute(text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            """)).fetchall()
            table_names = [t[0] for t in tables]
            print(f"Existing tables: {table_names}")
            
            # Check data counts
            for table in ['agents', 'chat_sessions', 'chat_messages', 'session_knowledge']:
                if table in table_names:
                    count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                    print(f"  {table}: {count} records")
            
            # Only create tables that don't exist
            missing_tables = []
            for table in ['agents', 'chat_sessions', 'chat_messages', 'session_knowledge']:
                if table not in table_names:
                    missing_tables.append(table)
            
            if missing_tables:
                print(f"Creating missing tables: {missing_tables}")
                models.Base.metadata.create_all(bind=engine)  # Create all tables safely - SQLAlchemy handles existing tables
            
            db = SessionLocal()
            
            try:
                # Only add default agents if table is empty
                agents_count = db.execute(text("SELECT COUNT(*) FROM agents")).scalar()
                if agents_count == 0:
                    print("Adding default agents (no existing agents found)...")
                    
                    # Code Assistant
                    db.execute(text("""
                        INSERT INTO agents (name, description, system_prompt, model, temperature, is_active, created_at, updated_at)
                        VALUES (:name, :description, :system_prompt, :model, :temperature, :is_active, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """), {
                        'name': 'Code Assistant',
                        'description': 'Expert in programming, debugging, and code optimization',
                        'system_prompt': 'You are a helpful coding assistant. Provide clear, concise programming advice.',
                        'model': 'glm-4.6',
                        'temperature': 0.3,
                        'is_active': True
                    })
                    
                    # General Helper
                    db.execute(text("""
                        INSERT INTO agents (name, description, system_prompt, model, temperature, is_active, created_at, updated_at)
                        VALUES (:name, :description, :system_prompt, :model, :temperature, :is_active, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """), {
                        'name': 'General Helper',
                        'description': 'Helps with various tasks and general questions',
                        'system_prompt': 'You are a helpful AI assistant. Be friendly and informative.',
                        'model': 'glm-4.5',
                        'temperature': 0.7,
                        'is_active': True
                    })
                    
                    # Data Analyst
                    db.execute(text("""
                        INSERT INTO agents (name, description, system_prompt, model, temperature, is_active, created_at, updated_at)
                        VALUES (:name, :description, :system_prompt, :model, :temperature, :is_active, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """), {
                        'name': 'Data Analyst',
                        'description': 'Specializes in data analysis, visualization, and insights',
                        'system_prompt': 'You are a data analysis expert. Help analyze data and provide insights.',
                        'model': 'glm-4.5-air',
                        'temperature': 0.5,
                        'is_active': True
                    })
                    
                    db.commit()
                    print("Added 3 default agents")
                else:
                    print(f"Preserving existing {agents_count} agents")
                
                # Only add default session if no sessions exist
                sessions_count = db.execute(text("SELECT COUNT(*) FROM chat_sessions")).scalar()
                if sessions_count == 0:
                    # Get first agent
                    agent = db.execute(text("SELECT id FROM agents LIMIT 1")).fetchone()
                    if agent:
                        db.execute(text("""
                            INSERT INTO chat_sessions (title, agent_id, message_count, is_archived, created_at, updated_at)
                            VALUES ('Default Chat Session', :agent_id, 0, false, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                        """), {'agent_id': agent[0]})
                        db.commit()
                        print("Created default chat session")
                else:
                    print(f"Preserving existing {sessions_count} chat sessions")
                    
            except Exception as e:
                db.rollback()
                print(f"Database operation failed: {e}")
                return False
            finally:
                db.close()
            
            print("✅ Database setup completed - existing data preserved")
            return True
            
    except Exception as e:
        print(f"Database setup failed: {e}")
        return False

if __name__ == "__main__":
    success = safe_database_setup()
    if not success:
        sys.exit(1)
    print("✅ Safe database setup complete")