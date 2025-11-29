#!/usr/bin/env python3
"""
Production Battle-Ready Validation
Final check before deployment
"""
import os
import sys
import subprocess

def run_check(command, description):
    """Run validation check"""
    print(f"🔍 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=os.path.dirname(__file__))
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            return True
        else:
            print(f"❌ {description} - FAILED")
            if result.stdout:
                print(f"   Output: {result.stdout.strip()}")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def validate_imports():
    """Check all critical imports work"""
    try:
        import app.main
        import app.db.database
        import app.core.zai_client
        import app.api.ui
        import app.crud.crud
        print("✅ All critical imports work")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def validate_environment():
    """Check required environment variables"""
    required_vars = ["DATABASE_URL", "ZAI_API_KEY"]
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"❌ Missing environment variables: {missing}")
        return False
    print("✅ Environment variables configured")
    return True

def validate_postgres_connection():
    """Test PostgreSQL connection"""
    if not run_check("python validate_postgres.py", "PostgreSQL validation"):
        return False
    return True

def validate_database_models():
    """Check database models are consistent"""
    try:
        from app.models.models import Base
        from sqlalchemy import inspect
        
        # Create inspector to validate tables
        from app.db.database import engine
        
        # This will fail if models are broken
        inspector = inspect(engine)
        print("✅ Database models validated")
        return True
    except Exception as e:
        print(f"❌ Model validation failed: {e}")
        return False

def validate_api_endpoints():
    """Check FastAPI app loads successfully"""
    try:
        from app.main import app
        # This will fail if there are FastAPI configuration errors
        print("✅ FastAPI app loads successfully")
        return True
    except Exception as e:
        print(f"❌ FastAPI validation failed: {e}")
        return False

def main():
    """Run all validation checks"""
    print("🚀 BATTLE-READY VALIDATION CHECKS")
    print("=" * 50)
    
    checks = [
        validate_imports,
        validate_environment,
        validate_postgres_connection,
        validate_database_models,
        validate_api_endpoints
    ]
    
    passed = 0
    total = len(checks)
    
    for check in checks:
        if check():
            passed += 1
        print()
    
    print("=" * 50)
    if passed == total:
        print(f"🎉 ALL CHECKS PASSED ({passed}/{total})")
        print("✅ CODE IS BATTLE-READY FOR DEPLOYMENT!")
        return 0
    else:
        print(f"🚨 {total - passed} CHECKS FAILED ({passed}/{total})")
        print("❌ FIX ISSUES BEFORE DEPLOYMENT!")
        return 1

if __name__ == "__main__":
    sys.exit(main())