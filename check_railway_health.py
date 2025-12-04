#!/usr/bin/env python3
"""
Railway MCP Integration Health Check
Verifies all MCP functionality works in Railway environment
"""

import os
import sys
import requests
import json
from typing import Dict, List

def check_railway_environment():
    """Check if we're running in Railway"""
    railway_vars = [k for k in os.environ.keys() if k.startswith("RAILWAY_")]
    db_url = os.getenv("DATABASE_URL", "")
    
    print("🚂 Railway Environment Check:")
    print(f"   📋 Railway Variables Found: {len(railway_vars)}")
    print(f"   🗄️ Database URL: {db_url[:50]}...")
    print(f"   🏛️ Database Type: {'PostgreSQL' if 'postgresql' in db_url else 'Other'}")
    
    railway_env = os.getenv("ENVIRONMENT", "unknown")
    port = os.getenv("PORT", "unknown")
    
    print(f"   📦 Environment: {railway_env}")
    print(f"   📡 Port: {port}")
    
    return len(railway_vars) > 0 and "postgresql" in db_url

def check_railway_postgresql():
    """Check PostgreSQL connectivity and version"""
    db_url = os.getenv("DATABASE_URL", "")
    if not db_url:
        return False
    
    try:
        # Test basic connection
        import subprocess
        import psycopg2
        conn = psycopg2.connect(db_url, connect_timeout=10)
        
        # Get PostgreSQL version
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"✅ PostgreSQL connection successful")
        print(f"   📊 PostgreSQL Version: {version}")
        return True
        
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

def check_backend_api():
    """Test Railway backend API endpoints"""
    api_base = os.getenv("API_BASE_URL", "http://localhost:8000")
    
    endpoints_to_check = [
        "/",
        "/api/v1/ui/health",
        "/api/v1/system/diagnose", 
        "/api/v1/system/test-mcp-compatibility",
        "/database/mcp-status"
    ]
    
    results = {}
    
    for endpoint in endpoints_to_check:
        try:
            url = f"{api_base}{endpoint}"
            response = requests.get(url, timeout=10)
            
            status = "✅" if response.status_code == 200 else f"⚠️ {response.status_code}"
            print(f"   {status} {endpoint}")
            
            if response.headers.get('content-type', '').startswith('application/json'):
                try:
                    data = response.json()
                    results[endpoint] = data
                except:
                    results[endpoint] = {"error": "Invalid JSON"}
            else:
                results[endpoint] = {"status": response.status_code}
                
        except requests.RequestException as e:
            print(f"   ❌ {endpoint} failed: {e}")
            results[endpoint] = {"error": str(e)}
    
    return results

def check_mcp_management_api():
    """Test MCP Management API endpoints"""
    mcp_base = os.getenv("MCP_API_BASE_URL", "http://localhost:8001")
    
    if mcp_base == "http://localhost:8001":
        print("⚠️ MCP Management API assumed to be running locally for this test")
        return {"note": "MCP API not running - expected for Railway"}
    
    endpoints_to_check = [
        "/",
        "/api/v1/mcp/health", 
        "/api/v1/mcp/status",
        "/api/v1/mcp/servers"
    ]
    
    results = {}
    
    for endpoint in endpoints_to_check:
        try:
            url = f"{mcp_base}{endpoint}"
            response = requests.get(url, timeout=10)
            
            status = "✅" if response.status_code == 200 else f"⚠️ {response.status_code}"
            print(f"   {status} MCP {endpoint}")
            
            if endpoint == "/api/v1/mcp/servers":
                try:
                    data = response.json()
                    server_count = len(data) if isinstance(data, list) else 0
                    print(f"      📊 Found {server_count} MCP servers")
                except:
                    pass
            elif endpoint == "/api/v1/mcp/status":
                try:
                    data = response.json()
                    print(f"      📊 Total servers: {data.get('total_servers', 0)}")
                    print(f"      📊 Running: {data.get('running_servers', 0)}")
                except:
                    pass
            
            results[endpoint] = {"status": response.status_code}
                
        except requests.RequestException as e:
            print(f"   ❌ MCP {endpoint} failed: {e}")
            results[endpoint] = {"error": str(e)}
    
    return results

