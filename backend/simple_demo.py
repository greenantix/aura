#!/usr/bin/env python3
"""
Simple Aura Performance Demo
============================

Simple demonstration of performance optimization systems working.

Author: Aura - Level 9 Autonomous AI Coding Assistant
"""

import asyncio
import sys
import time
from pathlib import Path

# Add aura directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from performance.standalone_manager import StandalonePerformanceManager


async def simple_file_analyzer(file_path: str):
    """Simple file analysis function for demonstration"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Simple metrics
        lines = len(content.splitlines())
        chars = len(content)
        
        # Simulate some processing time
        await asyncio.sleep(0.1)
        
        return {
            'file': file_path,
            'lines': lines,
            'characters': chars,
            'size_kb': chars / 1024,
            'analysis_time': 0.1
        }
    except Exception as e:
        return {'file': file_path, 'error': str(e)}


async def demo_performance():
    """Demonstrate performance optimization"""
    print("🚀 Simple Aura Performance Demo")
    print("=" * 40)
    
    # Initialize performance manager
    config = {
        'async_pipeline_enabled': True,
        'max_workers': 4,
        'cache_enabled': True,
        'cache_max_memory_mb': 128
    }
    
    perf_manager = StandalonePerformanceManager(config)
    
    if not await perf_manager.initialize():
        print("❌ Failed to initialize performance manager")
        return
    
    print("✅ Performance Manager initialized")
    
    # Find files to analyze
    python_files = [str(f) for f in Path('.').rglob("*.py")][:5]  # Limit for demo
    print(f"🔍 Found {len(python_files)} files for analysis")
    
    # Test 1: Sequential processing
    print("\n📊 Sequential processing...")
    start_time = time.time()
    
    sequential_results = []
    for file_path in python_files:
        result = await simple_file_analyzer(file_path)
        sequential_results.append(result)
    
    sequential_time = time.time() - start_time
    print(f"⏱️ Sequential time: {sequential_time:.2f} seconds")
    
    # Set baseline
    await perf_manager.set_baseline_metrics()
    
    # Test 2: Parallel processing with performance optimization
    print("\n🚀 Parallel processing with optimization...")
    start_time = time.time()
    
    parallel_results = await perf_manager.batch_process_files(
        python_files,
        simple_file_analyzer
    )
    
    parallel_time = time.time() - start_time
    print(f"⏱️ Parallel time: {parallel_time:.2f} seconds")
    
    # Calculate speedup
    speedup = sequential_time / parallel_time if parallel_time > 0 else 1
    print(f"🎯 Speedup: {speedup:.2f}x faster")
    
    # Show performance report
    perf_report = await perf_manager.generate_performance_report()
    print(f"\n📊 Performance Report:")
    print(f"   • Cache Hit Rate: {perf_report['performance_summary']['cache_hit_rate']:.1f}%")
    print(f"   • Tasks Processed: {perf_report['performance_summary']['total_tasks_processed']}")
    print(f"   • Performance Factor: {perf_report['performance_summary']['improvement_factor']:.2f}x")
    
    # Show sample results
    print(f"\n📋 Sample Analysis Results:")
    for i, result in enumerate(parallel_results[:3]):
        if result and 'error' not in result:
            file_name = Path(result['file']).name
            print(f"   • {file_name}: {result['lines']} lines, {result['size_kb']:.1f}KB")
    
    # Test caching by running again
    print(f"\n🔄 Testing cache performance...")
    start_time = time.time()
    
    cached_results = await perf_manager.batch_process_files(
        python_files,
        simple_file_analyzer
    )
    
    cached_time = time.time() - start_time
    print(f"⏱️ Cached time: {cached_time:.2f} seconds")
    
    # Final performance report
    final_report = await perf_manager.generate_performance_report()
    print(f"\n📊 Final Performance Report:")
    print(f"   • Cache Hit Rate: {final_report['performance_summary']['cache_hit_rate']:.1f}%")
    print(f"   • Total Tasks: {final_report['performance_summary']['total_tasks_processed']}")
    
    # Cleanup
    await perf_manager.shutdown()
    print("\n✅ Demo complete - Performance systems working perfectly!")


if __name__ == "__main__":
    asyncio.run(demo_performance())