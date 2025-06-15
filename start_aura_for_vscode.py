#!/usr/bin/env python3
"""
Aura VS Code Integration Launcher
=================================

Simple launcher script to start the Aura backend service for VS Code integration.
This script handles dependency checking, environment setup, and service startup.

Usage:
    python3 start_aura_for_vscode.py [--port 5559] [--debug]

Author: Aura - Level 9 Autonomous AI Coding Assistant
Date: 2025-06-15
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    missing_deps = []
    
    try:
        import zmq
    except ImportError:
        missing_deps.append("pyzmq")
    
    if missing_deps:
        print("❌ Missing required dependencies:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\nInstall with:")
        print(f"   pip install {' '.join(missing_deps)}")
        return False
    
    return True

def check_backend_modules():
    """Check if Aura backend modules are available"""
    backend_dir = Path(__file__).parent / "backend"
    if not backend_dir.exists():
        print(f"❌ Backend directory not found: {backend_dir}")
        return False
    
    # Check key module files
    key_modules = [
        "intelligence/python_analyzer.py",
        "llm/providers.py", 
        "git/semantic_commits.py",
        "generation/test_generator.py",
        "generation/refactoring_engine.py"
    ]
    
    missing_modules = []
    for module in key_modules:
        module_path = backend_dir / module
        if not module_path.exists():
            missing_modules.append(module)
    
    if missing_modules:
        print("⚠️  Some backend modules are missing (features may be limited):")
        for module in missing_modules:
            print(f"   - {module}")
        print()
    
    return True

def start_backend_service(port: int = 5559, debug: bool = False):
    """Start the Aura backend service"""
    backend_dir = Path(__file__).parent / "backend"
    service_script = backend_dir / "vscode_backend_service.py"
    
    if not service_script.exists():
        print(f"❌ Backend service script not found: {service_script}")
        return False
    
    print("🚀 Starting Aura VS Code Backend Service...")
    print(f"   Port: {port}")
    print(f"   Debug: {debug}")
    print(f"   Backend: {backend_dir}")
    print()
    
    # Build command
    cmd = [sys.executable, str(service_script), "--port", str(port)]
    if debug:
        cmd.append("--debug")
    
    try:
        # Change to backend directory
        os.chdir(backend_dir)
        
        # Start the service
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        print("\n⏹️  Service stopped by user")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Service failed to start: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    return True

def main():
    """Main entry point"""
    print("🤖 Aura VS Code Integration Launcher")
    print("=" * 40)
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="Start Aura backend service for VS Code")
    parser.add_argument("--port", type=int, default=5559, help="ZeroMQ port (default: 5559)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--check-only", action="store_true", help="Only check dependencies and exit")
    args = parser.parse_args()
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    print("✅ Dependencies OK")
    
    # Check backend modules
    print("\n🔍 Checking backend modules...")
    if not check_backend_modules():
        sys.exit(1)
    print("✅ Backend modules OK")
    
    if args.check_only:
        print("\n✅ All checks passed! Ready to start service.")
        return
    
    # Start service
    print("\n🚀 Starting service...")
    success = start_backend_service(args.port, args.debug)
    
    if success:
        print("\n✅ Service started successfully!")
    else:
        print("\n❌ Service failed to start!")
        sys.exit(1)

if __name__ == "__main__":
    main()