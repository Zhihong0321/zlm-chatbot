#!/usr/bin/env python3
"""
Railway MCP Database Setup - Direct Execution
This script directly creates MCP tables in the Railway PostgreSQL database
"""

import os
import sys
import json
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment
load_dotenv()

def main():
    print("=" * 60)
    print("RAILWAY MCP DATABASE SETUP - DIRECT")
    print("=" * 60)
    
    # Get database URL
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("ERROR: DATABASE_URL not found in environment")
        return 1
    
    print(f"Database URL: {db_url[:30]}...")
    
    # Create engine
    try:
        engine = create_engine(db_url)
        print("✅ Database engine created")
    except Exception as e:
        print(f"❌ Failed to create engine: {e}")
        return 1
    
    # MCP tables setup SQL
    mcp_setup_sql = [
        # Create mcp_servers table
        """
        CREATE TABLE IF NOT EXISTS mcp_servers (
            id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            command VARCHAR(500) NOT NULL,
            arguments JSONB,
            environment JSONB,
            working_directory VARCHAR(1000),
            enabled BOOLEAN DEFAULT TRUE,
            auto_start BOOLEAN DEFAULT TRUE,
            health_check_interval INTEGER DEFAULT 30,
            status VARCHAR(20) DEFAULT 'stopped',
            process_id INTEGER,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """,
        
        # Create indexes
        "CREATE INDEX IF NOT EXISTS ix_mcp_servers_enabled ON mcp_servers(enabled);",
        "CREATE INDEX IF NOT EXISTS ix_mcp_servers_status ON mcp_servers(status);",
        
        # Create mcp_server_logs table
        """
        CREATE TABLE IF NOT EXISTS mcp_server_logs (
            id SERIAL PRIMARY KEY,
            server_id VARCHAR(255) NOT NULL REFERENCES mcp_servers(id) ON DELETE CASCADE,
            level VARCHAR(10) NOT NULL,
            message TEXT NOT NULL,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """,
        
        # Create indexes for logs
        "CREATE INDEX IF NOT EXISTS ix_mcp_server_logs_server_id ON mcp_server_logs(server_id);",
        "CREATE INDEX IF NOT EXISTS ix_mcp_server_logs_timestamp ON mcp_server_logs(timestamp);",
        
        # Create agent_mcp_servers table
        """
        CREATE TABLE IF NOT EXISTS agent_mcp_servers (
            id SERIAL PRIMARY KEY,
            agent_id INTEGER NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
            server_id VARCHAR(255) NOT NULL REFERENCES mcp_servers(id) ON DELETE CASCADE,
            is_enabled BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(agent_id, server_id)
        );
        """,
        
        # Create indexes for agent_mcp_servers
        "CREATE INDEX IF NOT EXISTS ix_agent_mcp_servers_agent_id ON agent_mcp_servers(agent_id);",
        "CREATE INDEX IF NOT EXISTS ix_agent_mcp_servers_server_id ON agent_mcp_servers(server_id);",
        
        # Add missing columns to existing tables
        "ALTER TABLE agents ADD COLUMN IF NOT EXISTS mcp_servers JSONB;",
        "ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS tools_used JSONB;",
        "ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS mcp_server_responses JSONB;",
        
        # Create mcp_tool_usage table
        """
        CREATE TABLE IF NOT EXISTS mcp_tool_usage (
            id SERIAL PRIMARY KEY,
            server_id VARCHAR(255) NOT NULL REFERENCES mcp_servers(id) ON DELETE CASCADE,
            tool_name VARCHAR(255) NOT NULL,
            parameters JSONB,
            response JSONB,
            duration_ms INTEGER,
            status VARCHAR(20) DEFAULT 'success',
            error_message TEXT,
            session_id INTEGER REFERENCES chat_sessions(id) ON DELETE SET NULL,
            message_id INTEGER REFERENCES chat_messages(id) ON DELETE SET NULL,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """,
        
        # Create indexes for tool_usage
        "CREATE INDEX IF NOT EXISTS ix_mcp_tool_usage_server_id ON mcp_tool_usage(server_id);",
        "CREATE INDEX IF NOT EXISTS ix_mcp_tool_usage_session_id ON mcp_tool_usage(session_id);",
        "CREATE INDEX IF NOT EXISTS ix_mcp_tool_usage_timestamp ON mcp_tool_usage(timestamp);",
        
        # Create mcp_system_metrics table
        """
        CREATE TABLE IF NOT EXISTS mcp_system_metrics (
            id SERIAL PRIMARY KEY,
            metric_type VARCHAR(50) NOT NULL,
            metric_value DECIMAL(10,4) NOT NULL,
            metadata JSONB,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """,
        
        # Create indexes for metrics
        "CREATE INDEX IF NOT EXISTS ix_mcp_system_metrics_type ON mcp_system_metrics(metric_type);",
        "CREATE INDEX IF NOT EXISTS ix_mcp_system_metrics_timestamp ON mcp_system_metrics(timestamp);",
        
        # Insert default MCP servers
        """
        INSERT INTO mcp_servers (id, name, description, command, arguments, environment, working_directory, enabled, auto_start, health_check_interval, status)
        VALUES 
            ('filesystem-1', 'File System Server', 'Local file system operations (list, read, search)', 'python', '["mcp_file_server.py']', '{}', '/app', TRUE, TRUE, 30, 'stopped'),
            ('database-1', 'Database Server', 'Database query and management tools', 'npx', '["-y", "@modelcontextprotocol/server-postgres"]', '{"DATABASE_URL": "' || :db_url || '"}', '/app', TRUE, TRUE, 30, 'stopped'),
            ('git-1', 'Git Server', 'Git repository operations and file version control', 'npx', '["-y", "@modelcontextprotocol/server-git"]', '{}', '/app', TRUE, TRUE, 30, 'stopped'),
            ('web-fetch-1', 'Web Fetch Server', 'HTTP requests and web content fetching', 'npx', '["-y", "@modelcontextprotocol/server-fetch"]', '{}', '/app', TRUE, TRUE, 30, 'stopped')
        ON CONFLICT (id) DO NOTHING;
        """
    ]
    
    # Execute SQL
    try:
        with engine.begin() as conn:
            for i, sql in enumerate(mcp_setup_sql):
                try:
                    if "INSERT INTO mcp_servers" in sql and ":db_url" in sql:
                        conn.execute(text(sql), {"db_url": db_url})
                    else:
                        conn.execute(text(sql))
                    print(f"✅ Step {i+1}/{len(mcp_setup_sql)}: Executed successfully")
                except Exception as e:
                    if "already exists" in str(e) or "does not exist" in str(e):
                        print(f"⚠️ Step {i+1}/{len(mcp_setup_sql)}: {str(e)[:100]}")
                    else:
                        print(f"❌ Step {i+1}/{len(mcp_setup_sql)}: {str(e)[:100]}")
                        return 1
        
        print("\n✅ MCP database setup completed successfully!")
        
        # Verify setup
        with engine.begin() as conn:
            # Check tables
            tables = conn.execute(text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema='public' AND table_name LIKE 'mcp_%'
            """)).fetchall()
            
            print(f"\n✅ Created {len(tables)} MCP tables:")
            for table in tables:
                print(f"  • {table[0]}")
            
            # Check servers
            server_count = conn.execute(text("SELECT COUNT(*) FROM mcp_servers")).scalar()
            print(f"\n✅ Seeded {server_count} default MCP servers")
            
            # Show servers
            servers = conn.execute(text("""
                SELECT id, name, description, status FROM mcp_servers
            """)).fetchall()
            
            for server in servers:
                print(f"  • {server[0]}: {server[1]} - {server[3]}")
        
        print("\n" + "=" * 60)
        print("MCP DATABASE IS NOW READY!")
        print("=" * 60)
        print("\nFrontend should now be able to load MCP servers.")
        print("Test the API endpoints:")
        print("  • GET /api/v1/mcp/servers")
        print("  • GET /api/v1/mcp/status")
        print("  • GET /api/v1/mcp/health")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
