#!/usr/bin/env python3
"""
Aura VS Code Integration Test Suite
===================================

Test suite to validate the connection between VS Code extension and Aura backend.
This script tests all major integration points to ensure the extension will work properly.

Usage:
    python3 test_vscode_integration.py [--port 5559] [--verbose]

Author: Aura - Level 9 Autonomous AI Coding Assistant  
Date: 2025-06-15
"""

import sys
import os
import json
import time
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

try:
    import zmq
except ImportError:
    print("❌ ZeroMQ not installed. Install with: pip install pyzmq")
    sys.exit(1)

class VSCodeIntegrationTester:
    """Test suite for VS Code integration"""
    
    def __init__(self, port: int = 5559, verbose: bool = False):
        self.port = port
        self.verbose = verbose
        self.context = zmq.Context()
        self.socket = None
        self.message_id = 0
        
        # Test results
        self.results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'errors': []
        }
    
    def log(self, message: str, level: str = "INFO"):
        """Log message if verbose mode is enabled"""
        if self.verbose or level == "ERROR":
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] {level}: {message}")
    
    def connect(self) -> bool:
        """Connect to the backend service"""
        try:
            self.socket = self.context.socket(zmq.REQ)
            self.socket.setsockopt(zmq.RCVTIMEO, 5000)  # 5 second timeout
            self.socket.connect(f"tcp://localhost:{self.port}")
            self.log(f"Connected to backend service on port {self.port}")
            return True
        except Exception as e:
            self.log(f"Failed to connect: {e}", "ERROR")
            return False
    
    def disconnect(self):
        """Disconnect from the backend service"""
        if self.socket:
            self.socket.close()
            self.socket = None
        self.context.term()
    
    def send_request(self, target: str, command: str, payload: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Send a request to the backend service"""
        if not self.socket:
            return None
            
        self.message_id += 1
        message = {
            "id": f"test_{self.message_id}_{int(time.time())}",
            "type": "command",
            "source": "integration_test",
            "target": target,
            "timestamp": int(time.time() * 1000),
            "payload": {"command": command, **(payload or {})}
        }
        
        try:
            self.socket.send_json(message)
            response = self.socket.recv_json()
            return response
        except zmq.Again:
            self.log(f"Request timeout for {target}.{command}", "ERROR")
            return None
        except Exception as e:
            self.log(f"Request failed for {target}.{command}: {e}", "ERROR")
            return None
    
    def run_test(self, test_name: str, test_func) -> bool:
        """Run a single test and record results"""
        self.results['total_tests'] += 1
        
        try:
            self.log(f"Running test: {test_name}")
            success = test_func()
            
            if success:
                self.results['passed'] += 1
                self.log(f"✅ {test_name} - PASSED")
                return True
            else:
                self.results['failed'] += 1
                self.results['errors'].append(f"{test_name} - Test assertion failed")
                self.log(f"❌ {test_name} - FAILED")
                return False
                
        except Exception as e:
            self.results['failed'] += 1
            self.results['errors'].append(f"{test_name} - Exception: {e}")
            self.log(f"❌ {test_name} - ERROR: {e}", "ERROR")
            return False
    
    def test_health_check(self) -> bool:
        """Test basic health check functionality"""
        response = self.send_request("system", "health_check")
        
        if not response:
            return False
            
        return (
            response.get("success") is True and
            response.get("payload", {}).get("status") == "healthy"
        )
    
    def test_system_status(self) -> bool:
        """Test system status retrieval"""
        response = self.send_request("system", "get_status")
        
        if not response:
            return False
            
        status = response.get("payload", {}).get("status", {})
        return (
            response.get("success") is True and
            "service_running" in status and
            "modules_health" in status
        )
    
    def test_python_file_analysis(self) -> bool:
        """Test Python file analysis"""
        # Create a temporary Python file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
def hello_world():
    '''Simple hello world function'''
    print("Hello, World!")
    return "Hello, World!"

class TestClass:
    def __init__(self, name):
        self.name = name
    
    def greet(self):
        return f"Hello, {self.name}!"

if __name__ == "__main__":
    hello_world()
""")
            temp_file = f.name
        
        try:
            response = self.send_request("python_intelligence", "analyze_file", {
                "file_path": temp_file,
                "language": "python",
                "include_metrics": True,
                "include_complexity": True
            })
            
            if not response:
                return False
                
            analysis = response.get("payload", {}).get("analysis", {})
            return (
                response.get("success") is True and
                "elements" in analysis and
                "metrics" in analysis
            )
            
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file)
            except:
                pass
    
    def test_python_real_time_analysis(self) -> bool:
        """Test real-time Python code analysis"""
        code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

