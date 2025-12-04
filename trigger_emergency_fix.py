#!/usr/bin/env python3
"""
Add this to your Railway app to trigger emergency schema fix
"""

from fastapi import APIRouter
import os
import sys

# Add current directory to Python path so we can import our fix script
sys.path.append('/app')

router = APIRouter(prefix="/emergency", tags=["emergency"])

@router.post("/fix-schema")
def trigger_emergency_fix():
    """Trigger emergency schema fix"""
    try:
        # Import and run the emergency fix
        from emergency_schema_fix import emergency_schema_fix
        
        success = emergency_schema_fix()
        
        if success:
            return {
                "status": "success", 
                "message": "Emergency schema fix completed successfully"
            }
        else:
            return {
                "status": "failed", 
                "message": "Emergency schema fix failed - check logs"
            }
            
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Failed to run emergency fix: {str(e)}"
        }
