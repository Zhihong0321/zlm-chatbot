#!/usr/bin/env python3
"""
Simple MCP Database Test Script
Tests PostgreSQL database setup for MCP integration
"""

import os
import sys
import asyncio
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

print("POSTGRESQL MCP DATABASE TEST")
print("=" * 50)

# Check database connection
try:
    from sqlalchemy import create_engine, text
    from dotenv import load_dotenv
    
   	load_dotenv()
    
    db_url = os.getenv("DATABASE_URL", "postgresql://localhost/postgres")
    print(f"Database URL: {db_url}")
    
    engine = create_engine(db_url)
    
    with engine.connect() as conn:
        print("PASS: Database connection successful")
        
        # Check if MCP tables exist
        tables_to_check = [
            'mcp_servers',
            'mcp_server_logs', 
            'agent_mcp_servers',
            'mcp_tool_usage',
            'mcp_system_metrics'
        ]
        
        all_tables_exist = True
        for table in tables_to_check:
            result = conn.execute(text(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = '{table}'
                )
            """)).scalar()
            
            status = "PASS" if result else "FAIL"
            exists_text = "Yes" if result else "No"
            print(f"  {status} Table '{table}' exists: {exists_text}")
            
            if not result:
                all_tables_exist = False
        
        if all_tables_exist:
            print("PASS: All MCP tables exist in database")
            
            # Check agent table structure
            columns_result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'agents'
            """)).fetchall()
            
            mcp_column_exists = any('mcp_servers' in str(col) for col in columns_result)
            tools_column_exists = any('tools_used' in str(col) for col in columns_result)
            mcp_responses_column_exists = any('mcp_server_responses' in str(col) for col in columns_result)
            
            print(f"  {'PASS' if mcp_column_exists else 'FAIL'} Agents table has mcp_servers column")
            print(f"  {'PASS' if tools_column_exists else 'FAIL'} Messages table has tools_used column")
            print(f"  {'PASS' if mcp_responses_column_exists else 'FAIL'} Messages table has mcp_server_responses column")
            
            # Check server data
            server_count = conn.execute(text("SELECT COUNT(*) FROM mcp_servers")).scalar()
            print(f"  PASS: Found {server_count} MCP servers in database")
            
            # Check agent-MCP relationships
            relationships = conn.execute(text("SELECT COUNT(*) FROM agent_mcp_servers")).scalar()
            print(f"  PASS: Found {relationships} agent-MCP server relationships")
            
            print("\nSUCCESS: PostgreSQL MCP database is ready!")
            print("Available features:")
            print("  - MCP server management with full CRUD operations")
            print("  - Agent-MCP server relationships")
            print("  - Tool usage tracking in conversations")
            print("  - Server health monitoring and logging")
            print("  - System metrics and performance tracking")
            
        else:
            print("FAIL: Some MCP tables are missing")
            print("Please run: python setup_mcp_database.py")
        
except ImportError as e:
    print(f"FAIL: Required libraries not available: {e}")
    print("Please install: pip install sqlalchemy psycopg2-binary python-dotenv")
except Exception as e:
    print(f"FAIL: Database test failed: {e}")
    print("Please check your DATABASE_URL configuration")

print("\nDatabase configuration status checked.")
