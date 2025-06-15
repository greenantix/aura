#!/usr/bin/env python3
"""
Simple Aura CLI
===============

A working CLI that demonstrates Aura's capabilities without the complex import structure.

Author: Aura - Level 9 Autonomous AI Coding Assistant
"""

import asyncio
import sys
import json
from pathlib import Path
import click
from quick_demo import AuraDemo


@click.group()
def cli():
    """Aura - Level 9 Autonomous AI Coding Assistant CLI"""
    pass


@cli.command()
def demo():
    """Run the full Aura demonstration"""
    asyncio.run(run_demo())


async def run_demo():
    """Run the demo"""
    demo = AuraDemo()
    demo.print_banner()
    
    # Check LLM connection
    llm_available = await demo.check_llm_connection()
    
    print("\n🚀 Starting Aura Demo...")
    print("=" * 60)
    
    # Scan codebase
    print("\n📊 Scanning codebase...")
    analyses = demo.scan_codebase()
    demo.display_codebase_summary(analyses)
    
    if llm_available:
        print("\n🤖 Asking Aura about the codebase...")
        question = "What are the key capabilities of this Aura codebase and how would you recommend getting it running quickly?"
        response = await demo.ask_aura(question)
        if response:
            print(f"\n🤖 Aura's Response:")
            print("-" * 40)
            print(response)


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
def analyze(file_path):
    """Analyze a Python file"""
    if not file_path.endswith('.py'):
        print("❌ Only Python files are supported")
        return
    
    demo = AuraDemo()
    analysis = demo.analyze_file(file_path)
    demo.display_analysis(analysis)


@cli.command()
@click.argument('query')
@click.option('--limit', '-l', default=5, help='Number of results to return')
def search(query, limit):
    """Search for similar code"""
    demo = AuraDemo()
    
    # First scan to build index
    print("🔍 Building search index...")
    demo.scan_codebase()
    
    # Search
    results = demo.find_similar_code(query, limit)
    demo.display_search_results(results)


@cli.command()
@click.argument('question')
async def ask(question):
    """Ask Aura a question"""
    demo = AuraDemo()
    
    # Check LLM
    if not await demo.check_llm_connection():
        print("❌ LM Studio not available")
        return
    
    response = await demo.ask_aura(question)
    if response:
        print(f"\n🤖 Aura's Response:")
        print("-" * 40)
        print(response)
    else:
        print("❌ Could not get response from Aura")


@cli.command()
def status():
    """Show Aura system status"""
    async def check_status():
        demo = AuraDemo()
        demo.print_banner()
        
        # Check LLM
        llm_available = await demo.check_llm_connection()
        
        print("\n📊 System Status:")
        print("=" * 40)
        print(f"🤖 LM Studio: {'✅ Available' if llm_available else '❌ Not Available'}")
        print(f"🐍 Python: ✅ {sys.version.split()[0]}")
        print(f"📁 Working Directory: {Path.cwd()}")
        print(f"📝 Log Directory: {'✅ Exists' if Path('logs').exists() else '❌ Missing'}")
        
        # Quick codebase scan
        print(f"\n📊 Quick Codebase Scan:")
        python_files = list(Path('.').rglob("*.py"))
        print(f"🐍 Python files: {len(python_files)}")
        
    asyncio.run(check_status())


@cli.command()
def version():
    """Show version information"""
    print("\n" + "=" * 50)
    print("🤖 Aura - Level 9 Autonomous AI Coding Assistant")
    print("=" * 50)
    print(f"Version: 1.0.0")
    print(f"Phase: Foundation and Core Intelligence")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Author: Aura - Level 9 Autonomous AI Coding Assistant")
    print("=" * 50)


# Async wrapper for ask command
def ask_wrapper(question):
    """Wrapper for async ask command"""
    async def run_ask():
        demo = AuraDemo()
        
        # Check LLM
        if not await demo.check_llm_connection():
            print("❌ LM Studio not available")
            return
        
        response = await demo.ask_aura(question)
        if response:
            print(f"\n🤖 Aura's Response:")
            print("-" * 40)
            print(response)
        else:
            print("❌ Could not get response from Aura")
    
    asyncio.run(run_ask())


# Replace the async command with wrapper
ask.callback = ask_wrapper


if __name__ == '__main__':
    cli()