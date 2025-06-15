#!/usr/bin/env python3
"""
Aura Integration Test
====================

Tests the basic functionality of the Aura system without requiring 
external dependencies like LM Studio.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

async def test_llm_integration():
    """Test LLM provider integration"""
    print("Testing LLM Integration...")
    try:
        # Import basic classes first
        from llm.providers import LLMRequest, ModelCapability
        print("✅ LLM Provider classes imported successfully")
        
        # Test request creation
        request = LLMRequest(
            prompt="Test prompt",
            model_preference=ModelCapability.CODING,
            max_tokens=100
        )
        print("✅ LLM Request created successfully")
        
        # Test model capability enum
        capabilities = [cap.value for cap in ModelCapability]
        print(f"✅ Available model capabilities: {capabilities}")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM Integration test failed: {e}")
        return False

async def test_security_integration():
    """Test security module integration"""
    print("\nTesting Security Integration...")
    try:
        from security import SecurityManager, AuthenticationError
        
        # Create security manager
        security_manager = SecurityManager()
        print("✅ Security Manager created successfully")
        
        # Test authentication
        try:
            # This should fail with invalid credentials
            security_manager.create_service_token('invalid', 'invalid')
            print("❌ Authentication should have failed")
            return False
        except AuthenticationError:
            print("✅ Authentication properly rejects invalid credentials")
        
        # Test encryption
        test_data = "sensitive information"
        encrypted = security_manager.encrypt_sensitive_data(test_data)
        decrypted = security_manager.decrypt_sensitive_data(encrypted)
        
        if decrypted == test_data:
            print("✅ Encryption/decryption working correctly")
        else:
            print("❌ Encryption/decryption failed")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Security Integration test failed: {e}")
        return False

async def test_git_integration():
    """Test git semantic commits integration"""
    print("\nTesting Git Integration...")
    try:
        # Import and test basic git classes
        from git.semantic_commits import GitAnalyzer, CommitType
        print("✅ Git classes imported successfully")
        
        # Test git analyzer creation
        analyzer = GitAnalyzer('.')
        is_repo = analyzer.is_git_repo()
        print(f"✅ Git repository check: {is_repo}")
        
        # Test commit types
        commit_types = [ct.value for ct in CommitType]
        print(f"✅ Available commit types: {commit_types}")
        
        return True
        
    except Exception as e:
        print(f"❌ Git Integration test failed: {e}")
        return False

async def test_code_generation():
    """Test code generation module"""
    print("\nTesting Code Generation...")
    try:
        # Import basic classes
        from generation.code_generator import CodeGenerationRequest
        print("✅ Code Generation classes imported successfully")
        
        # Test request creation
        request = CodeGenerationRequest(
            description="test function",
            language="python",
            target="function"
        )
        print("✅ Code Generation Request created successfully")
        print(f"   Description: {request.description}")
        print(f"   Language: {request.language}")
        print(f"   Target: {request.target}")
        
        return True
        
    except Exception as e:
        print(f"❌ Code Generation test failed: {e}")
        return False

def test_vscode_extension():
    """Test VSCode extension compilation"""
    print("\nTesting VSCode Extension...")
    try:
        extension_path = Path(__file__).parent / "vscode-extension"
        
        # Check if extension files exist
        required_files = [
            "package.json",
            "src/extension.ts", 
            "src/connection.ts",
            "out/extension.js"
        ]
        
        for file in required_files:
            file_path = extension_path / file
            if file_path.exists():
                print(f"✅ {file} exists")
            else:
                print(f"❌ {file} missing")
                return False
        
        print("✅ VSCode extension files are present")
        return True
        
    except Exception as e:
        print(f"❌ VSCode Extension test failed: {e}")
        return False

async def main():
    """Run all integration tests"""
    print("🚀 Starting Aura Integration Tests")
    print("=" * 50)
    
    tests = [
        ("LLM Integration", test_llm_integration),
        ("Security Integration", test_security_integration), 
        ("Git Integration", test_git_integration),
        ("Code Generation", test_code_generation),
        ("VSCode Extension", lambda: test_vscode_extension())
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("🏁 Integration Test Results:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed!")
        return True
    else:
        print("⚠️  Some integration tests failed")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"💥 Test runner failed: {e}")
        sys.exit(1)