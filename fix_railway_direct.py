#!/usr/bin/env python3
"""
Direct fix using Railway environment variable RAILWAY_POSTGRES_URL
"""

import os
import psycopg2
from dotenv import load_dotenv

def fix_railway_direct():
    load_dotenv()
    
    # Try Railway environment variable first
    railway_url = os.getenv('RAILWAY_POSTGRES_URL')
    if railway_url:
        db_url = railway_url
        print(f'Using RAILWAY_POSTGRES_URL: {db_url[:50]}...')
    else:
        # Fallback to cleaned DATABASE_URL
        db_url = os.getenv('DATABASE_URL', '')
        if '?' in db_url:
            db_url = db_url.split('?')[0]
        print(f'Using cleaned DATABASE_URL: {db_url[:50]}...')

    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print('\n=== Connected successfully! ===')
        
        # Check existing schema
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        print(f'Tables: {tables}')
        
        # Get chat_messages columns
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'chat_messages' 
            AND table_schema = 'public'
            ORDER BY ordinal_position
        """)
        chat_cols = [row[0] for row in cursor.fetchall()]
        print(f'chat_messages columns: {chat_cols}')
        
        # Add missing columns to chat_messages
        missing_chat = []
        if 'tools_used' not in chat_cols:
            cursor.execute('ALTER TABLE chat_messages ADD COLUMN tools_used JSON;')
            print('Added tools_used to chat_messages')
            missing_chat.append('tools_used')
        else:
            print('tools_used already exists')
            
        if 'mcp_server_responses' not in chat_cols:
            cursor.execute('ALTER TABLE chat_messages ADD COLUMN mcp_server_responses JSON;')
            print('Added mcp_server_responses to chat_messages')
            missing_chat.append('mcp_server_responses')
        else:
            print('mcp_server_responses already exists')
        
        # Get agents columns
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'agents' 
            AND table_schema = 'public'
            ORDER BY ordinal_position
        """)
        agent_cols = [row[0] for row in cursor.fetchall()]
        print(f'agents columns: {agent_cols}')
        
        # Add missing column to agents
        if 'mcp_servers' not in agent_cols:
            cursor.execute('ALTER TABLE agents ADD COLUMN mcp_servers JSON;')
            print('Added mcp_servers to agents')
        else:
            print('mcp_servers already exists')
        
        # Verify final state
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'chat_messages' 
            AND column_name IN ('tools_used', 'mcp_server_responses')
            AND table_schema = 'public'
        """)
        verified_chat = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'agents' 
            AND column_name = 'mcp_servers'
            AND table_schema = 'public'
        """)
        verified_agent = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        print('\n=== VERIFICATION COMPLETE ===')
        print(f'chat_messages MCP columns: {verified_chat}')
        print(f'agents MCP columns: {verified_agent}')
        print('Railway production database fixed successfully!')
        
        return len(missing_chat) == 0 and 'mcp_servers' in agent_cols
        
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    fix_railway_direct()
