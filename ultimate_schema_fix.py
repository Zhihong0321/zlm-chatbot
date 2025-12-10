
import os
import psycopg2
from urllib.parse import urlparse

# Explicitly load .env
from dotenv import load_dotenv
load_dotenv()

def force_fix_schema():
    print("STARTING BRUTE FORCE SCHEMA FIX")
    
    # Get database URL
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL not set in environment")
        # Try to read manually from .env file if load_dotenv failed
        try:
            with open('.env', 'r') as f:
                for line in f:
                    if line.startswith('DATABASE_URL='):
                        db_url = line.split('=', 1)[1].strip()
                        print(f"   Found DATABASE_URL in .env file")
                        break
        except Exception as e:
            print(f"   Error reading .env file: {e}")
            
    if not db_url:
        print("❌ Critical: Could not find DATABASE_URL anywhere")
        return

        try:
            print(f"Connecting to: {db_url[:20]}...")
            conn = psycopg2.connect(db_url)
            conn.autocommit = True
            cursor = conn.cursor()
            
            # 1. Add mcp_servers to agents
            print("1. Checking 'mcp_servers' column in 'agents'...")
            try:
                cursor.execute("ALTER TABLE agents ADD COLUMN IF NOT EXISTS mcp_servers JSON;")
                print("   - Success: 'mcp_servers' column ensure on 'agents'")
            except Exception as e:
                print(f"   - Failed: {e}")
    
            # 2. Add tools_used to chat_messages
            print("2. Checking 'tools_used' column in 'chat_messages'...")
            try:
                cursor.execute("ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS tools_used JSON;")
                print("   - Success: 'tools_used' column ensure on 'chat_messages'")
            except Exception as e:
                print(f"   - Failed: {e}")
    
            # 3. Add mcp_server_responses to chat_messages
            print("3. Checking 'mcp_server_responses' column in 'chat_messages'...")
            try:
                cursor.execute("ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS mcp_server_responses JSON;")
                print("   - Success: 'mcp_server_responses' column ensure on 'chat_messages'")
            except Exception as e:
                print(f"   - Failed: {e}")
                
            # 4. Ensure MCP tables exist (Basic check)
            print("4. Checking 'mcp_servers' table...")
            try:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS mcp_servers (
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
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                print("   - Success: 'mcp_servers' table ensured")
            except Exception as e:
                print(f"   - Failed: {e}")
    
            conn.close()
            print("\nFIX COMPLETE. Restart the application to verify.")
    
        except Exception as e:
            print(f"\nCRITICAL CONNECTION ERROR: {e}")

if __name__ == "__main__":
    force_fix_schema()