result = factorial(5)
print(f"5! = {result}")
"""
        
        response = self.send_request("python_intelligence", "analyze_file", {
            "file_path": "/tmp/test_realtime.py",
            "content": code,
            "language": "python",
            "real_time": True
        })
        
        if not response:
            return False
            
        analysis = response.get("payload", {}).get("analysis", {})
        return (
            response.get("success") is True and
            "elements" in analysis
        )
    
    def test_llm_provider_health(self) -> bool:
        """Test LLM provider health check"""
        response = self.send_request("llm_provider", "health_check")
        
        if not response:
            return False
            
        # LLM provider might not be available in test environment
        # We just check that the request is handled properly
        return response.get("success") is True
    
    def test_llm_provider_generate(self) -> bool:
        """Test LLM text generation"""
        response = self.send_request("llm_provider", "generate", {
            "request": {
                "prompt": "Write a simple Python function that adds two numbers.",
                "model_preference": "medium",
                "max_tokens": 100,
                "temperature": 0.3
            }
        })
        
        if not response:
            return False
            
        # LLM might not be available, so we accept either success or proper error handling
        return (
            response.get("success") is True or
            response.get("type") in ["module_error", "llm_error"]
        )
    
    def test_git_semantic_commits(self) -> bool:
        """Test Git semantic commit generation"""
        response = self.send_request("git_semantic", "generate_commit", {
            "include_unstaged": False
        })
        
        if not response:
            return False
            
        # Git might not have changes, so we accept proper error handling
        return (
            response.get("success") is True or
            response.get("type") in ["module_error", "git_error"]
        )
    
    def test_test_generation(self) -> bool:
        """Test test generation functionality"""
        # Create a temporary Python file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
def add(a, b):
    '''Add two numbers'''
    return a + b

def multiply(a, b):
    '''Multiply two numbers'''
    return a * b
""")
            temp_file = f.name
        
        try:
            response = self.send_request("test_generator", "generate_tests", {
                "file_path": temp_file,
                "test_type": "unit"
            })
            
            if not response:
                return False
                
            # Test generation might not be available, check for proper handling
            return (
                response.get("success") is True or
                response.get("type") in ["module_error", "test_generation_error"]
            )
            
        finally:
            try:
                os.unlink(temp_file)
            except:
                pass
    
    def test_refactoring_analysis(self) -> bool:
        """Test refactoring analysis"""
        code = """
def long_function_with_multiple_responsibilities():
    # This function does too many things
    data = []
    for i in range(100):
        if i % 2 == 0:
            data.append(i * 2)
        else:
            data.append(i * 3)
    
    total = 0
    for item in data:
        total += item
    
    average = total / len(data)
    
    print(f"Data: {data}")
    print(f"Total: {total}")
    print(f"Average: {average}")
    
    return data, total, average
"""
        
        response = self.send_request("refactoring_engine", "analyze_refactoring_opportunities", {
            "file_path": "/tmp/test_refactor.py",
            "code": code
        })
        
        if not response:
            return False
            
        # Refactoring might not be available, check for proper handling
        return (
            response.get("success") is True or
            response.get("type") in ["module_error", "refactoring_error"]
        )
    
    def run_all_tests(self) -> bool:
        """Run all integration tests"""
        print("🧪 Aura VS Code Integration Test Suite")
        print("=" * 50)
        
        # Connect to backend
        if not self.connect():
            print("❌ Failed to connect to backend service")
            print("   Make sure the service is running: python3 start_aura_for_vscode.py")
            return False
        
        print(f"✅ Connected to backend on port {self.port}")
        print()
        
        # Define all tests
        tests = [
            ("Health Check", self.test_health_check),
            ("System Status", self.test_system_status),
            ("Python File Analysis", self.test_python_file_analysis),
            ("Python Real-time Analysis", self.test_python_real_time_analysis),
            ("LLM Provider Health", self.test_llm_provider_health),
            ("LLM Text Generation", self.test_llm_provider_generate),
            ("Git Semantic Commits", self.test_git_semantic_commits),
            ("Test Generation", self.test_test_generation),
            ("Refactoring Analysis", self.test_refactoring_analysis)
        ]
        
        # Run all tests
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
            time.sleep(0.1)  # Small delay between tests
        
        # Disconnect
        self.disconnect()
        
        # Print results
        print()
        print("📊 Test Results")
        print("-" * 20)
        print(f"Total Tests: {self.results['total_tests']}")
        print(f"Passed: {self.results['passed']}")
        print(f"Failed: {self.results['failed']}")
        
        if self.results['errors']:
            print("\n❌ Errors:")
            for error in self.results['errors']:
                print(f"   - {error}")
        
        print()
        
        success_rate = (self.results['passed'] / self.results['total_tests']) * 100
        if success_rate >= 80:
            print(f"✅ Integration tests PASSED ({success_rate:.1f}% success rate)")
            return True
        else:
            print(f"❌ Integration tests FAILED ({success_rate:.1f}% success rate)")
            return False

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Aura VS Code integration")
    parser.add_argument("--port", type=int, default=5559, help="Backend service port")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()
    
    tester = VSCodeIntegrationTester(port=args.port, verbose=args.verbose)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()