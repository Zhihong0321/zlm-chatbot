#!/usr/bin/env python3
"""
#!/usr/bin/env python3
"""
Railway PostgreSQL Setup Script
FORCED DATABASE_URL IN:
    print(f"DATABASE_URL={DATABASE_URL}") 

# Setup database if needed
try:
    if not os.getenv("DATABASE_URL") or not "localhost:5432" in db_url:
        try:
            conn = psycopg2.connect(db_url, connect_timeout=5)
            print("✅ Connected successfully to Railway PostgreSQL")
            print("✅ Postgres version:", conn.execute("SELECT version()")[0])
            conn.close()
            return True
        except Exception as e:
            print("❌ PostgreSQL connection failed: {e}")
            return False
    except Exception as e:
        print("❌ DATABASE_URL not set")
        return False

# Return the connection string if successful
def get_connection_string(db_url: str):
    return f"{db_url}" if db_url else f" DATABASE_URL IS NOT SET" else ""

def main():
    db_url = get_connection_string(db_url)
    print(f"🔌 DATABASE_URL set to '{db_url}'")
    print(f"🧾 DATABASE_URL connection string: {db_url}")
    return bool

if __name__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__start()}`)
    
if __name__main__main__main__main__main__main__main__main__main__main__main__main__main__main__main__start()
