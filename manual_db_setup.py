#!/usr/bin/env python3
"""
Manual Database Setup for Railway
Run this via API endpoint to avoid slow Docker startup
"""

import os
import subprocess
import psycopg2
from sqlalchemy import create_engine, text

def run_migrations_safely():
    """Run database migrations with error handling"""
    print("🔧 Running database migrations...")
    
    try:
        # Change to backend directory and run alembic
        # Try running alembic directly from the current directory if backend fails
        try:
            print(f"   Running Alembic from: {os.path.join(os.getcwd(), 'backend')}")
            result = subprocess.run(
                ["alembic", "upgrade", "heads"],
                cwd=os.path.join(os.getcwd(), "backend"),
                capture_output=True,
                text=True,
                timeout=60
            )
        except FileNotFoundError:
            # Fallback to try running from current directory if structure is different
            print(f"   Backend directory not found, trying current directory: {os.getcwd()}")
            result = subprocess.run(
                ["alembic", "upgrade", "heads"],
                cwd=os.getcwd(),
                capture_output=True,
                text=True,
                timeout=60
            )
        
        if result.returncode == 0:
            print("✅ Migrations completed successfully")
            return True
        else:
            print(f"❌ Migration failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Migration error: {e}")
        return False

def check_database_connectivity():
    """Quick connectivity test"""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        return False, "DATABASE_URL not set"
    
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        return True, "Connectivity OK"
        
    except Exception as e:
        return False, f"Connection failed: {e}"

def check_required_tables():
    """Check if required tables exist"""
    db_url = os.getenv("DATABASE_URL")
    engine = create_engine(db_url)
    
    try:
        with engine.connect() as conn:
            # Check critical tables
            critical_tables = ['agents', 'chat_sessions', 'chat_messages']
            
            results = {}
            for table in critical_tables:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    results[table] = count
                except Exception as e:
                    results[table] = f"ERROR: {e}"
            
            return results
            
    except Exception as e:
        return {"error": f"Database check failed: {e}"}

def check_required_columns():
    """Check MCP columns in key tables"""
    db_url = os.getenv("DATABASE_URL")
    
    try:
        with psycopg2.connect(db_url) as conn:
            cursor = conn.cursor()
            
            # Check chat_messages for MCP columns
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'chat_messages' 
                AND table_schema = 'public'
                AND column_name IN ('tools_used', 'mcp_server_responses')
            """)
            chat_cols = [row[0] for row in cursor.fetchall()]
            
            # Check agents for MCP column
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'agents' 
                AND table_schema = 'public'
                AND column_name = 'mcp_servers'
            """)
            agent_cols = [row[0] for row in cursor.fetchall()]
            
            return {
                "chat_messages_mcp_columns": chat_cols,
                "agents_mcp_column": agent_cols
            }
            
    except Exception as e:
        return {"error": f"Column check failed: {e}"}

def full_database_setup():
    """Complete database health check and setup"""
    print("🚂 MANUAL DATABASE SETUP & HEALTH CHECK")
    print("=" * 50)
    
    # Step 1: Connectivity
    print("1️⃣ Testing database connectivity...")
    success, message = check_database_connectivity()
    if success:
        print(f"   ✅ {message}")
    else:
        print(f"   ❌ {message}")
        return {"status": "failed", "step": "connectivity", "error": message}
    
    # Step 2: Run migrations
    print("\n2️⃣ Running database migrations...")
    if not run_migrations_safely():
        return {"status": "failed", "step": "migrations"}
    
    # Step 3: Check tables
    print("\n3️⃣ Checking required tables...")
    tables = check_required_tables()
    if "error" in tables:
        print(f"   ❌ {tables['error']}")
        return {"status": "failed", "step": "tables_check", "error": tables["error"]}
    
    for table, count in tables.items():
        if isinstance(count, int):
            print(f"   ✅ {table}: {count} records")
        else:
            print(f"   ❌ {table}: {count}")
            return {"status": "failed", "step": "table_issue", "table": table, "error": count}
    
    # Step 4: Check MCP columns
    print("\n4️⃣ Checking MCP columns...")
    columns = check_required_columns()
    if "error" in columns:
        print(f"   ❌ {columns['error']}")
        return {"status": "failed", "step": "columns_check", "error": columns["error"]}
    
    chat_cols = columns.get("chat_messages_mcp_columns", [])
    agent_cols = columns.get("agents_mcp_column", [])
    
    print(f"   ✅ Chat messages MCP columns: {chat_cols}")
    print(f"   ✅ Agents MCP column: {agent_cols}")
    
    # Check if all required columns exist
    required_chat_cols = ['tools_used', 'mcp_server_responses']
    if all(col in chat_cols for col in required_chat_cols) and agent_cols:
        print("\n🎉 DATABASE SETUP COMPLETE - All requirements satisfied!")
        return {"status": "success"}
    else:
        missing = []
        if 'tools_used' not in chat_cols:
            missing.append('tools_used in chat_messages')
        if 'mcp_server_responses' not in chat_cols:
            missing.append('mcp_server_responses in chat_messages')
        if not agent_cols:
            missing.append('mcp_servers in agents')
        
        return {
            "status": "failed", 
            "step": "missing_columns", 
            "missing": missing,
            "chat_columns": chat_cols,
            "agent_columns": agent_cols
        }

if __name__ == "__main__":
    full_database_setup()
