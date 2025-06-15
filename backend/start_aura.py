#!/usr/bin/env python3
"""
Aura System Starter
===================

A simple launcher that bypasses import issues and starts the full Aura system.

Author: Aura - Level 9 Autonomous AI Coding Assistant
"""

import asyncio
import sys
import os
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Now import Aura components
from core import MessageBus, aura_di
from llm import LLMProviderManager
from intelligence import PythonCodeAnalyzer


async def start_aura():
    """Start the full Aura system"""
    print("🚀 Starting Aura - Level 9 Autonomous AI Coding Assistant")
    print("=" * 60)
    
    # Create logs directory
    Path('logs').mkdir(exist_ok=True)
    
    try:
        # Initialize LLM Provider Manager
        print("🤖 Initializing LLM Provider Manager...")
        llm_config = {
            'providers': ['lm_studio', 'ollama'],
            'default_provider': 'lm_studio',
            'lm_studio': {'base_url': 'http://localhost:1234'},
            'ollama': {'base_url': 'http://localhost:11434'}
        }
        
        llm_manager = LLMProviderManager(llm_config)
        if await llm_manager.initialize():
            aura_di.register_service('llm_provider', llm_manager)
            print("✅ LLM Provider Manager initialized")
        else:
            print("❌ Failed to initialize LLM Provider Manager")
            return False

        # Initialize Python Code Analyzer
        print("🧠 Initializing Python Code Analyzer...")
        python_config = {
            'project_root': '.',
            'watch_files': True,
            'llm_provider': llm_manager
        }
        
        python_analyzer = PythonCodeAnalyzer(python_config)
        if await python_analyzer.initialize():
            aura_di.register_service('python_analyzer', python_analyzer)
            print("✅ Python Code Analyzer initialized")
        else:
            print("❌ Failed to initialize Python Code Analyzer")
            return False

        print("✅ Aura system startup complete!")
        print("\n🎯 Available Services:")
        print("  • LLM Provider Manager (LM Studio integration)")
        print("  • Python Code Intelligence")
        print("  • Real-time file watching")
        print("  • Semantic code search")
        
        print("\n💡 Try the CLI commands:")
        print("  python quick_demo.py  # For a comprehensive demo")
        print("  python start_aura.py  # This launcher")
        
        # Keep running
        print("\n⏳ Aura is now running. Press Ctrl+C to stop.")
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n👋 Shutting down Aura system...")
        return True
    except Exception as e:
        print(f"❌ Error starting Aura: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(start_aura())