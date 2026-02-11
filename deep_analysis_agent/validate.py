#!/usr/bin/env python3
"""
Quick validation script for Deep Analysis Agent

This script validates the module structure without requiring AWS credentials
or external dependencies.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported."""
    print("=" * 60)
    print("Testing Deep Analysis Agent Module Structure")
    print("=" * 60)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Core modules
    print("\n[1] Testing core module imports...")
    try:
        from deep_analysis_agent import memory
        print("    ✓ memory module")
        tests_passed += 1
    except Exception as e:
        print(f"    ✗ memory module: {e}")
        tests_failed += 1
    
    # Test 2: Node modules
    print("\n[2] Testing node modules...")
    node_modules = [
        "load_incident",
        "fetch_related_incidents",
        "correlate_iocs",
        "threat_reasoning",
        "remediation_advice"
    ]
    
    for node_name in node_modules:
        try:
            module = __import__(f'deep_analysis_agent.nodes.{node_name}', fromlist=[node_name])
            print(f"    ✓ {node_name}")
            tests_passed += 1
        except Exception as e:
            print(f"    ✗ {node_name}: {e}")
            tests_failed += 1
    
    # Test 3: Graph module
    print("\n[3] Testing graph module...")
    try:
        from deep_analysis_agent import graph
        print("    ✓ graph module")
        
        # Check for key classes/functions
        if hasattr(graph, 'DeepAnalysisGraph'):
            print("    ✓ DeepAnalysisGraph class found")
            tests_passed += 1
        if hasattr(graph, 'create_analysis_graph'):
            print("    ✓ create_analysis_graph function found")
            tests_passed += 1
    except Exception as e:
        print(f"    ✗ graph module: {e}")
        tests_failed += 1
    
    # Test 4: Memory state management
    print("\n[4] Testing memory state management...")
    try:
        from deep_analysis_agent.memory import AgentMemory, InMemoryTraceCollector
        
        # Create a test memory instance
        mem = AgentMemory(request_id="test_123")
        mem.add_trace_entry("test_node", "success", 100.0)
        
        print("    ✓ AgentMemory class instantiated")
        print("    ✓ Trace entry added successfully")
        
        # Test trace collector
        collector = InMemoryTraceCollector()
        collector.record_trace("test_req", {"node": "test", "status": "ok"})
        traces = collector.get_traces("test_req")
        
        if len(traces) == 1:
            print("    ✓ InMemoryTraceCollector working")
            tests_passed += 1
        
    except Exception as e:
        print(f"    ✗ memory tests: {e}")
        tests_failed += 1
    
    # Test 5: File structure
    print("\n[5] Checking file structure...")
    required_files = [
        "deep_analysis_agent/__init__.py",
        "deep_analysis_agent/api.py",
        "deep_analysis_agent/bedrock_client.py",
        "deep_analysis_agent/dynamodb_client.py",
        "deep_analysis_agent/graph.py",
        "deep_analysis_agent/memory.py",
        "deep_analysis_agent/requirements.txt",
        "deep_analysis_agent/Dockerfile",
        "deep_analysis_agent/README.md",
        "deep_analysis_agent/nodes/__init__.py",
    ]
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    for file_path in required_files:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            print(f"    ✓ {file_path}")
            tests_passed += 1
        else:
            print(f"    ✗ {file_path} not found")
            tests_failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Tests Passed: {tests_passed}")
    print(f"Tests Failed: {tests_failed}")
    print("=" * 60)
    
    if tests_failed == 0:
        print("\n✓ All validation tests PASSED!")
        print("The Deep Analysis Agent module is properly structured.")
        return 0
    else:
        print(f"\n✗ {tests_failed} validation test(s) FAILED")
        return 1


def show_module_info():
    """Display module information."""
    print("\n" + "=" * 60)
    print("Deep Analysis Agent - Module Information")
    print("=" * 60)
    
    try:
        from deep_analysis_agent import __version__
        print(f"Version: {__version__}")
    except:
        print("Version: 1.0.0")
    
    print("\nComponents:")
    print("  • LangGraph Workflow: 5 sequential nodes")
    print("  • FastAPI Service: REST API with /deep-analysis endpoint")
    print("  • AWS Integrations: DynamoDB + Bedrock")
    print("  • Observability: Logging, metrics, execution traces")
    
    print("\nDeployment Options:")
    print("  • Docker container (Dockerfile provided)")
    print("  • AWS Lambda with Function URL")
    print("  • ECS/Fargate service")
    
    print("\nFor more information, see: deep_analysis_agent/README.md")


if __name__ == "__main__":
    exit_code = test_imports()
    show_module_info()
    sys.exit(exit_code)
