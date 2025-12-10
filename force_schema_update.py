
import os
import sys
import psycopg2
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_clean_db_url():
    url = os.getenv("DATABASE_URL")
    if not url:
        # Try reading local .env directly if load_dotenv failed or env var not set
        try:
            with open('.env', 'r') as f:
                for line in f:
                    if line.startswith('DATABASE_URL='):
                        url = line.split('=', 1)[1].strip().strip("'").strip('"')
                        break
        except:
            pass
            
    if not url:
        print("Error: DATABASE_URL not found.")
        return None

    # Fix for "invalid dsn: invalid URI query parameter: schema"
    # Parse the URL
    try:
        parsed = urlparse(url)
        # If query parameters exist, filter out 'schema' or other problematic ones for libpq
        if parsed.query:
            qs = parse_qs(parsed.query)
            # Remove 'schema' if present
            if 'schema' in qs:
                del qs['schema']
            # Rebuild query string
            new_query = urlencode(qs, doseq=True)
            # Rebuild URL
            url = urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                new_query,
                parsed.fragment
            ))
    except Exception as e:
        print(f"Warning parsing URL: {e}")
        
    return url

def run_sql():
    print("--- STARTING DIRECT SQL FIX ---")
    db_url = get_clean_db_url()
    if not db_url:
        sys.exit(1)
        
    print(f"Target Database: {db_url.split('@')[1] if '@' in db_url else 'Unknown'}")
    
    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # LIST OF COMMANDS TO RUN
        commands = [
            # 1. Add mcp_servers to agents
            {
                "desc": "Add 'mcp_servers' column to 'agents' table",
                "sql": "ALTER TABLE agents ADD COLUMN IF NOT EXISTS mcp_servers JSON DEFAULT '[]'::json;"
            },
            # 2. Add tools_used to chat_messages
            {
                "desc": "Add 'tools_used' column to 'chat_messages' table",
                "sql": "ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS tools_used JSON DEFAULT '[]'::json;"
            },
            # 3. Add mcp_server_responses to chat_messages
            {
                "desc": "Add 'mcp_server_responses' column to 'chat_messages' table",
                "sql": "ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS mcp_server_responses JSON DEFAULT '[]'::json;"
            }
        ]
        
        for cmd in commands:
            print(f"\nExecuting: {cmd['desc']}")
            print(f"SQL: {cmd['sql']}")
            try:
                cursor.execute(cmd['sql'])
                print("✅ SUCCESS")
            except Exception as e:
                print(f"❌ FAILED: {e}")
                
        # VERIFICATION
        print("\n--- VERIFICATION ---")
        
        # Verify agents
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='agents' AND column_name='mcp_servers';")
        if cursor.fetchone():
            print("✅ 'agents.mcp_servers' exists.")
        else:
            print("❌ 'agents.mcp_servers' STILL MISSING.")

        # Verify chat_messages
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='chat_messages' AND column_name='tools_used';")
        if cursor.fetchone():
            print("✅ 'chat_messages.tools_used' exists.")
        else:
            print("❌ 'chat_messages.tools_used' STILL MISSING.")

        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='chat_messages' AND column_name='mcp_server_responses';")
        if cursor.fetchone():
            print("✅ 'chat_messages.mcp_server_responses' exists.")
        else:
            print("❌ 'chat_messages.mcp_server_responses' STILL MISSING.")

        conn.close()
        print("\nDone.")
        
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_sql()
