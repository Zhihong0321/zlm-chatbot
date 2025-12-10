#!/usr/bin/env python3
"""
Direct SQL fix for missing database columns in production
"""

import os
import psycopg2
from dotenv import load_dotenv

def fix_production_database():
    load_dotenv()
    # Clean the DATABASE_URL by removing invalid schema parameter
    db_url = os.getenv('DATABASE_URL', '')
    if '?schema=public' in db_url:
        db_url = db_url.split('?schema=public')[0]
    
    print(f'Clean DB URL: {db_url[:50]}...')

    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print('\n=== Checking chat_messages columns ===')
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'chat_messages' 
            AND table_schema = 'public'
            ORDER BY ordinal_position
        """)
        cols = cursor.fetchall()
        for col in cols:
            print(f'  {col[0]}: {col[1]}')
        
        print('\n=== Adding missing columns ===')
        
        # Check if tools_used exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'chat_messages' 
            AND column_name = 'tools_used'
        """)
        if not cursor.fetchone():
            print('Adding tools_used column...')
            cursor.execute('ALTER TABLE chat_messages ADD COLUMN tools_used JSON;')
            print('tools_used added')
        else:
            print('tools_used already exists')
        
        # Check if mcp_server_responses exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'chat_messages' 
            AND column_name = 'mcp_server_responses'
        """)
        if not cursor.fetchone():
            print('Adding mcp_server_responses column...')
            cursor.execute('ALTER TABLE chat_messages ADD COLUMN mcp_server_responses JSON;')
            print('mcp_server_responses added')
        else:
            print('mcp_server_responses already exists')
        
        print('\n=== Verifying final schema ===')
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'chat_messages' 
            AND table_schema = 'public'
            ORDER BY ordinal_position
        """)
        final_cols = cursor.fetchall()
        for col in final_cols:
            print(f'  {col[0]}: {col[1]}')
        
        conn.close()
        print('\nDatabase schema fixed successfully!')
        return True
        
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    fix_production_database()
