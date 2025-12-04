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

@router.post("/fix-mcp-tables-properly")
def fix_mcp_tables_properly():
    """PROPERLY fix MCP tables by recreating with correct schema"""
    try:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            return {"status": "error", "message": "DATABASE_URL not set"}
            
        import psycopg2
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        results = []
        
        # STEP 1: Drop the incomplete mcp_servers table completely
        try:
            cursor.execute("DROP TABLE IF EXISTS mcp_servers CASCADE;")
            results.append("Dropped incomplete mcp_servers table")
        except Exception as e:
            results.append(f"Failed to drop table: {e}")
        
        # STEP 2: Create mcp_servers table with COMPLETE CORRECT schema
        try:
            cursor.execute("""
                CREATE TABLE mcp_servers (
                    id VARCHAR(255) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT DEFAULT '',
                    command VARCHAR(500) NOT NULL,
                    arguments JSONB DEFAULT '[]',
                    environment JSONB DEFAULT '{}',
                    working_directory VARCHAR(1000) DEFAULT '',
                    enabled BOOLEAN DEFAULT TRUE,
                    auto_start BOOLEAN DEFAULT TRUE,
                    health_check_interval INTEGER DEFAULT 30,
                    status VARCHAR(20) DEFAULT 'stopped',
                    process_id INTEGER,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX ix_mcp_servers_enabled ON mcp_servers(enabled);")
            cursor.execute("CREATE INDEX ix_mcp_servers_status ON mcp_servers(status);")
            
            results.append("Created complete mcp_servers table with all required columns")
        except Exception as e:
            results.append(f"Failed to create complete table: {e}")
            conn.close()
            return {"status": "error", "results": results}
        
        # STEP 3: Insert test MCP server with ALL fields
        try:
            cursor.execute("""
                INSERT INTO mcp_servers (id, name, description, command, arguments, environment, working_directory, enabled, auto_start, health_check_interval, status)
                VALUES ('test-1', 'Test Server', 'A test MCP server for validation', 'echo', '["hello"]', '{}', '/app', TRUE, FALSE, 30, 'stopped');
            """)
            results.append("Inserted test server with complete schema")
        except Exception as e:
            results.append(f"Failed to insert test server: {e}")
        
        # STEP 4: Add other required columns to existing tables
        try:
            cursor.execute("ALTER TABLE agents ADD COLUMN IF NOT EXISTS mcp_servers JSON;")
            cursor.execute("ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS tools_used JSON;")
            cursor.execute("ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS mcp_server_responses JSON;")
            results.append("Added MCP columns to agents and chat_messages tables")
        except Exception as e:
            results.append(f"Failed to add MCP columns: {e}")
        
        # STEP 5: Verify the table has correct structure
        try:
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'mcp_servers' 
                ORDER BY ordinal_position;
            """)
            columns = cursor.fetchall()
            results.append(f"Table columns: {[col[0] for col in columns]}")
            
            # Test a query like the MCP manager would use
            cursor.execute("""
                SELECT id, name, description, command, arguments, environment, 
                       working_directory, enabled, auto_start, health_check_interval,
                       status, process_id, created_at, updated_at 
                FROM mcp_servers
            """)
            servers = cursor.fetchall()
            results.append(f"MCP manager query test: {len(servers)} servers found")
            
        except Exception as e:
            results.append(f"Verification failed: {e}")
            
        conn.close()
        return {"status": "success", "results": results}
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@router.post("/create-mcp-tables")
def create_mcp_tables():
    """Create only the missing MCP tables"""
    try:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            return {"status": "error", "message": "DATABASE_URL not set"}
            
        import psycopg2
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        results = []
        
        # Create just the MCP tables that are missing
        mcp_tables_sql = [
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
            "CREATE INDEX IF NOT EXISTS ix_mcp_system_metrics_timestamp ON mcp_system_metrics(timestamp);"
        ]
        
        # Execute all MCP table creation statements
        for i, sql in enumerate(mcp_tables_sql):
            try:
                cursor.execute(sql)
                results.append(f"Table Step {i+1}: Success")
            except Exception as e:
                if "already exists" in str(e):
                    results.append(f"Table Step {i+1}: Already exists")
                else:
                    results.append(f"Table Step {i+1}: Failed - {str(e)[:50]}")
        
        # Insert default MCP servers
        try:
            cursor.execute("""
                INSERT INTO mcp_servers (id, name, description, command, arguments, environment, working_directory, enabled, auto_start, health_check_interval, status)
                VALUES 
                    ('filesystem-1', 'File System Server', 'Local file system operations (list, read, search)', 'python', '["mcp_file_server.py"]', '{}', '/app', TRUE, TRUE, 30, 'stopped'),
                    ('database-1', 'Database Server', 'Database query and management tools', 'npx', '["-y", "@modelcontextprotocol/server-postgres"]', '{"DATABASE_URL": "' + db_url + '"}', '/app', TRUE, TRUE, 30, 'stopped'),
                    ('git-1', 'Git Server', 'Git repository operations and file version control', 'npx', '["-y", "@modelcontextprotocol/server-git"]', '{}', '/app', TRUE, TRUE, 30, 'stopped'),
                    ('web-fetch-1', 'Web Fetch Server', 'HTTP requests and web content fetching', 'npx', '["-y", "@modelcontextprotocol/server-fetch"]', '{}', '/app', TRUE, TRUE, 30, 'stopped')
                ON CONFLICT (id) DO NOTHING;
            """)
            results.append("Default MCP servers inserted")
        except Exception as e:
            results.append(f"Failed to insert servers: {str(e)[:50]}")
            
        # Verify setup
        try:
            cursor.execute("SELECT COUNT(*) FROM mcp_servers")
            server_count = cursor.fetchone()[0]
            results.append(f"Verification: {server_count} MCP servers found")
        except Exception as e:
            results.append(f"Verification failed: {str(e)[:50]}")
        
        conn.close()
        return {"status": "success", "results": results}
        
    except Exception as e:
        return {"status": "error", "error": str(e)}
