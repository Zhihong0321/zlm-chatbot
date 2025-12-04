#!/usr/bin/env python3
"""
Railway Database Schema Diagnostic Tool
Checks the actual database schema on Railway to identify issues
"""

import os
import psycopg2
from sqlalchemy import create_engine, MetaData, inspect
from sqlalchemy.orm import sessionmaker
from backend.app.models.models import Base

def check_railway_schema():
    """Check what tables and columns actually exist on Railway"""
    print("🔍 RAILWAY DATABASE SCHEMA DIAGNOSTIC")
    print("=" * 60)
    
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL not set")
        return
    
    print(f"📊 Database URL: {db_url[:50]}...")
    
    try:
        # Test basic connection
        conn = psycopg2.connect(db_url)
        print("✅ Basic PostgreSQL connection working")
        
        cursor = conn.cursor()
        
        # Check all tables
        cursor.execute("""
            SELECT table_name, table_type 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        
        print(f"\n📋 Found {len(tables)} tables:")
        
        # Check expected tables
        expected_tables = [
            'users', 'agents', 'chat_sessions', 'chat_messages', 
            'session_knowledge', 'agent_knowledge_files',
            'mcp_servers', 'mcp_server_logs', 'agent_mcp_servers', 
            'mcp_tool_usage', 'mcp_system_metrics'
        ]
        
        found_tables = [table[0] for table in tables]
        missing_tables = []
        extra_tables = []
        
        for table in expected_tables:
            if table in found_tables:
                print(f"   ✅ {table}")
            else:
                missing_tables.append(table)
                print(f"   ❌ {table} - MISSING")
        
        for table in found_tables:
            if table not in expected_tables:
                extra_tables.append(table)
                print(f"   ⚠️ {table} - EXTRA")
                
        # Check critical columns in chat_messages
        print(f"\n🔍 Checking chat_messages columns:")
        if 'chat_messages' in found_tables:
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'chat_messages' 
                AND table_schema = 'public'
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            
            critical_columns = ['tools_used', 'mcp_server_responses']
            found_columns = [col[0] for col in columns]
            
            for col in critical_columns:
                if col in found_columns:
                    print(f"   ✅ {col}")
                else:
                    print(f"   ❌ {col} - MISSING")
            
            print(f"\n📝 All columns in chat_messages:")
            for col in columns:
                print(f"   {col[0]} ({col[1]})")
        
        # Check critical columns in agents
        print(f"\n🔍 Checking agents columns:")
        if 'agents' in found_tables:
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'agents' 
                AND table_schema = 'public'
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            
            critical_columns = ['mcp_servers']
            found_columns = [col[0] for col in columns]
            
            for col in critical_columns:
                if col in found_columns:
                    print(f"   ✅ {col}")
                else:
                    print(f"   ❌ {col} - MISSING")
        
        # Test a simple query
        print(f"\n🧪 Testing basic queries:")
        try:
            cursor.execute("SELECT COUNT(*) FROM agents")
            agent_count = cursor.fetchone()[0]
            print(f"   ✅ Agents table accessible: {agent_count} records")
        except Exception as e:
            print(f"   ❌ Agents query failed: {e}")
            
        try:
            cursor.execute("SELECT COUNT(*) FROM chat_messages")  
            message_count = cursor.fetchone()[0]
            print(f"   ✅ Chat messages table accessible: {message_count} records")
        except Exception as e:
            print(f"   ❌ Chat messages query failed: {e}")
        
        # Test relationship query (this is likely what's failing)
        print(f"\n🔄 Testing relationship queries:")
        try:
            cursor.execute("""
                SELECT a.id, a.name, cm.role, cm.content 
                FROM agents a
                LEFT JOIN chat_sessions cs ON a.id = cs.agent_id
                LEFT JOIN chat_messages cm ON cs.id = cm.session_id
                LIMIT 1
            """)
            result = cursor.fetchone()
            print(f"   ✅ Relationship query works: {result}")
        except Exception as e:
            print(f"   ❌ Relationship query failed: {e}")
            print(f"   🚨 THIS IS LIKELY THE CAUSE!")
        
        cursor.close()
        conn.close()
        
        print(f"\n📊 SUMMARY:")
        print(f"   ✅ Connection: Working")
        print(f"   ✅ Tables: {len(found_tables)}/{len(expected_tables)} expected")
        print(f"   ❌ Missing tables: {missing_tables}")
        print(f"   ⚠️ Extra tables: {extra_tables}")
        
        if missing_tables:
            print(f"\n🎯 NEXT STEP: Run migrations to create missing tables")
            return False
        else:
            print(f"\n✅ All expected tables present!")
            return True
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print(f"🚨 DATABASE CONNECTION IS THE PROBLEM!")
        return False

if __name__ == "__main__":
    check_railway_schema()
