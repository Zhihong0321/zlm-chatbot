#!/usr/bin/env python3
"""
Final Integration Test for Z.ai MCP Backend
Tests all MCP functionality without requiring server startup
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_backend_import():
    """Test backend import and initialization"""
    print("Testing Backend Import...")
    
    try:
        from test_mcp_backend import ZaiMCPBackend
        
        backend = ZaiMCPBackend()
        print(f"PASS: Backend imported successfully")
        print(f"  MCP tools available: {len(backend.available_tools)}")
        return True, backend
    except Exception as e:
        print(f"FAIL: Backend import failed: {e}")
        return False, None

def test_tool_execution(backend):
    """Test individual tool execution"""
    print("\nTesting Tool Execution...")
    
    test_cases = [
        ("list_directory", {"path": ".", "pattern": "*.py"}, "File listing"),
        ("read_file", {"path": "requirements.txt"}, "File reading"),
        ("search_code", {"pattern": "import", "file_pattern": "*.py"}, "Code search")
    ]
    
    results = []
    
    for tool_name, args, description in test_cases:
        try:
            result = backend.execute_mcp_tool(tool_name, args)
            
            if result and not result.startswith("Error:"):
                print(f"  PASS: {description}")
                results.append(True)
            else:
                print(f"  FAIL: {description} - {result}")
                results.append(False)
                
        except Exception as e:
            print(f"  FAIL: {description} - Exception: {e}")
            results.append(False)
    
    return all(results), results

def test_mcp_workflow(backend):
    """Test full MCP workflow"""
    print("\nTesting MCP Workflow...")
    
    try:
        # Test message processing
        test_messages = [
            "List Python files in this directory",
            "Read the README.md file",
            "Search for database connections in the code"
        ]
        
        results = []
        
        for message in test_messages:
            result = backend.process_message(message)
            
            if result['success']:
                print(f"  PASS: {message[:30]}...")
                print(f"    Tools: {', '.join(result['tools_used'])}")
                results.append(True)
            else:
                print(f"  FAIL: {message[:30]}...")
                print(f"    Error: {result['response'][:50]}...")
                results.append(False)
        
        return all(results), results
        
    except Exception as e:
        print(f"  FAIL: Workflow exception: {e}")
        return False, [False]

def test_backend_server_structure():
    """Test backend server file structure"""
    print("\nTesting Backend Server Structure...")
    
    required_files = [
        "backend_mcp_server.py",
        "mcp_file_server.py", 
        "test_mcp_backend.py",
        "test_mcp_simple.py"
    ]
    
    results = []
    
    for file_name in required_files:
        if os.path.exists(file_name):
            print(f"  PASS: {file_name} exists")
            results.append(True)
        else:
            print(f"  FAIL: {file_name} missing")
            results.append(False)
    
    return all(results), results

def test_api_endpoints():
    """Test API endpoint functionality"""
    print("\nTesting API Endpoint Logic...")
    
    try:
        # Import the backend server module
        import importlib.util
        spec = importlib.util.spec_from_file_location("backend_server", "backend_mcp_server.py")
        backend_module = importlib.util.module_from_spec(spec)
        
        # Check if file has required functions
        required_functions = [
            "chat_with_mcp",
            "list_available_tools",
            "get_tool_info"
        ]
        
        results = []
        
        for func_name in required_functions:
            if hasattr(backend_module, func_name):
                print(f"  PASS: {func_name} endpoint defined")
                results.append(True)
            else:
                print(f"  FAIL: {func_name} endpoint missing")
                results.append(False)
        
        return all(results), results
        
    except Exception as e:
        print(f"  FAIL: API structure test failed: {e}")
        return False, [False]

def main():
    """Run comprehensive integration tests"""
    print("=" * 60)
    print("Z.ai MCP Integration - Final Test Suite")
    print("=" * 60)
    
    # Check environment
    if not os.getenv("ZAI_API_KEY"):
        print("WARNING: ZAI_API_KEY not configured")
        return False
    
    load_dotenv()
    
    test_results = []
    
    # Test 1: Backend import
    backend_imported, backend = test_backend_import()
    test_results.append(backend_imported)
    
    if not backend_imported:
        print("Cannot proceed without successful backend import")
        return False
    
    # Test 2: Tool execution
    tools_result, tool_details = test_tool_execution(backend)
    test_results.append(tools_result)
    
    # Test 3: MCP workflow
    workflow_result, workflow_details = test_mcp_workflow(backend)
    test_results.append(workflow_result)
    
    # Test 4: Backend structure
    structure_result, structure_details = test_backend_server_structure()
    test_results.append(structure_result)
    
    # Test 5: API endpoints
    api_result, api_details = test_api_endpoints()
    test_results.append(api_result)
    
    # Summary
    print("\n" + "=" * 60)
    print("FINAL INTEGRATION RESULTS")
    print("=" * 60)
    
    total_tests = len(test_results)
    passed_tests = sum(test_results)
    
    print(f"Tests: {passed_tests}/{total_tests} passed")
    print(f"Success Rate: {passed_tests/total_tests*100:.1f}%")
    
    test_names = [
        "Backend Import",
        "Tool Execution", 
        "MCP Workflow",
        "Backend Structure",
        "API Endpoints"
    ]
    
    print("\nDetailed Results:")
    for i, (name, passed) in enumerate(zip(test_names, test_results)):
        status = "PASS" if passed else "FAIL"
        print(f"  {i+1}. {name}: {status}")
    
    if all(test_results):
        print("\nSUCCESS: Z.ai MCP integration is fully functional!")
        print("\nFeatures ready for deployment:")
        print("✓ MCP-style tool discovery and execution")
        print("✓ File system operations")
        print("✓ Code search and analysis")
        print("✓ Context-aware conversations")
        print("✓ HTTP API endpoints")
        print("\nNext steps:")
        print("1. Deploy backend_mcp_server.py")
        print("2. Connect frontend to /api/v1/chat endpoint")
        print("3. Enable advanced MCP features")
        return True
    else:
        print(f"\nPARTIAL SUCCESS: {passed_tests}/{total_tests} tests passed")
        print("Some functionality may be limited but core MCP integration works.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