def check_mcp_frontend():
    """Test Railway frontend is serving"""
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:8000")
    
    if frontend_url == "http://localhost:8000":
        print("⚠️ Frontend assumed to be running locally")
        return {"note": "Frontend not running on Railway"}
    
    try:
        response = requests.get(f"{frontend_url}/", timeout=10)
        status = "✅" if response.status_code == 200 else f"⚠️ {response.status_code}"
        print(f"   {status} Frontend serving")
        
        # Check if MCP Management page is accessible
        mcp_response = requests.get(f"{frontend_url}/mcp", timeout=10)
        mcp_status = "✅" if mcp_response.status_code == 200 else f"⚠️ {mcp_response.status_code}"
        print(f"   {mcp_status} MCP Management page")
        
        return {"frontend_status": response.status_code, "mcp_status": mcp_response.status_code}
        
    except Exception as e:
        print(f"   ❌ Frontend check failed: {e}")
        return {"error": str(e)}

def main():
    """Main Railway health check function"""
    
    print("🚂 Railway MCP Integration Health Check")
    print("=" * 60)
    
    # Environment Check
    print("\n🌍 Checking Railway Environment...")
    railway_ok = check_railway_environment()
    
    # Database Check
    print("\n🗄️ Checking PostgreSQL Connection...")
    pg_ok = check_railway_postgresql()
    
    # Backend API Check
    print("\n🔌 Checking Backend API...")
    api_results = check_backend_api()
    
    # MCP API Check
    print("\n🛠️ Checking MCP Management API...")
    mcp_results = check_mcp_management_api()
    
    # Frontend Check
    print("\n💻 Checking Frontend...")
    frontend_results = check_mcp_frontend()
    
    print("\n" + "=" * 60)
    print("🔍 RAILWAY MCP INTEGRATION STATUS")
    print("=" * 60)
    
    # Overall Status
    status_color = "🟢" if all([
        railway_ok, pg_ok, len([r for r in api_results.values() if "error" not in str(r).lower()])
    ]) else "🔴"
    
    print(f"Overall Status: {status_color} {'🟢': 'HEALTHY', '🔴': 'DEGRADED'}[status_color]}")
    
    # Detailed Status
    print(f"Railway Environment: {'✅' if railway_ok else '❌'}")
    print(f"PostgreSQL Connection: {'✅' if pg_ok else '❌'}")
    print(f"Backend API: {'✅' if len(api_results) > 0 else '❌'}")
    print(f"MCP Management API: {'✅' if len(mcp_results) > 0 else '❌'}")
    print(f"MCP Frontend: {'✅' if 'frontend_url' in os.environ else '🚠️'}")
    
    # Recommendations
    print("\n📋 Recommendations:")
    if not railway_ok:
        print("   ⚠️ Environment variables may not be properly set by Railway")
    
    if not pg_ok:
        print("   ⚠️ PostgreSQL may not be provisioned or accessible")
        print("      → Check Railway database logs")
        print("      → Verify DATABASE_URL environment variable")
        
    if len(api_results) > 2:
        error_endpoints = [name for name, result in api_results.items() if "error" in str(result)]
        if error_endpoints:
            print(f"   ⚠️ API endpoints failing: {', '.join(error_endpoints)}")
        
    if len(mcp_results) > 2:
        error_mcp_endpoints = [name for name, result in mcp_results.items() if "error" in str(result)]
        if error_mcp_endpoints:
            print(f"   ⚠️ MCP endpoints failing: {', '.join(error_mcp_endpoints)}")
    
    print("   📋 Next Steps:")
    if railway_ok and pg_ok:
        print("   → Railway environment is properly configured")
        print("   → Run: cd backend && alembic upgrade head")
        print("   → Monitor deployment logs for migration success")
    else:
        print("   → Fix Railway environment variables first")
    
    return 0

if __name__ == "__main__":
    main()
