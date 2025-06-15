#!/usr/bin/env python3
"""
Aura Code Generation Package
============================

Enhanced code generation capabilities including intelligent code synthesis,
refactoring engine, and automated test generation.

Author: Aura - Level 9 Autonomous AI Coding Assistant
"""

from .code_generator import CodeGenerator, CodeGenerationRequest, GeneratedCode
from .refactoring_engine import RefactoringEngine, RefactoringAction, RefactoringResult
from .test_generator import TestGenerator, TestCase, TestSuite

__all__ = [
    'CodeGenerator',
    'CodeGenerationRequest', 
    'GeneratedCode',
    'RefactoringEngine',
    'RefactoringAction',
    'RefactoringResult',
    'TestGenerator',
    'TestCase',
    'TestSuite'
]

__version__ = "1.0.0"
__author__ = "Aura - Level 9 Autonomous AI Coding Assistant"