from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.app.db.database import get_db
import os
import psycopg2
import subprocess
import sys

router = APIRouter(prefix="/diagnostic", tags=["diagnostic"])

@router.get("/schema")
def check_railway_schema(db: Session = Depends(get_db)):
    """Diagnostic endpoint to check actual Railway database schema"""
    try:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            return {"error": "DATABASE_URL not set", "status": "error"}
        
        # Use direct PostgreSQL connection for schema inspection
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Check all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        # Check chat_messages columns
        chat_cols = []
        if 'chat_messages' in tables:
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'chat_messages' 
                AND table_schema = 'public'
                ORDER BY ordinal_position
            """)
            chat_cols = [{"name": row[0], "type": row[1]} for row in cursor.fetchall()]
        
        # Check agents columns
        agent_cols = []
        if 'agents' in tables:
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'agents' 
                AND table_schema = 'public'
                ORDER BY ordinal_position
            """)
            agent_cols = [{"name": row[0], "type": row[1]} for row in cursor.fetchall()]
        
        # Test relationship query (the failing one)
        relationship_test = {"success": False, "error": None}
        try:
            cursor.execute("""
                SELECT a.id, a.name, cm.role 
                FROM agents a
                LEFT JOIN chat_sessions cs ON a.id = cs.agent_id  
                LEFT JOIN chat_messages cm ON cs.id = cm.session_id
                LIMIT 1
            """)
            result = cursor.fetchone()
            relationship_test = {"success": True, "result": result}
        except Exception as e:
            relationship_test = {"success": False, "error": str(e)}
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "database_url": db_url[:50] + "...",
            "tables": tables,
            "unexpected_error": relationship_test
        }
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@router.post("/setup-database")
def setup_database_manually():
    """Manual database setup endpoint - avoid slow Docker startup"""
    try:
        # Import and run the manual setup
        sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))
        from manual_db_setup import full_database_setup
        
        result = full_database_setup()
        return result
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@router.post("/run-migrations")
def run_migrations_only():
    """Just run migrations"""
    try:
        # Import and run just migrations
        sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))
        from manual_db_setup import run_migrations_safely
        
        success = run_migrations_safely()
        if success:
            return {"status": "success", "message": "Migrations completed"}
        else:
            return {"status": "failed", "message": "Migrations failed"}
            
    except Exception as e:
        return {"status": "error", "error": str(e)}

@router.post("/fix-schema-brute-force")
def fix_schema_brute_force():
    """Force create columns via raw SQL"""
    try:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            return {"status": "error", "message": "DATABASE_URL not set"}
            
        import psycopg2
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        results = []
        
        # 1. Add mcp_servers to agents
        try:
            cursor.execute("ALTER TABLE agents ADD COLUMN IF NOT EXISTS mcp_servers JSON;")
            results.append("Added mcp_servers to agents")
        except Exception as e:
            results.append(f"Failed agents: {e}")

        # 2. Add tools_used to chat_messages
        try:
            cursor.execute("ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS tools_used JSON;")
            results.append("Added tools_used to chat_messages")
        except Exception as e:
            results.append(f"Failed tools_used: {e}")

        # 3. Add mcp_server_responses to chat_messages
        try:
            cursor.execute("ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS mcp_server_responses JSON;")
            results.append("Added mcp_server_responses to chat_messages")
        except Exception as e:
            results.append(f"Failed mcp_server_responses: {e}")
            
        conn.close()
        return {"status": "success", "results": results}
        
    except Exception as e:
        return {"status": "error", "error": str(e)}
