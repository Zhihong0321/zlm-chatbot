#!/usr/bin/env python3
"""
Emergency database check for MCP tables
"""
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    import psycopg2
    from sqlalchemy import create_engine, text
    from dotenv import load_dotenv
    
    load_dotenv()
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    print(f"DATABASE_URL: {DATABASE_URL[:50]}...")
    
    # Test connection
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        # Check if MCP tables exist
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema='public' 
            AND table_name LIKE 'mcp_%'
        """)).fetchall()
        
        print(f"MCP tables found: {len(result)}")
        for table in result:
            print(f"  - {table[0]}")
            
        # Check basic agents table
        agents_result = conn.execute(text("SELECT COUNT(*) FROM agents")).fetchone()
        print(f"Total agents: {agents_result[0]}")
        
        # Test MCP servers table
        if 'mcp_servers' in [table[0] for table in result]:
            mcp_result = conn.execute(text("SELECT COUNT(*) FROM mcp_servers")).fetchone()
            print(f"MCP servers: {mcp_result[0]}")
        
        print("✅ Database connection working")
        
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    sys.exit(1)
