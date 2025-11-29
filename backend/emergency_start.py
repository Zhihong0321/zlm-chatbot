#!/usr/bin/env python3
"""
EMERGENCY FALLBACK - Minimal working deployment
Bypasses all schema issues and starts API
"""
import os
import sys

def emergency_start():
    """Emergency start with minimal database setup"""
    
    print("🚨 EMERGENCY FALLBACK MODE")
    
    # Set environment
    os.environ["ENVIRONMENT"] = "production"
    
    # Check DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    if database_url and "postgresql" in database_url:
        print(f"✅ PostgreSQL detected: {database_url.split('@')[1] if '@' in database_url else 'PostgreSQL URL'}")
    else:
        print("❌ DATABASE_URL missing or not PostgreSQL")
        return False
    
    # Try basic imports first
    try:
        print("📦 Testing imports...")
        from app.main import app
        print("✅ FastAPI app imported successfully")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Test database connection ONLY (no table creation)
    try:
        print("🔍 Testing database connection...")
        from app.db.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()")).fetchone()
            print(f"✅ Database connected: {result[0].split(',')[0]}")
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    # Start server directly without any schema operations
    print("🌟 Starting emergency server...")
    os.system("uvicorn app.main:app --host 0.0.0.0 --port $PORT")
    return True

if __name__ == "__main__":
    if not emergency_start():
        sys.exit(1)