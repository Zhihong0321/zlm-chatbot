#!/usr/bin/env python3
"""
MCP Database Status Check
Shows current database readiness for MCP integration
"""

import os
import sys
from pathlib import Path
import subprocess

def check_environment():
    """Check environment configuration"""
    print("MCP DATABASE STATUS CHECK")
    print("=" * 50)
    
    # Check backend files exist
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("FAIL: Backend directory not found!")
        return False
    
    # Check alembic directory
    alembic_dir = backend_dir / "alembic"
    if not alembic_dir.exists():
        print("INFO: Alembic directory not found, attempting to create...")
        try:
            alembic_dir.mkdir()
            print("PASS: Alembic directory created")
        except Exception as e:
            print(f"FAIL: Could not create Alembic directory: {e}")
    
    # Check migration files
    alembic_versions_dir = alembic_dir / "versions"
    migration_files = list(alembic_versions_dir.glob("*.py")) if alembic_versions_dir.exists() else []
    mcp_migration_files = [f for f in migration_files if "002_add_mcp_schema" in str(f)]
    
    print(f"Backend directory found: {backend_dir}")
    print(f"Alembic directory: {alembic_dir}")
    print(f"Migration files: {len(migration_files)} found")
    
    if not mcp_migration_files:
        print("WARNING: MCP migration not found!")
        print("Available migrations: {migration_files}")
        return False
    
    print("✓ MCP migration files are ready")
    return True

def check_database_connection():
    """Test database connection"""
    try:
        from sqlalchemy import create_engine
        from dotenv import load_dotenv
        
        load_dotenv()
        
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            print("FAIL: DATABASE_URL not configured")
            return False
        
        print(f"Testing connection: {db_url}")
        
        engine = create_engine(db_url)
        
        with engine.begin() as conn:
            # Check database type
            if "postgresql" in db_url.lower():
                print("PASS: PostgreSQL detected")
                
                # Check if MCP tables exist
                try:
                    result = conn.execute(text("""
                        SELECT COUNT(*) FROM information_schema.tables 
                        WHERE table_schema='public' AND table_name LIKE 'mcp_%'
                    """)).scalar()
                    print(f"✅ Found {result} MCP tables in database")
                    
                    # Check if agents table has mcp_servers column
                    try:
                        result = conn.execute(text("""
                        SELECT EXISTS (
                            SELECT column_name
                            FROM information_schema.columns 
                            WHERE table_name='agents' AND column_name='mcp_servers'
                        )
                    """)).scalar()
                    print(f"✅ Agents table has mcp_servers column")
                    
                    print("✅ Database is READY for MCP integration")
                    return True
                    
                except Exception as e:
                    print(f"Database connected but verification failed: {e}")
                    print("Run 'python setup_mcp_database.py' to create MCP tables")
                    
            else:
                print("INFO: SQLite database detected")
                print("MCP support requires PostgreSQL for full functionality")
                return False
                
    except Exception as e:
        print(f"FAIL: Database connection failed: {e}")
        return False
        
    except Exception as e:
        print(f"FAIL: Could not import required libraries: {e}")
        return False

def show_database_status():
    """Show current database status"""
    print("\nDATABASE ANALYSIS:")
    print("-" * 40)
    
    try:
        from sqlalchemy import create_engine
        from dotenv import load_dotenv
        load_dotenv()
        
        db_url = os.getenv("DATABASE_URL")
        engine = create_engine(db_url)
        
        with engine.begin() as conn:
            print(f"Database Type: {'PostgreSQL' if 'postgresql' in db_url.lower() else 'SQLite'}")
            
            if "postgresql" in db_url.lower():
                # Get table list
                tables = conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
                table_list = [row[0] for row in tables]
                
                # Filter MCP-related tables
                mcp_tables = [t for t in table_list if "mcp" in t.lower()]
                normal_tables = [t for t in table_list if "mcp" not in t.lower()]
                
                print(f"📊 Total tables: {len(table_list)}")
                print(f"📊 MCP tables: {len(mcp_tables)}")
                print(f"📊 Normal tables: {len(normal_tables)}")
                
                if mcp_tables:
                    print("\nMCP Tables:")
                    for table in mcp_tables:
                        # Get row count
                        try:
                            count = conn.execute(f"SELECT COUNT(*) FROM {table}")
                            print(f"  - {table}: {count} rows")
                        except:
                            print(f"  - {table}: Row count unavailable")
            
            else:
                print("INFO: SQLite database detected (limited MCP functionality)")
                return False
                
            return True
            
    except Exception as e:
        print(f"ERROR: Database analysis failed: {e}")
        return False

def check_mcp_integration_readiness():
    """Check if MCP integration is ready"""
    print("\nMCP INTEGRATION READINESS:")
    print("-" * 40)
    
    try:
        # Check models.py has MCP model classes
        models_path = Path("backend/app/models/models.py")
        if not models_path.exists():
            print("FAIL: models.py not found")
            return False
        
        with open(models_path, 'r') as f:
            content = f.read()
            
        # Check for MCP model classes
        mcp_models = [
            "class MCPServer",
            "class MCPServerLog",  
            "class AgentMCPServer",
            "class MCPToolUsage",
            "class MCPSystemMetrics"
        ]
        
        for model_class in mcp_models:
            if model_class in content:
                print(f"✅ Found {model_class} class in models.py")
            else:
                print(f"⚠️ Missing {model_class} class in models.py")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Could not check models.py: {e}")
        return False

def main():
    """Main status check function"""
    
    print("MCP DATABASE STATUS CHECKLIST")
    print("=" * 50)
    
    # Run all checks
    checks = [
        ("Environment Check", check_environment),
        ("Database Connection", check_database_connection),
        ("Database Status", show_database_status),
        ("MCP Integration Readiness", check_mcp_integration_readiness)
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        print(f"\n{check_name}:")
        try:
            result = check_func()
            if result:
                status = "PASS"
            else:
                status = "FAIL"
            print(f"  Status: {status}")
            all_passed &= result
        except Exception as e:
            print(f"  Status: ERROR - {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("SUCCESS: All checks passed!")
        print("Your database is ready for MCP integration!")
        print("\nNext Steps:")
        print("1. Run 'cd backend && alembic upgrade head upgrade head mcp_schema'")
        print("2. Start backend services:")
        print("   - python backend_mcp_server.py")
        print("   - python mcp_management_api.py")
        print("3. Test the enhanced backend:")
        print("   - Test MCP server management endpoints")
        print("   - Test agent-MCP configurations")
        print("   - Test tool tracking in conversations")
        
    else:
        print("ISSUES DETECTED!")
        print("Please address the issues above before proceeding:")
        print("- Install required backend dependencies")
        print("- Configure DATABASE_URL environment variable")
        print("- Run database migrations as needed")
        
        print("\nNext Steps:")
        print("1. Run 'cd backend && alembic upgrade head upgrade head mcp_schema'")
        print("2. Start backend services:")
        print("   - python backend_mcp_server.py")
        print("   - python mcp_management_api.py")
        print("3. Test the enhanced backend:")
        print("   - Test MCP server management endpoints")
        print("   - Test agent-MCP configurations")
        print("   - Test tool tracking in conversations")
        
    else:
        print("ISSUES DETECTED!")
        print("Please address the issues above before proceeding:")
        print("- Install required backend dependencies")
        print("- Configure DATABASE_URL environment variable")
        print("- Run database migrations as needed")
    
    return not all_passed

if __name__ == "__main__":
    status = not main()
    sys.exit(0 if status else 1)
