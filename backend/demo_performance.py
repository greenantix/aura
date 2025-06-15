#!/usr/bin/env python3
"""
Aura Performance Demonstration
==============================

Demonstrates real performance optimization on actual code analysis.

Author: Aura - Level 9 Autonomous AI Coding Assistant
"""

import asyncio
import sys
import time
from pathlib import Path

# Add aura directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from performance.standalone_manager import StandalonePerformanceManager
from performance.quality_analyzer import CodeQualityAnalyzer


async def demo_performance_optimization():
    """Demonstrate performance optimization on real code analysis"""
    print("🚀 Aura Performance Optimization Demo")
    print("=" * 50)
    
    # Initialize performance manager
    config = {
        'async_pipeline_enabled': True,
        'max_workers': 4,
        'cache_enabled': True,
        'cache_max_memory_mb': 256
    }
    
    perf_manager = StandalonePerformanceManager(config)
    
    if not await perf_manager.initialize():
        print("❌ Failed to initialize performance manager")
        return
    
    print("✅ Performance Manager initialized")
    
    # Initialize quality analyzer
    analyzer_config = {
        'enable_complexity_analysis': True,
        'enable_maintainability_scoring': True,
        'enable_quality_suggestions': True,
        'target_quality_score': 80.0
    }
    quality_analyzer = CodeQualityAnalyzer(analyzer_config)
    print("✅ Quality Analyzer initialized")
    
    # Find Python files to analyze
    python_files = list(Path('.').rglob("*.py"))[:10]  # Limit to 10 files for demo
    print(f"🔍 Found {len(python_files)} Python files for analysis")
    
    # Benchmark without performance optimization
    print("\n📊 Benchmarking WITHOUT performance optimization...")
    start_time = time.time()
    
    baseline_results = []
    for file_path in python_files:
        try:
            result = quality_analyzer.analyze_file(str(file_path))
            baseline_results.append(result)
        except Exception as e:
            print(f"⚠️ Error analyzing {file_path}: {e}")
    
    baseline_time = time.time() - start_time
    print(f"⏱️ Baseline analysis time: {baseline_time:.2f} seconds")
    print(f"📈 Files analyzed: {len(baseline_results)}")
    
    # Set baseline metrics
    await perf_manager.set_baseline_metrics()
    
    # Benchmark WITH performance optimization
    print("\n🚀 Benchmarking WITH performance optimization...")
    start_time = time.time()
    
    # Use batch processing with performance optimization
    optimized_results = await perf_manager.batch_process_files(
        [str(f) for f in python_files],
        quality_analyzer.analyze_file
    )
    
    optimized_time = time.time() - start_time
    print(f"⏱️ Optimized analysis time: {optimized_time:.2f} seconds")
    print(f"📈 Files analyzed: {len([r for r in optimized_results if r])}")
    
    # Calculate improvement
    if baseline_time > 0:
        speedup = baseline_time / optimized_time if optimized_time > 0 else 1
        print(f"🎯 Performance improvement: {speedup:.2f}x faster")
    
    # Show performance report
    perf_report = await perf_manager.generate_performance_report()
    print(f"\n📊 Performance Report:")
    print(f"   • Cache Hit Rate: {perf_report['performance_summary']['cache_hit_rate']:.1f}%")
    print(f"   • Total Tasks Processed: {perf_report['performance_summary']['total_tasks_processed']}")
    print(f"   • Performance Factor: {perf_report['performance_summary']['improvement_factor']:.2f}x")
    
    # Show quality metrics from one analysis
    if optimized_results and optimized_results[0]:
        sample_result = optimized_results[0]
        if hasattr(sample_result, 'overall_score'):
            print(f"\n🎯 Sample Quality Metrics:")
            print(f"   • Overall Score: {sample_result.overall_score:.1f}/100")
            print(f"   • Quality Level: {sample_result.quality_level.value}")
    
    # Show recommendations
    if perf_report.get('recommendations'):
        print(f"\n💡 Performance Recommendations:")
        for rec in perf_report['recommendations']:
            print(f"   • {rec}")
    
    # Cleanup
    await perf_manager.shutdown()
    print("\n✅ Demo complete - Performance optimization systems working!")


if __name__ == "__main__":
    asyncio.run(demo_performance_optimization())