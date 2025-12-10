#!/usr/bin/env python3
"""
Direct fix for Railway production database schema
Adds missing columns: tools_used, mcp_server_responses, mcp_servers
"""

import os
import psycopg2
from dotenv import load_dotenv
import re

def fix_railway_database():
    load_dotenv()
    
    # Get DATABASE_URL and clean it
    db_url = os.getenv('DATABASE_URL', '')
    
    # Remove invalid schema parameter if present
    db_url = re.sub(r'\?schema=.*$', '', db_url)
    print(f'Cleaned DB URL: {db_url[:50]}...')

    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print('\n=== Checking existing schema ===')
        
        # Check what tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        print(f'Tables found: {tables}')
        
        # Check chat_messages columns
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'chat_messages' 
            AND table_schema = 'public'
            ORDER BY ordinal_position
        """)
        chat_cols = cursor.fetchall()
        print(f'\nchat_messages columns:')
        for col in chat_cols:
            print(f'  {col[0]}: {col[1]}')
        
        print('\n=== Adding missing columns ===')
        
        # Add tools_used to chat_messages
        if 'tools_used' not in [col[0] for col in chat_cols]:
            print('Adding tools_used column to chat_messages...')
            cursor.execute('ALTER TABLE chat_messages ADD COLUMN tools_used JSON;')
            print('tools_used added successfully')
        else:
            print('tools_used already exists in chat_messages')
        
        # Add mcp_server_responses to chat_messages
        if 'mcp_server_responses' not in [col[0] for col in chat_cols]:
            print('Adding mcp_server_responses column to chat_messages...')
            cursor.execute('ALTER TABLE chat_messages ADD COLUMN mcp_server_responses JSON;')
            print('mcp_server_responses added successfully')
        else:
            print('mcp_server_responses already exists in chat_messages')
        
        # Check agents columns
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'agents' 
            AND table_schema = 'public'
            ORDER BY ordinal_position
        """)
        agent_cols = cursor.fetchall()
        print(f'\nagents columns:')
        for col in agent_cols:
            print(f'  {col[0]}: {col[1]}')
        
        # Add mcp_servers to agents
        if 'mcp_servers' not in [col[0] for col in agent_cols]:
            print('Adding mcp_servers column to agents...')
            cursor.execute('ALTER TABLE agents ADD COLUMN mcp_servers JSON;')
            print('mcp_servers added successfully')
        else:
            print('mcp_servers already exists in agents')
        
        print('\n=== Verifying final schema ===')
        
        # Verify chat_messages final columns
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'chat_messages' 
            AND table_schema = 'public'
            ORDER BY ordinal_position
        """)
        final_chat_cols = cursor.fetchall()
        print(f'\nFinal chat_messages columns:')
        for col in final_chat_cols:
            print(f'  {col[0]}: {col[1]}')
        
        # Verify agents final columns
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'agents' 
            AND table_schema = 'public'
            ORDER BY ordinal_position
        """)
        final_agent_cols = cursor.fetchall()
        print(f'\nFinal agents columns:')
        for col in final_agent_cols:
            print(f'  {col[0]}: {col[1]}')
        
        conn.close()
        print('\n✅ Railway production database schema fixed successfully!')
        return True
        
    except Exception as e:
        print(f'❌ Error fixing database: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    fix_railway_database()
