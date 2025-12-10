#!/usr/bin/env python3
"""Test local PostgreSQL connection and run migrations"""
import os
import sys
import psycopg2

def test_connection():
    db_url = "postgresql://postgres:postgres@127.0.0.1:5433/railway"
    print(f"Testing connection to: {db_url}")
    
    try:
        conn = psycopg2.connect(db_url)
        print("Connection successful!")
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"PostgreSQL version: {version}")
        
        cursor.execute("SELECT current_database();")
        db_name = cursor.fetchone()[0]
        print(f"Current database: {db_name}")
        
        cursor.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema='public';")
        table_count = cursor.fetchone()[0]
        print(f"Tables found: {table_count}")
        
        cursor.close()
        conn.close()
        print("Connection closed properly")
        return True
        
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

def run_alembic_migrations():
    """Run alembic migrations with proper environment setup"""
    print("Running alembic migrations...")
    
    # Set environment variable
    os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@127.0.0.1:5433/railway"
    
    # Change to backend directory and run alembic
    import subprocess
    try:
        backend_dir = os.path.join(os.getcwd(), "backend")
        result = subprocess.run(
            ["alembic", "upgrade", "heads"],
            cwd=backend_dir,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("Migrations completed successfully!")
            print(result.stdout)
            return True
        else:
            print(f"Migration failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Migration error: {e}")
        return False

if __name__ == "__main__":
    print("=== Local PostgreSQL Setup ===")
    
    # Step 1: Test connection
    if test_connection():
        print("Step 1: Database connection OK")
        
        # Step 2: Run migrations
        if run_alembic_migrations():
            print("Step 2: Migrations OK")
            print("=== DATABASE SETUP COMPLETE ===")
        else:
            print("Step 2: Migrations FAILED")
            sys.exit(1)
    else:
        print("Step 1: Database connection FAILED")
        sys.exit(1)
