#!/usr/bin/env python3
"""Check current deployment mode and configuration"""

import os
from pathlib import Path

def check_deployment_mode():
    print("DEPLOYMENT MODE CHECKER")
    print("=" * 50)
    
    # Check which .env file is being used
    env_file = Path(".env")
    if not env_file.exists():
        print("ERROR: No .env file found")
        print("   Run: switch-to-local or switch-to-railway")
        return
    
    env_content = env_file.read_text()
    
    # Detect mode based on DATABASE_URL
    if "localhost" in env_content or "127.0.0.1" in env_content:
        print("Mode: LOCAL DEVELOPMENT")
        print("   Database: Local PostgreSQL")
        print("   Port: 5433 (Docker)")
        
        # Check if PostgreSQL container is running
        try:
            import subprocess
            result = subprocess.run(["docker", "ps"], capture_output=True, text=True)
            if "oneapi-postgres" in result.stdout:
                print("   PostgreSQL container: RUNNING")
            else:
                print("   PostgreSQL container: NOT RUNNING")
        except:
            print("   Unable to check container status")
            
    elif "railway" in env_content.lower() or "RAILWAY" in env_content:
        print("🚂 Mode: RAILWAY PRODUCTION")
        print("   Database: Railway PostgreSQL (managed)")
        print("   Deployment: Automatic via GitHub push")
        
    else:
        print("❓ Mode: UNKNOWN")
        print("   Check .env file contents")
    
    print("\n📊 Environment Variables:")
    print(f"   DATABASE_URL: {os.getenv('DATABASE_URL', 'Not set')}")
    print(f"   ENVIRONMENT: {os.getenv('ENVIRONMENT', 'Not set')}")
    print(f"   ZAI_API_KEY: {'✅ Set' if os.getenv('ZAI_API_KEY') else '❌ Not set'}")
    
    # Test database connection if URL is set
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        print(f"\n🔗 Testing database connection...")
        try:
            import psycopg2
            conn = psycopg2.connect(db_url)
            print("   ✅ Database connection: SUCCESS")
            
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema='public';")
            table_count = cursor.fetchone()[0]
            print(f"   📋 Tables found: {table_count}")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"   ❌ Database connection failed: {e}")
    else:
        print(f"\n⚠️ DATABASE_URL not configured")

if __name__ == "__main__":
    check_deployment_mode()
