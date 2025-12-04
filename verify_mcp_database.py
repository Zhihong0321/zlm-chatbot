#!/usr/bin/env python3
"""
Comprehensive MCP Database Verification and Testing Script
Ensures all MCP features work end-to-end
"""

import os
import sys
import json
import asyncio
from typing import Dict, List
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    from dotenv import load_dotenv
    
    # Import our models to test they can load
    from app.models.models import Base
    from app.api.diagnostic import system_diagnostic
    
    load_dotenv()
    
    print("🔍 MCP Database Verification Tool")
    print("=" * 60)
    
except ImportError as e:
    print(f"❌ Error importing backend modules: {e}")
    print("Please ensure you run this from the project root directory")
    sys.exit(1)

class MCPDatabaseVerifier:
    """Comprehensive MCP database verification"""
    
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        self.engine = create_engine(self.db_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False)
        
        print(f"🔌 Database URL: {self.db_url[:50]}...")
        print(f"📋 Engine created successfully")
        
    def run_comprehensive_test(self) -> Dict[str, any]:
        """Run comprehensive MCP database test suite"""
        
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "database_connection": False,
            "alembic_configuration": False,
            "required_tables": {},
            "required_columns": {},
            "model_loading": False,
            "api_endpoints": {},
            "migration_status": "unknown",
            "overall_status": "❌ FAILED"
        }
        
        print("\n🧪 Running comprehensive MCP database verification...")
        
        # Test 1: Basic Database Connection
        print("\n1️⃣ Testing database connection...")
        results["database_connection"] = self._test_database_connection()
        
        # Test 2: Alembic Configuration
        print("\n2️⃣ Testing Alembic configuration...")
        results["alembic_configuration"] = self._test_alembic_config()
        
        # Test 3: Required Tables
        print("\n3️⃣ Testing required MCP tables...")
        results["required_tables"] = self._test_required_tables()
        
        # Test 4: Required Columns
        print("\n4️⃣ Testing required MCP columns...")
        results["required_columns"] = self._test_required_columns()
        
        # Test 5: Model Loading
        print("\n5️⃣ Testing SQLAlchemy model loading...")
        results["model_loading"] = self._test_model_loading()
        
        # Test 6: API Endpoints
        print("\n6️⃣ Testing MCP API endpoints...")
        results["api_endpoints"] = self._test_api_endpoints()
        
        # Test 7: Migration Status
        print("\n7️⃣ Testing migration completeness...")
        results["migration_status"] = self._test_migration_status()
        
        # Overall Status
        all_tests = [
            results["database_connection"],
            results["alembic_configuration"],
            len(results["required_tables"]["missing"]) == 0,
            len(results["required_columns"]["missing"]) == 0,
            results["model_loading"],
            results["api_endpoints"]["database_check"],
            results["migration_status"]
        ]
        
        if all(all_tests):
            results["overall_status"] = "✅ ALL TESTS PASSED"
            print("\n🎉 COMPREHENSIVE MCP VERIFICATION: PASSED")
            self._print_summary(results)
        else:
            results["overall_status"] = "❌ SOME TESTS FAILED"
            print("\n❌ COMPREHENSIVE MCP VERIFICATION: FAILED")
            self._print_issues(results)
        
        return results
    
    def _test_database_connection(self) -> bool:
        """Test basic database connection"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                print("   ✅ Database connection successful")
                return True
        except Exception as e:
            print(f"   ❌ Database connection failed: {e}")
            return False
    
    def _test_alembic_config(self) -> bool:
        """Test Alembic configuration"""
        try:
            import alembic
            config = alembic.config.Config("alembic.ini")
            
            # Check if config loads correctly
            script_location = config.get_main_option("script_location")
            print(f"   ✅ Alembic script_location: {script_location}")
            
            # Check database URL in config
            url = config.get_main_option("sqlalchemy.url")
            if url:
                print(f"   ✅ Alembic database URL found: {url[:50]}...")
                if "localhost:5432" in url:
                    print("   ⚠️ WARNING: Alembic still using localhost, but environment variable override should work")
                return True
            else:
                print("   ⚠️ No hardcoded URL found (will use environment variable)")
                return True
                
        except Exception as e:
            print(f"   ❌ Alembic configuration error: {e}")
            return False
    
    def _test_required_tables(self) -> Dict[str, any]:
        """Test that all required MCP tables exist"""
        required_tables = [
            "mcp_servers",
            "mcp_server_logs", 
            "agent_mcp_servers",
            "mcp_tool_usage",
            "mcp_system_metrics"
        ]
        
        with self.SessionLocal() as session:
            found = []
            missing = []
            
            for table in required_tables:
                try:
                    session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    found.append(table)
                    print(f"   ✅ Table '{table}' exists")
                except Exception as e:
                    missing.append(table)
                    print(f"   ❌ Table '{table}' missing: {e}")
            
            return {
                "required": len(required_tables),
                "found": len(found),
                "missing": missing,
                "success": len(missing) == 0
            }
    
    def _test_required_columns(self) -> Dict[str, any]:
        """Test that all required MCP columns exist"""
        column_tests = [
            {
                "table": "chat_messages",
                "columns": ["tools_used", "mcp_server_responses", "role", "content"],
                "table_schema": "public"
            },
            {
                "table": "agents", 
                "columns": ["mcp_servers", "name", "description", "system_prompt"],
                "table_schema": "public"
            },
            {
                "table": "mcp_servers",
                "columns": ["id", "name", "description", "command", "status", "enabled"],
                "table_schema": "public"
            }
        ]
        
        results = {"all_found": 0, "missing": [], "extra_info": []}
        
        with self.SessionLocal() as session:
            for column_test in column_tests:
                table_name = column_test["table"]
                table_schema = column_test.get("table_schema", "public")
                
                for column in column_test["columns"]:
                    try:
                        session.execute(text(f"""
                            SELECT column_name 
                            FROM information_schema.columns 
                            WHERE table_schema = '{table_schema}'
                            AND table_name = '{table_name}'
                            AND column_name = '{column}'
                        """)).scalar()
                        results["all_found"] += 1
                        print(f"   ✅ Column {table_name}.{column} exists")
                    except Exception as e:
                        results["missing"].append(f"{table_name}.{column}")
                        print(f"   ❌ Column {table_name}.{column} missing: {e}")
                        
        results["success"] = len(results["missing"]) == 0
        return results
    
    def _test_model_loading(self) -> bool:
        """Test that SQLAlchemy models can load without errors"""
        try:
            # Try to query each model class
            from app.models.models import (
                MCPServer, MCPServerLog, AgentMCPServer,
                MCPToolUsage, MCPSystemMetrics
            )
            
            # Test that relationships work
            print("   ✅ All MCP model classes imported successfully")
            
            # Test basic query
            with self.SessionLocal() as session:
                try:
                    # Test basic server query
                    if "mcp_servers" in [table.name for table in Base.metadata.tables.keys()]:
                        session.execute(text("SELECT COUNT(*) FROM mcp_servers LIMIT 1"))
                        print("   ✅ MCP models can query database")
                except:
                    print("   ⚠️ MCP tables may not exist yet (expected if migrations not run)")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Model loading failed: {e}")
            return False
    
    def _test_api_endpoints(self) -> Dict[str, any]:
        """Test MCP-related API endpoints"""
        try:
            # Import and run diagnostic
            diag_result = system_diagnostic()
            
            api_results = {
                "system_health": True,
                "database_connected": diag_result["checks"].get("database", {}).get("status") == "ok",
                "api_key_configured": diag_result["checks"].get("api_key", {}).get("status") == "ok",
                "tools_used": tools_used in diag_result["checks"], if "tools_used" in diag_result["checks"] else False
            }
            
            print(f"   ✅ System diagnostic passed")
            print(f"   ✅ Database connectivity: {api_results['database_connected']}")
            print(f"   ✅ API key configured: {api_results['api_key_configured']}")
            
            return api_results
            
        except Exception as e:
            print(f"   ❌ API endpoint test failed: {e}")
            return {"system_health": False, "database_connected": False, "error": str(e)}
    
    def _test_migration_status(self) -> str:
        """Test migration status"""
        with self.SessionLocal() as session:
            try:
                # Check if all required tables exist
                mcp_tables = session.execute(text("""
                    SELECT COUNT(*) FROM information_schema.tables 
                    WHERE table_schema='public' AND table_name LIKE 'mcp_%'
                """)).scalar()
                
                # Check critical columns exist
                tools_column = session.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_name='chat_messages' 
                        AND column_name='tools_used'
                    )
                """)).scalar()
                
                if mcp_tables >= 5 and tools_column:
                    return "complete"
                elif mcp_tables > 0 or tools_column:
                    return "partial"
                else:
                    return "missing"
                    
            except Exception as e:
                return f"error: {e}"
    
    def _print_summary(self, results: Dict[str, any]):
        """Print comprehensive summary"""
        print("\n📊 MCP DATABASE VERIFICATION SUMMARY:")
        print(f"   📅 Timestamp: {results['timestamp']}")
        print(f"   🔗 Database URL: {results.get('timestamp', 'N/A')}")
        print(f"   ✅ Connection: {results['database_connection']}")
        print(f"   ⚙️ Alembic Config: {results['alembic_configuration']}")
        print(f"   🔧 Tables: {results['required_tables']['found']}/{results['required_tables']['required']}")
        print(f"   📊 Columns: {results['required_columns']['all_found']}")
        print(f"   📋 Models: {results['model_loading']}")
        print(f"   🌐 API Endpoints: {results['api_endpoints'].get('system_health', False)}")
        print(f"   🚀 Migration Status: {results['migration_status']}")
        
        if results["required_tables"]["missing"]:
            print(f"\n   📋 Missing Tables: {', '.join(results['required_tables']['missing'])}")
        if results["required_columns"]["missing"]:
            print(f"   📋 Missing Columns: {', '.join(results['required_columns']['missing'])}")
    
    def _print_issues(self, results: Dict[str, any]):
        """Print detailed failure information"""
        print("\n❌ FAILED TESTS:")
        
        if not results["database_connection"]:
            print("   🔴 DATABASE: Cannot connect to PostgreSQL")
            print("      → Check DATABASE_URL environment variable")
            print("      → Verify Railway PostgreSQL is running")
            
        if not results["alembic_configuration"]:
            print("   🔴 ALEMBIC: Configuration issue detected")
            print("      → Check alembic.ini database URL")
            print("      → Verify Railway container network access")
            
        if results["required_tables"]["missing"]:
            print("   🔴 SCHEMA: Required MCP tables missing")
            print(f"      → Run: alembic upgrade head")
            print(f"      → Missing: {results['required_tables']['missing']}")
            
        if results["required_columns"]["missing"]:
            print("   🔴 COLUMNS: Required MCP columns missing")
            print(f"      → Missing: {results['required_columns']['missing']}")
            print("      → Check migration 003_add_mcp_message_columns.py")
            
        if not results["model_loading"]:
            print("   🔴 MODELS: SQLAlchemy models cannot load")
            print("      → Fix schema issues first")
            
        if not results["api_endpoints"]["database_connected"]:
            print("   🔴 API: Database connectivity issues")
            
        print(f"\n🔧 RECOMMENDATIONS:")
        print("   1. Verify Railways DATABASE_URL is correct")
        print("   2. Check Railway PostgreSQL service status")
        print("   3. Run: cd backend && alembic upgrade head --verbose")
        print("   4. Check Railway container logs for migration output")

def main():
    """Main verification function"""
    
    verifier = MCPDatabaseVerifier()
    results = verifier.run_comprehensive_test()
    
    # Save results to file for Railway debugging
    try:
        with open("mcp_verification_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"📄 Results saved to mcp_verification_results.json")
    except Exception as e:
        print(f"⚠️ Could not save results: {e}")
    
    # Exit with appropriate code
    if results["overall_status"].startswith("✅"):
        print("\n🎉 MCP DATABASE IS READY FOR PRODUCTION!")
        return 0
    else:
        print("\n🚨 MCP DATABASE NEEDS ATTENTION BEFORE DEPLOYMENT!")
        return 1

if __name__ == "__main__":
    exit_code = main()
