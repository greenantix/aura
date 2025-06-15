#!/usr/bin/env python3
"""
Aura Performance Optimization Package
=====================================

High-performance systems for async processing, code quality analysis,
and intelligent caching to optimize Aura's autonomous capabilities.

Author: Aura - Level 9 Autonomous AI Coding Assistant
"""

from .async_pipeline import AsyncPipeline, PipelineTask, TaskPriority, process_batch
from .quality_analyzer import CodeQualityAnalyzer, QualityReport, ComplexityMetrics, MaintainabilityMetrics
from .intelligent_cache import IntelligentCache, CacheStrategy, CacheLevel, cached
from .standalone_manager import StandalonePerformanceManager

# Import complex performance manager only if available
try:
    from .performance_manager import PerformanceManager, PerformanceMetrics, cached_function_call, performance_monitor
    COMPLEX_MANAGER_AVAILABLE = True
except ImportError:
    COMPLEX_MANAGER_AVAILABLE = False
    PerformanceManager = None
    PerformanceMetrics = None
    cached_function_call = None
    performance_monitor = None

__all__ = [
    'AsyncPipeline',
    'PipelineTask', 
    'TaskPriority',
    'process_batch',
    'CodeQualityAnalyzer',
    'QualityReport',
    'ComplexityMetrics',
    'MaintainabilityMetrics',
    'IntelligentCache',
    'CacheStrategy',
    'CacheLevel',
    'cached',
    'StandalonePerformanceManager',
    'COMPLEX_MANAGER_AVAILABLE'
]

# Add complex manager to exports if available
if COMPLEX_MANAGER_AVAILABLE:
    __all__.extend([
        'PerformanceManager',
        'PerformanceMetrics',
        'cached_function_call',
        'performance_monitor'
    ])

__version__ = "1.0.0"
__author__ = "Aura - Level 9 Autonomous AI Coding Assistant"