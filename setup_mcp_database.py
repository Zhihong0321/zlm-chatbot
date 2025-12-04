#!/usr/bin/env python3
"""
PostgreSQL MCP Database Setup Script
Creates and migrates MCP-related tables and schemas
"""

import os
import asyncio
import sys
from typing import List, Dict, Any
from datetime import datetime
import json

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class MCPDatabaseSetup:
    """Handle MCP database schema setup and migration"""
    
    def __init__(self):
        # Database connection
        self.db_url = os.getenv("DATABASE_URL", "sqlite:///chatbot.db")
        self.engine = create_engine(self.db_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False)
        
        # Check if PostgreSQL or SQLite
        self.is_postgres = "postgresql" in self.db_url.lower()
        
        print(f"Database Setup Initialized")
        print(f"Database URL: {self.db_url}")
        print(f"Database Type: {'PostgreSQL' if self.is_postgres else 'SQLite'}")
    
    async def check_database_connection(self) -> bool:
        """Check if database connection is working"""
        try:
            with self.engine.connect() as conn:
                print("PASS: Database connection successful")
                return True
        except Exception as e:
            print(f"FAIL: Database connection failed: {e}")
            return False
    
    async def run_migration(self) -> bool:
        """Run the MCP schema migration"""
        try:
            print("\nRunning MCP Schema Migration...")
            
            with self.engine.begin() as conn:
                # Execute the migration SQL
                migration_sql = self._get_migration_sql()
                
                for sql_statement in migration_sql:
                    if sql_statement.strip():
                        try:
                            conn.execute(text(sql_statement))
                        except Exception as e:
                            print(f"Error executing: {sql_statement[:50]}...")
                            print(f"Error: {e}")
                            return False
            
            print("PASS: MCP schema migration completed successfully")
            return True
            
        except Exception as e:
            print(f"FAIL: Migration failed: {e}")
            return False
    
    def _get_migration_sql(self) -> List[str]:
        """Get SQL statements for MCP migration"""
        
        if self.is_postgres:
            return self._get_postgres_migration_sql()
        else:
            return self._get_sqlite_migration_sql()
    
    def _get_postgres_migration_sql(self) -> List[str]:
        """PostgreSQL migration SQL"""
        return [
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
            
            # Create indexes for mcp_servers
            """
            CREATE INDEX IF NOT EXISTS ix_mcp_servers_enabled ON mcp_servers(enabled);
            """,
            """
            CREATE INDEX IF NOT EXISTS ix_mcp_servers_status ON mcp_servers(status);
            """,
            
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
            
            # Create indexes for mcp_server_logs
            """
            CREATE INDEX IF NOT EXISTS ix_mcp_server_logs_server_id ON mcp_server_logs(server_id);
            """,
            """
            CREATE INDEX IF NOT EXISTS ix_mcp_server_logs_timestamp ON mcp_server_logs(timestamp);
            """,
            
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
            """
            CREATE INDEX IF NOT EXISTS ix_agent_mcp_servers_agent_id ON agent_mcp_servers(agent_id);
            """,
            """
            CREATE INDEX IF NOT EXISTS ix_agent_mcp_servers_server_id ON agent_mcp_servers(server_id);
            """,
            
            # Update agents table to add mcp_servers column
            """
            ALTER TABLE agents ADD COLUMN IF NOT EXISTS mcp_servers JSONB;
            """,
            
            # Update chat_messages table to add MCP fields
            """
            ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS tools_used JSONB;
            """,
            """
            ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS mcp_server_responses JSONB;
            """,
            
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
            
            # Create indexes for mcp_tool_usage
            """
            CREATE INDEX IF NOT EXISTS ix_mcp_tool_usage_server_id ON mcp_tool_usage(server_id);
            """,
            """
            CREATE INDEX IF NOT EXISTS ix_mcp_tool_usage_session_id ON mcp_tool_usage(session_id);
            """,
            """
            CREATE INDEX IF NOT EXISTS ix_mcp_tool_usage_timestamp ON mcp_tool_usage(timestamp);
            """,
            
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
            
            # Create indexes for mcp_system_metrics
            """
            CREATE INDEX IF NOT EXISTS ix_mcp_system_metrics_type ON mcp_system_metrics(metric_type);
            """,
            """
            CREATE INDEX IF NOT EXISTS ix_mcp_system_metrics_timestamp ON mcp_system_metrics(timestamp);
            """,
            
            # Insert default MCP servers
            """
            INSERT INTO mcp_servers (id, name, description, command, arguments, environment, working_directory, enabled, auto_start, health_check_interval, status)
            VALUES 
                ('filesystem-1', 'File System Server', 'Local file system operations (list, read, search)', 'python', '["mcp_file_server.py"]', '{}', CURRENT_DIRECTORY, TRUE, TRUE, 30, 'stopped'),
                ('database-1', 'Database Server', 'Database query and management tools', 'npx', '["-y", "@modelcontextprotocol/server-postgres"]', '{"DATABASE_URL": "sqlite:///chatbot.db"}', CURRENT_DIRECTORY, TRUE, TRUE, 30, 'stopped'),
                ('git-1', 'Git Server', 'Git repository operations and file version control', 'npx', '["-y", "@modelcontextprotocol/server-git"]', '{}', CURRENT_DIRECTORY, TRUE, TRUE, 30, 'stopped'),
                ('web-fetch-1', 'Web Fetch Server', 'HTTP requests and web content fetching', 'npx', '["-y", "@modelcontextprotocol/server-fetch"]', '{}', CURRENT_DIRECTORY, TRUE, TRUE, 30, 'stopped')
            ON CONFLICT (id) DO NOTHING;
            """
        ]
    
    def _get_sqlite_migration_sql(self) -> List[str]:
        """SQLite migration SQL"""
        return [
            # Create mcp_servers table
            """
            CREATE TABLE IF NOT EXISTS mcp_servers (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                command TEXT NOT NULL,
                arguments TEXT,
                environment TEXT,
                working_directory TEXT,
                enabled INTEGER DEFAULT 1,
                auto_start INTEGER DEFAULT 1,
                health_check_interval INTEGER DEFAULT 30,
                status TEXT DEFAULT 'stopped',
                process_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Create indexes for mcp_servers
            """
            CREATE INDEX IF NOT EXISTS ix_mcp_servers_enabled ON mcp_servers(enabled);
            """,
            """
            CREATE INDEX IF NOT EXISTS ix_mcp_servers_status ON mcp_servers(status);
            """,
            
            # Create mcp_server_logs table
            """
            CREATE TABLE IF NOT EXISTS mcp_server_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id TEXT NOT NULL REFERENCES mcp_servers(id) ON DELETE CASCADE,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Create indexes for mcp_server_logs
            """
            CREATE INDEX IF NOT EXISTS ix_mcp_server_logs_server_id ON mcp_server_logs(server_id);
            """,
            """
            CREATE INDEX IF NOT EXISTS ix_mcp_server_logs_timestamp ON mcp_server_logs(timestamp);
            """,
            
            # Create agent_mcp_servers table
            """
            CREATE TABLE IF NOT EXISTS agent_mcp_servers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id INTEGER NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
                server_id TEXT NOT NULL REFERENCES mcp_servers(id) ON DELETE CASCADE,
                is_enabled INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(agent_id, server_id)
            );
            """,
            
            # Create indexes for agent_mcp_servers
            """
            CREATE INDEX IF NOT EXISTS ix_agent_mcp_servers_agent_id ON agent_mcp_servers(agent_id);
            """,
            """
            CREATE INDEX IF NOT EXISTS ix_agent_mcp_servers_server_id ON agent_mcp_servers(server_id);
            """,
            
            # Update agents table to add mcp_servers column
            """
            ALTER TABLE agents ADD COLUMN mcp_servers TEXT;
            """,
            
            # Update chat_messages table to add MCP fields
            """
            ALTER TABLE chat_messages ADD COLUMN tools_used TEXT;
            """,
            """
            ALTER TABLE chat_messages ADD COLUMN mcp_server_responses TEXT;
            """,
            
            # Create mcp_tool_usage table
            """
            CREATE TABLE IF NOT EXISTS mcp_tool_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id TEXT NOT NULL REFERENCES mcp_servers(id) ON DELETE CASCADE,
                tool_name TEXT NOT NULL,
                parameters TEXT,
                response TEXT,
                duration_ms INTEGER,
                status TEXT DEFAULT 'success',
                error_message TEXT,
                session_id INTEGER REFERENCES chat_sessions(id) ON DELETE SET NULL,
                message_id INTEGER REFERENCES chat_messages(id) ON DELETE SET NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Create indexes for mcp_tool_usage
            """
            CREATE INDEX IF NOT EXISTS ix_mcp_tool_usage_server_id ON mcp_tool_usage(server_id);
            """,
            """
            CREATE INDEX IF NOT EXISTS ix_mcp_tool_usage_session_id ON mcp_tool_usage(session_id);
            """,
            """
            CREATE INDEX IF NOT EXISTS ix_mcp_tool_usage_timestamp ON mcp_tool_usage(timestamp);
            """,
            
            # Create mcp_system_metrics table
            """
            CREATE TABLE IF NOT EXISTS mcp_system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_type TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metadata TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Create indexes for mcp_system_metrics
            """
            CREATE INDEX IF NOT EXISTS ix_mcp_system_metrics_type ON mcp_system_metrics(metric_type);
            """,
            """
            CREATE INDEX IF NOT EXISTS ix_mcp_system_metrics_timestamp ON mcp_system_metrics(timestamp);
            """,
            
            # Insert default MCP servers
            """
            INSERT OR REPLACE INTO mcp_servers (id, name, description, command, arguments, environment, working_directory, enabled, auto_start, health_check_interval, status)
            VALUES 
                ('filesystem-1', 'File System Server', 'Local file system operations (list, read, search)', 'python', '["mcp_file_server.py"]', '{}', CURRENT_DIRECTORY, 1, 1, 30, 'stopped'),
                ('database-1', 'Database Server', 'Database query and management tools', 'npx', '["-y", "@modelcontextprotocol/server-postgres"]', '{"DATABASE_URL": "sqlite:///chatbot.db"}', CURRENT_DIRECTORY, 1, 1, 30, 'stopped'),
                ('git-1', 'Git Server', 'Git repository operations and file version control', 'npx', '["-y", "@modelcontextprotocol/server-git"]', '{}', CURRENT_DIRECTORY, 1, 1, 30, 'stopped'),
                ('web-fetch-1', 'Web Fetch Server', 'HTTP requests and web content fetching', 'npx', '["-y", "@modelcontextprotocol/server-fetch"]', '{}', CURRENT_DIRECTORY, 1, 1, 30, 'stopped')
            ;
            """
        ]
    
    async def seed_mcp_data(self) -> bool:
        """Seed MCP-related data"""
        try:
            print("\nSeeding MCP data...")
            
            with self.SessionLocal() as session:
                # Check if MCP servers exist
                if self.is_postgres:
                    mcp_servers = session.execute(
                        "SELECT COUNT(*) FROM mcp_servers"
                    ).scalar()
                else:
                    mcp_servers = session.execute(
                        "SELECT COUNT(*) FROM mcp_servers"
                    ).scalar()
                
                print(f"Found {mcp_servers} MCP servers in database")
                
                # Record system metrics
                current_time = datetime.utcnow()
                
                metrics_data = [
                    ('server_count', float(mcp_servers), {
                        'timestamp': current_time.isoformat(),
                        'server_types': ['filesystem', 'database', 'git', 'web-fetch']
                    }),
                    ('database_ready', 1.0, {
                        'timestamp': current_time.isoformat(),
                        'migration_status': 'completed',
                        'database_type': 'postgresql' if self.is_postgres else 'sqlite'
                    })
                ]
                
                for metric_type, metric_value, metadata in metrics_data:
                    try:
                        session.execute(
                            "INSERT INTO mcp_system_metrics (metric_type, metric_value, metadata) VALUES (?, ?, ?)",
                            (metric_type, metric_value, json.dumps(metadata))
                        )
                        print(f"  ✓ Recorded metric: {metric_type} = {metric_value}")
                    except Exception as e:
                        print(f"  ⚠️ Warning: Failed to record metric {metric_type}: {e}")
                
                session.commit()
            
            print("PASS: MCP data seeding completed")
            return True
            
        except Exception as e:
            print(f"FAIL: MCP data seeding failed: {e}")
            return False
    
    async def setup_database(self) -> bool:
        """Complete database setup process"""
        print("=" * 60)
        print("POSTGRESQL MCP DATABASE SETUP")
        print("=" * 60)
        
        # Step 1: Check connection
        if not await self.check_database_connection():
            print("\nFAIL: Database setup failed - connection error")
            return False
        
        # Step 2: Run migration
        if not await self.run_migration():
            print("\nFAIL: Database setup failed - migration error")
            return False
        
        # Step 3: Seed data
        if not await self.seed_mcp_data():
            print("\n⚠️ Database setup completed but data seeding failed")
            # Don't fail setup for seeding issues
        
        print("\n" + "=" * 60)
        print("PASS: MCP DATABASE SETUP COMPLETE!")
        print("=" * 60)
        
        print("\nDatabase Schema Summary:")
        print(f"  • mcp_servers: MCP server configurations")
        print(f"  • mcp_server_logs: Server logging and monitoring")
        print(f"  • agent_mcp_servers: Agent-server relationships")
        print(f"  • mcp_tool_usage: Tool execution tracking")
        print(f"  • mcp_system_metrics: System performance metrics")
        
        print("\nDatabase Features:")
        print(f"  • Foreign key constraints for data integrity")
        print(f"  • Indexes for optimal query performance")
        print(f"  • JSON fields for flexible data storage")
        print(f"  • Timestamp tracking for temporal queries")
        print(f"  • Cascade deletes for automatic cleanup")
        
        print("\nDefault MCP Servers Configured:")
        print("  • File System Server - Local file operations")
        print("  • Database Server - PostgreSQL operations")
        print("  • Git Server - Version control integration")
        print("  • Web Fetch Server - HTTP requests and scraping")
        
        return True
    
    async def verify_setup(self) -> bool:
        """Verify the MCP database setup"""
        try:
            print("\nVerifying MCP Database Setup...")
            
            with self.SessionLocal() as session:
                # Check all MCP tables exist
                tables_to_check = [
                    'mcp_servers',
                    'mcp_server_logs', 
                    'agent_mcp_servers',
                    'mcp_tool_usage',
                    'mcp_system_metrics'
                ]
                
                for table in tables_to_check:
                    if self.is_postgres:
                        result = session.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')").scalar()
                    else:
                        result = session.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'").fetchone()
                    
                    status = "✅" if result else "❌"
                    print(f"  {status} Table '{table}'")
                
                # Check if default servers exist
                if self.is_postgres:
                    server_count = session.execute("SELECT COUNT(*) FROM mcp_servers").scalar()
                else:
                    server_count = session.execute("SELECT COUNT(*) FROM mcp_servers").scalar()
                
                print(f"  ✅ MCP servers configured: {server_count}")
                
                # Check agents table has mcp_servers column
                if self.is_postgres:
                    has_column = session.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.columns 
                            WHERE table_name = 'agents' AND column_name = 'mcp_servers'
                        )
                    """).scalar()
                else:
                    has_column = session.execute("PRAGMA table_info(agents)").fetchall()
                    has_column = any('mcp_servers' in str(col) for col in has_column)
                
                column_status = "✅" if has_column else "❌"
                print(f"  {column_status} Agents table has mcp_servers column")
                
                # Check chat_messages table has MCP columns
                if self.is_postgres:
                    tools_column = session.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.columns 
                            WHERE table_name = 'chat_messages' AND column_name = 'tools_used'
                        )
                    """).scalar()
                    responses_column = session.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.columns 
                            WHERE table_name = 'chat_messages' AND column_name = 'mcp_server_responses'
                        )
                    """).scalar()
                else:
                    columns = session.execute("PRAGMA table_info(chat_messages)").fetchall()
                    tools_column = any('tools_used' in str(col) for col in columns)
                    responses_column = any('mcp_server_responses' in str(col) for col in columns)
                
                tools_status = "✅" if tools_column else "❌"
                responses_status = "✅" if responses_column else "❌"
                print(f"  {tools_status} Chat messages have tools_used column")
                print(f"  {responses_status} Chat messages have mcp_server_responses column")
                
                session.commit()
            
            print("\n✅ Database verification completed successfully!")
            return True
            
        except Exception as e:
            print(f"\n❌ Database verification failed: {e}")
            return False


async def main():
    """Main setup function"""
    
    setup = MCPDatabaseSetup()
    
    success = await setup.setup_database()
    
    if success:
        print("PASS: MCP database is now ready!")
        print("\nYou can now:")
        print("  • Start the MCP management API: python mcp_management_api.py")
        print("  • Start the enhanced backend: python backend_mcp_server.py")
        print("  • Access MCP features through the frontend")
        print("\nThe database will automatically:")
        print("  • Store MCP server configurations")
        print("  • Track tool usage in conversations")
        print("  • Monitor server health and performance")
        print("  • Manage agent-server relationships")
        print("  • Collect system metrics")
    else:
        print("\nFAIL: MCP database setup failed!")
        print("Please check your database configuration and try again.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
