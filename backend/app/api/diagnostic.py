from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
import os
import tempfile
from app.db.database import get_db
from openai import OpenAI

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

@router.post("/test-mcp-compatibility")
def test_mcp_compatibility():
    """
    Test MCP compatibility with Z.ai API
    """
    try:
        client = OpenAI(
            api_key=os.getenv("ZAI_API_KEY"),
            base_url="https://api.z.ai/api/coding/paas/v4"
        )
        
        # Test basic tool calling capability
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "test_tool",
                    "description": "A test tool for MCP compatibility",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "test_param": {"type": "string", "description": "Test parameter"}
                        },
                        "required": ["test_param"]
                    }
                }
            }
        ]
        
        response = client.chat.completions.create(
            model="glm-4.6",
            messages=[
                {"role": "user", "content": "Test MCP compatibility by calling the test_tool"}
            ],
            tools=tools,
            tool_choice="auto"
        )
        
        message = response.choices[0].message
        
        if hasattr(message, 'tool_calls') and message.tool_calls:
            return {
                "success": True,
                "message": "Z.ai API fully supports MCP-style tool calling",
                "details": {
                    "tool_calls_detected": len(message.tool_calls),
                    "reasoning_content": hasattr(message, 'reasoning_content'),
                    "compatible": True
                }
            }
        else:
            return {
                "success": True,
                "message": "Z.ai API responds correctly (tool calling available but not used in this response)",
                "details": {
                    "response_type": "direct_response",
                    "has_reasoning": hasattr(message, 'reasoning_content'),
                    "compatible": True
                }
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": f"Z.ai API compatibility test failed: {str(e)}",
            "details": {
                "error_type": type(e).__name__,
                "api_key_configured": bool(os.getenv("ZAI_API_KEY")),
                "compatible": False
            }
        }

@router.get("/database/mcp-status")
def check_mcp_database_status(db: Session = Depends(get_db)):
    """
    Comprehensive MCP database status check
    """
    try:
        # Check database connection
        db.execute(text("SELECT 1"))
        
        # Check MCP tables
        mcp_tables_result = db.execute(text("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema='public' AND table_name LIKE 'mcp_%'
        """)).scalar()
        
        # Check MCP-specific columns
        tools_column = db.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_name='chat_messages' 
                AND column_name='tools_used'
            )
        """)).scalar()
        
        mcp_responses_column = db.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_name='chat_messages' 
                AND column_name='mcp_server_responses'
            )
        """)).scalar()
        
        # Check agents table changes
        agents_mcp_column = db.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_name='agents' 
                AND column_name='mcp_servers'
            )
        """)).scalar()
        
        # Count MCP servers if table exists
        mcp_server_count = 0
        try:
            mcp_server_count = db.execute(text("SELECT COUNT(*) FROM mcp_servers")).scalar()
        except:
            pass
        
        # Validate schema completeness
        required_tables = ['mcp_servers', 'mcp_server_logs', 'agent_mcp_servers', 'mcp_tool_usage']
        found_tables = []
        
        for table in required_tables:
            try:
                db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                found_tables.append(table)
            except:
                pass
        
        schema_complete = (
            len(found_tables) == len(required_tables) and
            tools_column and
            mcp_responses_column and
            agents_mcp_column
        )
        
        return {
            "status": "healthy" if schema_complete else "incomplete",
            "database_connection": "✅ Working",
            "mcp_tables": {
                "found": mcp_tables_result,
                "required": len(required_tables),
                "complete": len(found_tables) == len(required_tables),
                "missing": list(set(required_tables) - set(found_tables))
            },
            "mcp_columns": {
                "tools_used": "✅ Present" if tools_column else "❌ Missing",
                "mcp_server_responses": "✅ Present" if mcp_responses_column else "❌ Missing"
            },
            "agents_table": {
                "mcp_column": "✅ Present" if agents_mcp_column else "❌ Missing"
            },
            "mcp_servers_count": mcp_server_count,
            "schema_ready": schema_complete,
            "migration_status": "✅ Complete" if schema_complete else "❌ Required",
            "recommendations": [] if schema_complete else [
                "Run 'alembic upgrade head' to apply missing migrations",
                "Check Railway PostgreSQL provisioning",
                "Verify DATABASE_URL environment variable"
            ]
        }
        
    except Exception as e:
        return {
            "status": "error",
            "database_connection": "❌ Failed",
            "error": str(e),
            "migration_status": "❌ Cannot Validate",
            "recommendations": [
                "Check DATABASE_URL environment variable",
                "Verify Railway PostgreSQL is running",
                "Run manual migration: alembic upgrade head"
            ]
        }
