#!/usr/bin/env python3
"""
Production Database Validation - Ensures PostgreSQL ONLY
"""

import os
import sys

def validate_database_setup():
    """Validate that we're NOT using SQLite"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ ERROR: DATABASE_URL not configured")
        return False
    
    if database_url.startswith("sqlite"):
        print("❌ ERROR: SQLite detected! This is production - PostgreSQL required!")
        print(f"   Current DATABASE_URL: {database_url}")
        return False
    
    if not database_url.startswith("postgresql"):
        print(f"❌ ERROR: Invalid database type detected: {database_url.split(':')[0]}")
        print("   Only PostgreSQL allowed in production!")
        return False
    
    print(f"✅ PostgreSQL validation passed: {database_url.split('@')[1] if '@' in database_url else 'PostgreSQL URL'}")
    return True

if __name__ == "__main__":
    if not validate_database_setup():
        sys.exit(1)
    print("✅ Ready for production with PostgreSQL")