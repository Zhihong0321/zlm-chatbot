#!/usr/bin/env python3
"""Simple database connectivity test"""
import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
    
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("FAIL: DATABASE_URL not found in environment")
        sys.exit(1)
    
    print(f"Database URL configured: {db_url[:50]}...")
    
    # Test if we can import SQLAlchemy (indicates backend setup)
    try:
        from sqlalchemy import create_engine
        print("PASS: SQLAlchemy available")
        
        # Test connection
        engine = create_engine(db_url)
        with engine.connect() as conn:
            print("PASS: Database connection successful")
            
            # Very basic check if we can query
            try:
                result = conn.execute("SELECT 1").scalar()
                print("PASS: Basic query works")
            except Exception as e:
                print(f"FAIL: Basic query failed: {e}")
        
        print("Database connectivity: READY")
        
    except ImportError as e:
        print(f"FAIL: Backend dependencies not available: {e}")
        print("Please run: pip install sqlalchemy psycopg2-binary python-dotenv")
        
    except Exception as e:
        print(f"FAIL: Database connection failed: {e}")
        print("Check your DATABASE_URL configuration")

    print("\nDatabase test completed!")
