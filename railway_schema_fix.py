#!/usr/bin/env python3
"""
Railway Production Database Schema Fix
Run this script in Railway environment to fix missing columns
"""

import os
import psycopg2
import sys

def fix_railway_production():
    # Use Railway's built-in DATABASE_URL
    db_url = os.getenv('DATABASE_URL')
    
    if not db_url:
        print("ERROR: DATABASE_URL not found in environment")
        return False
        
    print(f"DATABASE_URL found: {db_url[:30]}...")
    
    # Clean any invalid schema parameters
    if '?' in db_url:
        db_url = db_url.split('?')[0]
        print(f"Cleaned DATABASE_URL: {db_url[:30]}...")
    
    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("✅ Connected to Railway database!")
        
        # Check existing chat_messages columns
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'chat_messages' 
            AND table_schema = 'public'
        """)
        existing_chat_cols = {row[0] for row in cursor.fetchall()}
        print(f"chat_messages columns: {sorted(existing_chat_cols)}")
        
        # Add missing columns to chat_messages
        missing_chat = []
        if 'tools_used' not in existing_chat_cols:
            cursor.execute('ALTER TABLE chat_messages ADD COLUMN tools_used JSON;')
            missing_chat.append('tools_used')
            print("➕ Added tools_used to chat_messages")
        else:
            print("✓ tools_used already exists")
            
        if 'mcp_server_responses' not in existing_chat_cols:
            cursor.execute('ALTER TABLE chat_messages ADD COLUMN mcp_server_responses JSON;')
            missing_chat.append('mcp_server_responses')
            print("➕ Added mcp_server_responses to chat_messages")
        else:
            print("✓ mcp_server_responses already exists")
        
        # Check existing agents columns
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'agents' 
            AND table_schema = 'public'
        """)
        existing_agent_cols = {row[0] for row in cursor.fetchall()}
        print(f"agents columns: {sorted(existing_agent_cols)}")
        
        # Add missing column to agents
        if 'mcp_servers' not in existing_agent_cols:
            cursor.execute('ALTER TABLE agents ADD COLUMN mcp_servers JSON;')
            print("➕ Added mcp_servers to agents")
        else:
            print("✓ mcp_servers already exists")
        
        # Final verification
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'chat_messages' 
            AND column_name IN ('tools_used', 'mcp_server_responses')
            AND table_schema = 'public'
        """)
        verified_chat = {row[0] for row in cursor.fetchall()}
        
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'agents' 
            AND column_name = 'mcp_servers'
            AND table_schema = 'public'
        """)
        verified_agent = {row[0] for row in cursor.fetchall()}
        
        conn.close()
        
        print("\n" + "="*50)
        print("RAILWAY PRODUCTION SCHEMA FIX COMPLETE")
        print("="*50)
        print(f"chat_messages MCP columns verified: {sorted(verified_chat)}")
        print(f"agents MCP columns verified: {sorted(verified_agent)}")
        
        success = len(missing_chat) == 0 and 'mcp_servers' in existing_agent_cols
        if success:
            print("🎉 ALL REQUIRED COLUMNS EXISTED")
        else:
            print("🔧 MISSING COLUMNS ADDED SUCCESSFULLY")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fix_railway_production()
    sys.exit(0 if success else 1)
