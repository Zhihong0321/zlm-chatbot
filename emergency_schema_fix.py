#!/usr/bin/env python3
"""
EMERGENCY RAILWAY SCHEMA FIX
Run this directly on Railway to fix broken schema
"""

import os
import psycopg2
import sys

def emergency_schema_fix():
    # Get Railway DATABASE_URL
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("ERROR: DATABASE_URL not found")
        return False
        
    print(f"DATABASE_URL found: {db_url[:50]}...")
    
    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("✅ Connected to Railway database!")
        
        # === STEP 1: Add missing columns to agents ===
        print("\n=== STEP 1: Fix agents table ===")
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'agents' 
            AND table_schema = 'public'
        """)
        agent_cols = {row[0] for row in cursor.fetchall()}
        
        if 'mcp_servers' not in agent_cols:
            print("➕ ADDING mcp_servers to agents...")
            cursor.execute('ALTER TABLE agents ADD COLUMN mcp_servers JSON;')
            print("✅ mcp_servers added to agents")
        else:
            print("✅ mcp_servers already exists in agents")
        
        # === STEP 2: Add missing columns to chat_messages ===
        print("\n=== STEP 2: Fix chat_messages table ===")
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'chat_messages' 
            AND table_schema = 'public'
        """)
        chat_cols = {row[0] for row in cursor.fetchall()}
        
        if 'tools_used' not in chat_cols:
            print("➕ ADDING tools_used to chat_messages...")
            cursor.execute('ALTER TABLE chat_messages ADD COLUMN tools_used JSON;')
            print("✅ tools_used added to chat_messages")
        else:
            print("✅ tools_used already exists in chat_messages")
            
        if 'mcp_server_responses' not in chat_cols:
            print("➕ ADDING mcp_server_responses to chat_messages...")
            cursor.execute('ALTER TABLE chat_messages ADD COLUMN mcp_server_responses JSON;')
            print("✅ mcp_server_responses added to chat_messages")
        else:
            print("✅ mcp_server_responses already exists in chat_messages")
        
        # === STEP 3: Create mcp_servers table ===
        print("\n=== STEP 3: Create mcp_servers table ===")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name = 'mcp_servers' 
            AND table_schema = 'public'
        """)
        mcp_table_exists = cursor.fetchone()
        
        if not mcp_table_exists:
            print("➕ CREATING mcp_servers table...")
            cursor.execute("""
                CREATE TABLE mcp_servers (
                    id VARCHAR(255) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    command VARCHAR(500) NOT NULL,
                    arguments JSON,
                    environment JSON,
                    working_directory VARCHAR(1000),
                    enabled BOOLEAN DEFAULT TRUE,
                    auto_start BOOLEAN DEFAULT TRUE,
                    health_check_interval INTEGER DEFAULT 30,
                    status VARCHAR(20) DEFAULT 'stopped',
                    process_id INTEGER,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ
                );
            """)
            cursor.execute("CREATE INDEX ix_mcp_servers_id ON mcp_servers(id);")
            cursor.execute("CREATE INDEX ix_mcp_servers_enabled ON mcp_servers(enabled);")
            cursor.execute("CREATE INDEX ix_mcp_servers_status ON mcp_servers(status);")
            print("✅ mcp_servers table created")
        else:
            print("✅ mcp_servers table already exists")
        
        # === STEP 4: Create other MCP tables ===
        print("\n=== STEP 4: Create other MCP tables ===")
        
        # mcp_server_logs
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name = 'mcp_server_logs' 
            AND table_schema = 'public'
        """)
        if not cursor.fetchone():
            print("➕ CREATING mcp_server_logs table...")
            cursor.execute("""
                CREATE TABLE mcp_server_logs (
                    id SERIAL PRIMARY KEY,
                    server_id VARCHAR(255) NOT NULL,
                    level VARCHAR(10) NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TIMESTAMPTZ DEFAULT NOW(),
                    FOREIGN KEY (server_id) REFERENCES mcp_servers(id) ON DELETE CASCADE
                );
            """)
            cursor.execute("CREATE INDEX ix_mcp_server_logs_server_id ON mcp_server_logs(server_id);")
            print("✅ mcp_server_logs table created")
        
        # agent_mcp_servers (junction table)
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name = 'agent_mcp_servers' 
            AND table_schema = 'public'
        """)
        if not cursor.fetchone():
            print("➕ CREATING agent_mcp_servers table...")
            cursor.execute("""
                CREATE TABLE agent_mcp_servers (
                    id SERIAL PRIMARY KEY,
                    agent_id INTEGER NOT NULL,
                    server_id VARCHAR(255) NOT NULL,
                    is_enabled BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ,
                    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE,
                    FOREIGN KEY (server_id) REFERENCES mcp_servers(id) ON DELETE CASCADE,
                    UNIQUE(agent_id, server_id)
                );
            """)
            print("✅ agent_mcp_servers table created")
        
        # === FINAL VERIFICATION ===
        print("\n=== FINAL VERIFICATION ===")
        
        cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
        table_count = cursor.fetchone()[0]
        print(f"✅ Total tables: {table_count}")
        
        cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'agents' AND column_name = 'mcp_servers'
        """)
        mcp_servers_col = cursor.fetchone()
        print(f"✅ agents.mcp_servers: {'EXISTS' if mcp_servers_col else 'MISSING'}")
        
        cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'chat_messages' AND column_name = 'tools_used'
        """)
        tools_used_col = cursor.fetchone()
        print(f"✅ chat_messages.tools_used: {'EXISTS' if tools_used_col else 'MISSING'}")
        
        cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'chat_messages' AND column_name = 'mcp_server_responses'
        """)
        mcp_responses_col = cursor.fetchone()
        print(f"✅ chat_messages.mcp_server_responses: {'EXISTS' if mcp_responses_col else 'MISSING'}")
        
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_name = 'mcp_servers' AND table_schema = 'public'
        """)
        mcp_table = cursor.fetchone()
        print(f"✅ mcp_servers table: {'EXISTS' if mcp_table else 'MISSING'}")
        
        conn.close()
        
        print("\n🎉 RAILWAY PRODUCTION SCHEMA FIX COMPLETE!")
        print("All required columns and tables have been created.")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = emergency_schema_fix()
    sys.exit(0 if success else 1)
