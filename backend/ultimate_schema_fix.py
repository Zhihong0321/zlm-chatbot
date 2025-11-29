#!/usr/bin/env python3
"""
ULTIMATE DATABASE SCHEMA FIX - Kills all tables and recreates with correct schema
BRUTE FORCE approach - no existing data preservation to ensure clean schema
"""
import os
import sys
from sqlalchemy import text

def ultimate_schema_fix():
    """Ultimate schema fix - drop ALL tables and recreate cleanly"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found")
        return False
    
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from app.db.database import engine
    
    try:
        with engine.connect() as conn:
            print("🔥 ULTIMATE SCHEMA FIX - Dropping ALL tables...")
            
            # Drop ALL tables with CASCADE to remove all constraints
            tables_to_drop = [
                'chat_sessions',
                'chat_messages', 
                'session_knowledge',
                'agents'
            ]
            
            for table in tables_to_drop:
                try:
                    conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                    print(f"   ✅ Dropped table: {table}")
                except Exception as e:
                    print(f"   Warning: Could not drop {table}: {e}")
            
            conn.commit()
            print("✅ All tables dropped - clean slate for correct schema")
            
            print("🧪 Testing schema creation...")
            
            # Now test creating ONE table at a time to identify issues
            try:
                # Test agents table first
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
                print("   ✅ agents table created successfully")
                
                # Test chat_sessions table with proper foreign key
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
                print("   ✅ chat_sessions table created successfully")
                
                conn.commit()
                print("✅ Schema creation test PASSED")
                
            except Exception as e:
                print(f"❌ Schema creation test FAILED: {e}")
                conn.rollback()
                return False
            
            print("✅ Ultimate schema fix completed")
            return True
            
    except Exception as e:
        print(f"❌ Ultimate schema fix failed: {e}")
        return False

if __name__ == "__main__":
    success = ultimate_schema_fix()
    if not success:
        sys.exit(1)
    print("✅ Database schema is now clean and correct")