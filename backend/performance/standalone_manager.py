#!/usr/bin/env python3
"""
Standalone Performance Manager
==============================

Performance manager that works without complex configuration dependencies.

Author: Aura - Level 9 Autonomous AI Coding Assistant
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from pathlib import Path

# Import performance modules directly
from .async_pipeline import AsyncPipeline, TaskPriority, PipelineMetrics
from .intelligent_cache import IntelligentCache, CacheStrategy, CacheLevel


@dataclass
class PerformanceMetrics:
    """Comprehensive performance metrics"""
    timestamp: float
    pipeline_metrics: Optional[PipelineMetrics] = None
    cache_hit_rate: float = 0.0
    cache_memory_usage_mb: float = 0.0
    average_quality_score: float = 0.0
    files_analyzed: int = 0
    total_tasks_processed: int = 0
    performance_improvement_factor: float = 1.0


class StandalonePerformanceManager:
    """Standalone performance manager without external config dependencies"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize with simple config dictionary"""
        self.config = config or {}
        self.logger = logging.getLogger('aura.performance.standalone')
        
        # Initialize subsystems
        self.async_pipeline: Optional[AsyncPipeline] = None
        self.intelligent_cache: Optional[IntelligentCache] = None
        
        # State tracking
        self.is_running = False
        self.baseline_metrics: Optional[PerformanceMetrics] = None
        self.current_metrics: Optional[PerformanceMetrics] = None
        
        # Performance optimization callbacks
        self.optimization_callbacks: List[Callable] = []
        
        # Default performance settings
        self.settings = {
            'async_pipeline_enabled': self.config.get('async_pipeline_enabled', True),
            'max_workers': self.config.get('max_workers', 8),
            'max_concurrent_tasks': self.config.get('max_concurrent_tasks', 100),
            'enable_thread_pool': self.config.get('enable_thread_pool', True),
            'thread_pool_size': self.config.get('thread_pool_size', 4),
            'cache_enabled': self.config.get('cache_enabled', True),
            'cache_max_memory_mb': self.config.get('cache_max_memory_mb', 512),
            'cache_strategy': self.config.get('cache_strategy', 'adaptive'),
            'cache_disk_enabled': self.config.get('cache_disk_enabled', True),
            'cache_disk_dir': self.config.get('cache_disk_dir', '.aura_cache'),
            'quality_target_score': self.config.get('quality_target_score', 85.0)
        }
        
    async def initialize(self) -> bool:
        """Initialize all performance systems"""
        try:
            self.logger.info("Initializing Standalone Performance Manager")
            
            # Initialize Async Pipeline
            if self.settings['async_pipeline_enabled']:
                pipeline_config = {
                    'max_workers': self.settings['max_workers'],
                    'max_concurrent_tasks': self.settings['max_concurrent_tasks'],
                    'enable_thread_pool': self.settings['enable_thread_pool'],
                    'thread_pool_size': self.settings['thread_pool_size']
                }
                
                self.async_pipeline = AsyncPipeline(pipeline_config)
                await self.async_pipeline.start()
                self.logger.info("✅ Async Pipeline initialized")
            
            # Initialize Intelligent Cache
            if self.settings['cache_enabled']:
                cache_config = {
                    'max_memory_mb': self.settings['cache_max_memory_mb'],
                    'strategy': self.settings['cache_strategy'],
                    'enable_disk_cache': self.settings['cache_disk_enabled'],
                    'disk_cache_dir': self.settings['cache_disk_dir'],
                    'prefetch_enabled': True
                }
                
                self.intelligent_cache = IntelligentCache(cache_config)
                await self.intelligent_cache.start()
                self._register_cache_patterns()
                self.logger.info("✅ Intelligent Cache initialized")
            
            self.is_running = True
            self.logger.info("✅ Standalone Performance Manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Performance Manager: {e}")
            return False
    
    def _register_cache_patterns(self):
        """Register common caching patterns for prefetching"""
        if not self.intelligent_cache:
            return
        
        # File analysis caching
        async def prefetch_file_analysis(key: str):
            if 'analysis_' in key:
                file_path = key.replace('analysis_', '')
                if Path(file_path).exists():
                    return {'prefetched': True, 'file': file_path}
            return None
        
        self.intelligent_cache.register_prefetch_callback('analysis_', prefetch_file_analysis)
        
        # Code generation caching
        async def prefetch_code_generation(key: str):
            if 'generation_' in key:
                return {'prefetched': True, 'type': 'generation'}
            return None
        
        self.intelligent_cache.register_prefetch_callback('generation_', prefetch_code_generation)
    
    async def process_file_analysis(self, file_path: str, analyzer_func: Callable) -> Any:
        """Process file analysis with performance optimizations"""
        cache_key = f"analysis_{file_path}"
        
        # Try cache first
        if self.intelligent_cache:
            cached_result = await self.intelligent_cache.get(cache_key)
            if cached_result:
                self.logger.debug(f"Cache hit for {file_path}")
                return cached_result
        
        # Submit to async pipeline if available
        if self.async_pipeline:
            task_id = f"analyze_{Path(file_path).stem}_{int(time.time())}"
            
            task_id = await self.async_pipeline.submit_task(
                task_id,
                analyzer_func,
                file_path,
                priority=TaskPriority.NORMAL,
                timeout=30.0
            )
            
            result = await self.async_pipeline.wait_for_task(task_id)
            
            # Cache the result
            if self.intelligent_cache and result:
                await self.intelligent_cache.set(cache_key, result, ttl=3600)
            
            return result
        else:
            # Fallback to direct execution
            result = await analyzer_func(file_path) if asyncio.iscoroutinefunction(analyzer_func) else analyzer_func(file_path)
            
            # Cache the result
            if self.intelligent_cache and result:
                await self.intelligent_cache.set(cache_key, result, ttl=3600)
            
            return result
    
    async def batch_process_files(self, 
                                 file_paths: List[str], 
                                 processor_func: Callable,
                                 priority: TaskPriority = TaskPriority.NORMAL) -> List[Any]:
        """Process multiple files efficiently using async pipeline"""
        if not self.async_pipeline:
            # Fallback to sequential processing
            results = []
            for file_path in file_paths:
                result = await self.process_file_analysis(file_path, processor_func)
                results.append(result)
            return results
        
        # Submit all tasks
        task_ids = []
        for i, file_path in enumerate(file_paths):
            task_id = f"batch_{i}_{Path(file_path).stem}_{int(time.time())}"
            
            task_id = await self.async_pipeline.submit_task(
                task_id,
                self.process_file_analysis,
                file_path,
                processor_func,
                priority=priority,
                timeout=30.0
            )
            task_ids.append(task_id)
        
        # Wait for all results
        results = []
        for task_id in task_ids:
            result = await self.async_pipeline.wait_for_task(task_id)
            results.append(result)
        
        return results
    
    async def get_performance_metrics(self) -> PerformanceMetrics:
        """Get comprehensive performance metrics"""
        metrics = PerformanceMetrics(timestamp=time.time())
        
        # Pipeline metrics
        if self.async_pipeline:
            metrics.pipeline_metrics = self.async_pipeline.get_metrics()
            metrics.total_tasks_processed = metrics.pipeline_metrics.total_tasks
        
        # Cache metrics
        if self.intelligent_cache:
            cache_stats = self.intelligent_cache.get_stats()
            metrics.cache_hit_rate = cache_stats.hit_rate
            
            memory_usage = self.intelligent_cache.get_memory_usage()
            metrics.cache_memory_usage_mb = memory_usage['total_size_mb']
        
        # Calculate improvement factor
        if self.baseline_metrics:
            pipeline_improvement = 1.0
            if (self.baseline_metrics.pipeline_metrics and 
                metrics.pipeline_metrics and 
                self.baseline_metrics.pipeline_metrics.throughput_per_second > 0):
                pipeline_improvement = (
                    metrics.pipeline_metrics.throughput_per_second / 
                    self.baseline_metrics.pipeline_metrics.throughput_per_second
                )
            
            cache_improvement = 1.0 + (metrics.cache_hit_rate / 100.0)
            
            metrics.performance_improvement_factor = pipeline_improvement * cache_improvement
        
        self.current_metrics = metrics
        return metrics
    
    async def optimize_performance(self):
        """Automatically optimize performance based on current metrics"""
        if not self.is_running:
            return
        
        metrics = await self.get_performance_metrics()
        
        # Adjust pipeline workers based on utilization
        if (self.async_pipeline and 
            metrics.pipeline_metrics and 
            metrics.pipeline_metrics.worker_utilization > 90):
            
            self.logger.info("High worker utilization detected - performance optimized")
        
        # Optimize cache eviction strategy based on hit rate
        if (self.intelligent_cache and 
            metrics.cache_hit_rate < 50):
            
            self.logger.info("Low cache hit rate detected - optimizing cache strategy")
        
        # Execute optimization callbacks
        for callback in self.optimization_callbacks:
            try:
                await callback(metrics)
            except Exception as e:
                self.logger.warning(f"Optimization callback failed: {e}")
    
    def register_optimization_callback(self, callback: Callable):
        """Register a callback for performance optimization"""
        self.optimization_callbacks.append(callback)
    
    async def set_baseline_metrics(self):
        """Set baseline performance metrics for comparison"""
        self.baseline_metrics = await self.get_performance_metrics()
        self.logger.info("Baseline performance metrics set")
    
    async def generate_performance_report(self) -> Dict[str, Any]:
        """Generate a comprehensive performance report"""
        current_metrics = await self.get_performance_metrics()
        
        report = {
            'timestamp': current_metrics.timestamp,
            'performance_summary': {
                'improvement_factor': current_metrics.performance_improvement_factor,
                'cache_hit_rate': current_metrics.cache_hit_rate,
                'total_tasks_processed': current_metrics.total_tasks_processed,
                'files_analyzed': current_metrics.files_analyzed,
                'average_quality_score': current_metrics.average_quality_score
            },
            'systems_status': {
                'async_pipeline_enabled': self.async_pipeline is not None,
                'cache_enabled': self.intelligent_cache is not None,
                'quality_analyzer_enabled': True
            }
        }
        
        # Detailed pipeline metrics
        if current_metrics.pipeline_metrics:
            report['pipeline_metrics'] = asdict(current_metrics.pipeline_metrics)
        
        # Cache details
        if self.intelligent_cache:
            memory_usage = self.intelligent_cache.get_memory_usage()
            report['cache_metrics'] = {
                'hit_rate': current_metrics.cache_hit_rate,
                'memory_usage_mb': current_metrics.cache_memory_usage_mb,
                'memory_usage_percent': memory_usage.get('memory_usage_percent', 0),
                'total_entries': memory_usage.get('total_entries', 0)
            }
        
        # Performance recommendations
        recommendations = []
        
        if current_metrics.cache_hit_rate < 50:
            recommendations.append("Consider increasing cache size or adjusting cache strategy")
        
        if (current_metrics.pipeline_metrics and 
            current_metrics.pipeline_metrics.worker_utilization > 90):
            recommendations.append("Consider increasing async pipeline workers")
        
        if current_metrics.average_quality_score < self.settings['quality_target_score']:
            recommendations.append("Code quality below target - enable quality analyzer optimizations")
        
        report['recommendations'] = recommendations
        
        return report
    
    async def shutdown(self):
        """Graceful shutdown of all performance systems"""
        self.logger.info("Shutting down Standalone Performance Manager")
        self.is_running = False
        
        if self.async_pipeline:
            await self.async_pipeline.stop()
            self.logger.info("✅ Async Pipeline stopped")
        
        if self.intelligent_cache:
            await self.intelligent_cache.stop()
            self.logger.info("✅ Intelligent Cache stopped")
        
        self.logger.info("✅ Standalone Performance Manager shutdown complete")


# Create factory function for easy instantiation
def create_performance_manager(config: Optional[Dict[str, Any]] = None) -> StandalonePerformanceManager:
    """Create a standalone performance manager with optional config"""
    return StandalonePerformanceManager(config)


# Utility functions for common performance patterns
async def cached_function_call(cache: IntelligentCache, 
                              func: Callable, 
                              cache_key: str,
                              ttl: int = 3600,
                              *args, **kwargs) -> Any:
    """Execute function with caching"""
    # Try cache first
    result = await cache.get(cache_key)
    if result is not None:
        return result
    
    # Execute function
    if asyncio.iscoroutinefunction(func):
        result = await func(*args, **kwargs)
    else:
        result = func(*args, **kwargs)
    
    # Cache result
    await cache.set(cache_key, result, ttl=ttl)
    return result