#!/usr/bin/env python3
"""Simple test to check Railway PostgreSQL availability"""

import os
import psycopg2

def test_railway_postgres():
    """Test Railway PostgreSQL connection and setup"""
    print("🔍 Railway PostgreSQL Connection Test")
    print("=" * 50)
    
   db_url = os.getenv("DATABASE_URL", "DATABASE_URL NOT SET")
    
    if db_url == "DATABASE_URL NOT SET":
        print("❌ DATABASE_URL not set")
        return 1
    
    print(f"🔍 Testing PostgreSQL connection to: {db_url}")
    
    try:
        conn = psycopg2.connect(db_url, connect_timeout=5)
        
        version = conn.cursor().execute("SELECT version()")[0]
        print(f"✅ PostgreSQL Version: {version}")
        
        # Test basic schema existence
        try:
            table_count = conn.cursor().execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public'")
            print(f"✅ Found {table_count} tables in database")
            
            # Check for critical tables
            mcp_tables = ["mcp_servers", "chat_messages", "agents"]
            for table in mcp_tables:
                try:
                    table_exists = conn.cursor().execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] > 0
                    print(f"✅ Table '{table}' exists with rows")
                except:
                    print(f"⚠️ Table '{table}' missing")
            conn.close()
            return table_count >= 5
            
        except Exception as e:
            print(f"❌ Schema check failed: {e}")
            conn.close()
            return False

        print("✅ PostgreSQL connection successful and schema ready")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
        
if __name__main__main__main__main__main__main__main__main__main__":
    exit_code = test_railway_postgres()
