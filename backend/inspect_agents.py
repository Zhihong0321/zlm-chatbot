import sqlite3
import sys

try:
    conn = sqlite3.connect('chatbot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, system_prompt, model FROM agents WHERE name LIKE '%Billing%'")
    rows = cursor.fetchall()
    
    if not rows:
        print("No agents found with 'Billing' in the name.")
    else:
        for row in rows:
            print(f"Name: {row[0]}")
            print(f"Model: {row[2]}")
            print(f"System Prompt: {row[1]}")
            print("-" * 40)
    
    conn.close()
except Exception as e:
    print(f"Error reading DB: {e}")
