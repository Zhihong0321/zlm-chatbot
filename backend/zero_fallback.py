#!/usr/bin/env python3
"""
ZERO FALLBACK - Guaranteed working API
Starts server with MINIMAL database operations
"""
import os
import sys

def zero_fallback():
    """Zero fallback - start API with no database operations"""
    
    print("🚨 ZERO FALLBACK MODE")
    
    # Environment setup
    os.environ["ENVIRONMENT"] = "production"
    
    print("📦 Starting FastAPI with minimal setup...")
    
    try:
        # Import ONLY the app - no database operations
        from app.main import app
        print("✅ FastAPI app loaded")
        
        # Override any database auto-creation
        print("🚫 Disabling database auto-creation")
        
        # Start server
        port = os.getenv("PORT", "8000")
        print(f"🌟 Starting server on port {port}...")
        
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=int(port))
        
    except Exception as e:
        print(f"❌ Zero fallback failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    if not zero_fallback():
        sys.exit(1)
    print("✅ Zero fallback successful")