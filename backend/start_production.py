#!/usr/bin/env python3
"""
Production startup script for Railway
This script runs database migrations and initialization before starting the server
"""
import os
import sys
import subprocess

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed")
            return True
        else:
            print(f"❌ {description} failed:")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False

def main():
    """Production startup sequence"""
    print("🚀 Starting Railway production setup...")
    
    # Set environment for production
    os.environ["ENVIRONMENT"] = "production"
    
    # CRITICAL: Fix database schema first
    if not run_command("python fix_database_schema.py", "Database schema fix"):
        print("❌ Database schema fix failed!")
        sys.exit(1)
    
    # Run safe database setup (preserves existing data)
    if not run_command("python safe_db_setup.py", "Safe database setup"):
        print("❌ Database setup failed!")
        sys.exit(1)
    
    # Start the FastAPI server
    print("🌟 Starting FastAPI server...")
    os.system("uvicorn app.main:app --host 0.0.0.0 --port $PORT")

if __name__ == "__main__":
    main()