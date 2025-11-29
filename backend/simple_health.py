#!/usr/bin/env python3
"""
SIMPLE HEALTH CHECK - Works without database tables
Tests API and database connection separately
"""
import os
import sys
from datetime import datetime

def simple_health():
    """Simple health check that works even if database is broken"""
    
    health_data = {
        "status": "unknown",
        "timestamp": datetime.utcnow().isoformat(),
        "details": {}
    }
    
    # Test 1: Environment variables
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        if "postgresql" in database_url:
            health_data["details"]["database"] = {
                "type": "PostgreSQL",
                "status": "configured"
            }
        else:
            health_data["details"]["database"] = {
                "type": "Other",
                "status": database_url.split(':')[0]
            }
        
        zai_key = os.getenv("ZAI_API_KEY")
        if zai_key:
            health_data["details"]["zai_api"] = {
                "status": "configured",
                "key_length": len(zai_key)
            }
        
        # Test 2: Database connection ONLY (no table operations)
        try:
            from app.db.database import engine
            from sqlalchemy import text
            
            with engine.connect() as conn:
                result = conn.execute(text("SELECT version()")).fetchone()
                health_data["details"]["database"]["version"] = result[0].split(',')[0]
                health_data["details"]["database"]["status"] = "connected"
                
        except Exception as e:
            health_data["details"]["database"]["connection_error"] = str(e)
            health_data["details"]["database"]["status"] = "failed"
        
        # Test 3: FastAPI app loading
        try:
            from app.main import app
            health_data["details"]["api"] = {"status": "loaded"}
        except Exception as e:
            health_data["details"]["api"] = {"status": "failed", "error": str(e)}
        
        # Determine overall status
        if (health_data["details"].get("database", {}).get("status") == "connected" and
            health_data["details"].get("zai_api", {}).get("status") == "configured"):
            health_data["status"] = "healthy"
        else:
            health_data["status"] = "unhealthy"
    
    else:
        health_data["status"] = "unhealthy"
        health_data["details"]["environment"] = {"status": "missing_variables"}
    
    return health_data

if __name__ == "__main__":
    import json
    health = simple_health()
    print(json.dumps(health, indent=2))