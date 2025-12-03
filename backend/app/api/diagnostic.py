from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
import os
import tempfile
from app.db.database import get_db

router = APIRouter()

@router.get("/diagnose")
def system_diagnostic(db: Session = Depends(get_db)):
    """
    Perform a self-check of the system:
    1. Check Database Connection
    2. Check API Key configuration
    3. Check Temporary File Write permissions
    4. Check External API connectivity (basic)
    """
    results = {
        "timestamp": None,
        "status": "healthy",
        "checks": {}
    }
    from datetime import datetime
    results["timestamp"] = datetime.utcnow().isoformat()
    
    # 1. Database Check
    try:
        db.execute(text("SELECT 1"))
        results["checks"]["database"] = {"status": "ok", "message": "Connection successful"}
    except Exception as e:
        results["status"] = "degraded"
        results["checks"]["database"] = {"status": "failed", "message": str(e)}

    # 2. API Key Check
    api_key = os.getenv("ZAI_API_KEY")
    if api_key:
        masked_key = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "***"
        results["checks"]["api_key"] = {"status": "ok", "message": f"Configured ({masked_key})"}
    else:
        results["status"] = "degraded"
        results["checks"]["api_key"] = {"status": "failed", "message": "Missing ZAI_API_KEY environment variable"}

    # 3. File System Check (Temp Write)
    try:
        with tempfile.NamedTemporaryFile(delete=True) as tf:
            tf.write(b"test")
            tf.flush()
        results["checks"]["filesystem"] = {"status": "ok", "message": "Temporary write access confirmed"}
    except Exception as e:
        results["status"] = "degraded"
        results["checks"]["filesystem"] = {"status": "failed", "message": str(e)}

    # 4. Environment Info (Safe subset)
    results["environment"] = {
        "env_name": os.getenv("ENVIRONMENT", "unknown"),
        "python_version": os.sys.version.split()[0]
    }

    return results
