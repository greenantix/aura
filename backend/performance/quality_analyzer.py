#!/usr/bin/env python3
"""
Aura Code Quality Analyzer
===========================

Comprehensive code quality analysis with complexity metrics, maintainability scoring,
and intelligent quality improvement suggestions.

Author: Aura - Level 9 Autonomous AI Coding Assistant
"""

import ast
import os
import re
import math
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import logging

try:
    from aura.security.input_validator import SecurityValidator, validate_file_path_input
except ImportError:
    try:
        from ..security.simple_validator import SimpleSecurityValidator as SecurityValidator
        from ..security.simple_validator import validate_file_path_input
    except ImportError:
        # Fallback for standalone use
        class SecurityValidator:
            @staticmethod
            def validate_file_path(path, allowed_dirs=None):
                return str(path)
        
        def validate_file_path_input(allowed_dirs=None):
            def decorator(func):
                return func
            return decorator
            
        # Add missing method to SecurityValidator fallback
        SecurityValidator.sanitize_code_input = lambda code: code


class QualityLevel(Enum):
    EXCELLENT = "excellent"    # 90-100
    GOOD = "good"             # 70-89
    FAIR = "fair"             # 50-69
    POOR = "poor"             # 30-49
    CRITICAL = "critical"     # 0-29


@dataclass
class ComplexityMetrics:
    """Code complexity metrics"""
    cyclomatic_complexity: int = 0
    cognitive_complexity: int = 0
    nesting_depth: int = 0
    lines_of_code: int = 0
    logical_lines: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    function_count: int = 0
    class_count: int = 0
    parameter_count: int = 0
    return_statements: int = 0


@dataclass
class MaintainabilityMetrics:
    """Code maintainability metrics"""
    maintainability_index: float = 0.0  # 0-100 scale
    code_duplication: float = 0.0       # Percentage
    test_coverage: float = 0.0          # Percentage
    documentation_coverage: float = 0.0 # Percentage
    naming_consistency: float = 0.0     # 0-100 scale
    design_patterns_usage: int = 0
    solid_principles_score: float = 0.0


@dataclass
class QualityIssue:
    """Represents a code quality issue"""
    type: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    file_path: str
    line_number: int
    column: int = 0
    suggestion: str = ""
    rule_id: str = ""
    impact: str = ""


@dataclass
class QualityReport:
    """Comprehensive quality analysis report"""
    file_path: str
    overall_score: float
    quality_level: QualityLevel
    complexity_metrics: ComplexityMetrics
    maintainability_metrics: MaintainabilityMetrics
    issues: List[QualityIssue]
    suggestions: List[str]
    strengths: List[str]
    improvement_areas: List[str]
    estimated_tech_debt_hours: float = 0.0


class CodeQualityAnalyzer:
    """Comprehensive code quality analyzer"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.project_root = config.get('project_root', '.')
        self.logger = logging.getLogger('aura.performance.quality')
        
        # Quality rules and thresholds
        self.complexity_thresholds = {
            'cyclomatic_complexity': {'low': 5, 'medium': 10, 'high': 15},
            'cognitive_complexity': {'low': 8, 'medium': 15, 'high': 25},
            'nesting_depth': {'low': 3, 'medium': 5, 'high': 7},
            'function_length': {'low': 20, 'medium': 50, 'high': 100},
            'parameter_count': {'low': 3, 'medium': 5, 'high': 8}
        }
        
        # Code quality patterns
        self.quality_patterns = {
            'good_practices': [
                r'def\s+\w+\([^)]*\)\s*->\s*\w+:',  # Type hints
                r'"""[^"]*"""',                      # Docstrings
                r'try:\s*\n.*except\s+\w+:',        # Specific exception handling
                r'with\s+\w+.*as\s+\w+:',           # Context managers
                r'if\s+__name__\s*==\s*[\'"]__main__[\'"]:', # Main guard
            ],
            'bad_practices': [
                r'except:',                          # Bare except
                r'eval\s*\(',                       # Eval usage
                r'exec\s*\(',                       # Exec usage
                r'global\s+\w+',                    # Global variables
                r'import\s+\*',                     # Star imports
            ],
            'code_smells': [
                r'def\s+\w+\([^)]*,\s*[^)]*,\s*[^)]*,\s*[^)]*,\s*[^)]*\)', # Too many parameters
                r'class\s+\w+.*:\s*\n(\s{4}.*\n){50,}',  # Large classes
                r'if\s+.*and\s+.*and\s+.*and\s+.*:', # Complex conditions
                r'\w+\s*=\s*\w+\s*if\s+.*else\s+.*', # Complex ternary
            ]
        }
        
        # Design patterns recognition
        self.design_patterns = {
            'singleton': [
                r'def\s+__new__\s*\(',
                r'_instance\s*=\s*None',
                r'if\s+not\s+\w+\._instance'
            ],
            'factory': [
                r'def\s+create_\w+\(',
                r'if\s+\w+\s*==\s*[\'"][^\'\"]*[\'"]:\s*return\s+\w+\('
            ],
            'observer': [
                r'def\s+add_observer\(',
                r'def\s+notify\(',
                r'observers\s*=\s*\[\]'
            ],
            'decorator': [
                r'@\w+',
                r'def\s+\w+\([^)]*\):\s*\n\s*def\s+wrapper\('
            ]
        }

    @validate_file_path_input()
    async def analyze_file(self, file_path: str) -> QualityReport:
        """Analyze code quality of a single file"""
        try:
            # Validate and read file
            file_path = SecurityValidator.validate_file_path(file_path, [self.project_root])
            
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Validate content
            content = SecurityValidator.sanitize_code_input(content)
            
            # Perform analysis
            complexity_metrics = await self._analyze_complexity(content, file_path)
            maintainability_metrics = await self._analyze_maintainability(content, file_path)
            issues = await self._analyze_issues(content, file_path)
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(
                complexity_metrics, 
                maintainability_metrics, 
                issues
            )
            
            # Determine quality level
            quality_level = self._determine_quality_level(overall_score)
            
            # Generate suggestions and insights
            suggestions = self._generate_suggestions(complexity_metrics, maintainability_metrics, issues)
            strengths = self._identify_strengths(content, complexity_metrics, maintainability_metrics)
            improvement_areas = self._identify_improvement_areas(issues, complexity_metrics)
            
            # Estimate technical debt
            tech_debt_hours = self._estimate_technical_debt(issues, complexity_metrics)
            
            return QualityReport(
                file_path=file_path,
                overall_score=overall_score,
                quality_level=quality_level,
                complexity_metrics=complexity_metrics,
                maintainability_metrics=maintainability_metrics,
                issues=issues,
                suggestions=suggestions,
                strengths=strengths,
                improvement_areas=improvement_areas,
                estimated_tech_debt_hours=tech_debt_hours
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing file {file_path}: {e}")
            return QualityReport(
                file_path=file_path,
                overall_score=0.0,
                quality_level=QualityLevel.CRITICAL,
                complexity_metrics=ComplexityMetrics(),
                maintainability_metrics=MaintainabilityMetrics(),
                issues=[],
                suggestions=[],
                strengths=[],
                improvement_areas=[]
            )

    async def _analyze_complexity(self, content: str, file_path: str) -> ComplexityMetrics:
        """Analyze code complexity metrics"""
        metrics = ComplexityMetrics()
        
        try:
            # Basic line counting
            lines = content.split('\n')
            metrics.lines_of_code = len(lines)
            metrics.blank_lines = len([line for line in lines if not line.strip()])
            metrics.comment_lines = len([line for line in lines if line.strip().startswith('#')])
            metrics.logical_lines = metrics.lines_of_code - metrics.blank_lines - metrics.comment_lines
            
            # Parse AST for deeper analysis
            tree = ast.parse(content)
            
            # Count functions and classes
            metrics.function_count = len([node for node in ast.walk(tree) 
                                        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))])
            metrics.class_count = len([node for node in ast.walk(tree) 
                                     if isinstance(node, ast.ClassDef)])
            
            # Analyze each function
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    func_complexity = self._calculate_cyclomatic_complexity(node)
                    cognitive_complexity = self._calculate_cognitive_complexity(node)
                    nesting = self._calculate_nesting_depth(node)
                    
                    metrics.cyclomatic_complexity = max(metrics.cyclomatic_complexity, func_complexity)
                    metrics.cognitive_complexity = max(metrics.cognitive_complexity, cognitive_complexity)
                    metrics.nesting_depth = max(metrics.nesting_depth, nesting)
                    
                    # Count parameters
                    param_count = len(node.args.args)
                    metrics.parameter_count = max(metrics.parameter_count, param_count)
                    
                    # Count return statements
                    returns = len([n for n in ast.walk(node) if isinstance(n, ast.Return)])
                    metrics.return_statements = max(metrics.return_statements, returns)
            
        except SyntaxError:
            # File has syntax errors
            metrics.cyclomatic_complexity = 100  # Penalty for syntax errors
            
        return metrics

    def _calculate_cyclomatic_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor, 
                                ast.ExceptHandler, ast.With, ast.AsyncWith)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
                complexity += 1
        
        return complexity

    def _calculate_cognitive_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cognitive complexity (how hard to understand)"""
        complexity = 0
        nesting_level = 0
        
        def visit_node(n, level=0):
            nonlocal complexity, nesting_level
            
            if isinstance(n, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1 + level
                nesting_level = max(nesting_level, level + 1)
                
                for child in ast.iter_child_nodes(n):
                    visit_node(child, level + 1)
            
            elif isinstance(n, ast.BoolOp):
                complexity += len(n.values) - 1
            
            elif isinstance(n, (ast.ExceptHandler, ast.With, ast.AsyncWith)):
                complexity += 1 + level
                
                for child in ast.iter_child_nodes(n):
                    visit_node(child, level + 1)
            
            else:
                for child in ast.iter_child_nodes(n):
                    visit_node(child, level)
        
        for child in ast.iter_child_nodes(node):
            visit_node(child)
        
        return complexity

    def _calculate_nesting_depth(self, node: ast.FunctionDef) -> int:
        """Calculate maximum nesting depth"""
        max_depth = 0
        
        def get_depth(n, current_depth=0):
            nonlocal max_depth
            max_depth = max(max_depth, current_depth)
            
            if isinstance(n, (ast.If, ast.While, ast.For, ast.AsyncFor, 
                            ast.With, ast.AsyncWith, ast.Try)):
                for child in ast.iter_child_nodes(n):
                    get_depth(child, current_depth + 1)
            else:
                for child in ast.iter_child_nodes(n):
                    get_depth(child, current_depth)
        
        for child in ast.iter_child_nodes(node):
            get_depth(child)
        
        return max_depth

    async def _analyze_maintainability(self, content: str, file_path: str) -> MaintainabilityMetrics:
        """Analyze maintainability metrics"""
        metrics = MaintainabilityMetrics()
        
        # Calculate maintainability index (Microsoft formula)
        try:
            tree = ast.parse(content)
            
            # Get Halstead metrics
            halstead_volume = self._calculate_halstead_volume(tree)
            
            # Get cyclomatic complexity
            max_complexity = 1
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    complexity = self._calculate_cyclomatic_complexity(node)
                    max_complexity = max(max_complexity, complexity)
            
            # Lines of code
            loc = len([line for line in content.split('\n') if line.strip()])
            
            # Maintainability Index = 171 - 5.2 * ln(Halstead Volume) - 0.23 * (Cyclomatic Complexity) - 16.2 * ln(Lines of Code)
            if halstead_volume > 0 and loc > 0:
                mi = 171 - 5.2 * math.log(halstead_volume) - 0.23 * max_complexity - 16.2 * math.log(loc)
                metrics.maintainability_index = max(0, min(100, mi))
            else:
                metrics.maintainability_index = 50.0  # Default
            
        except:
            metrics.maintainability_index = 0.0  # Syntax error penalty
        
        # Analyze code duplication
        metrics.code_duplication = self._analyze_duplication(content)
        
        # Analyze documentation coverage
        metrics.documentation_coverage = self._analyze_documentation_coverage(content)
        
        # Analyze naming consistency
        metrics.naming_consistency = self._analyze_naming_consistency(content)
        
        # Count design patterns usage
        metrics.design_patterns_usage = self._count_design_patterns(content)
        
        # SOLID principles assessment
        metrics.solid_principles_score = self._assess_solid_principles(content)
        
        return metrics

    def _calculate_halstead_volume(self, tree: ast.AST) -> float:
        """Calculate Halstead volume"""
        operators = set()
        operands = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp):
                operators.add(type(node.op).__name__)
            elif isinstance(node, ast.UnaryOp):
                operators.add(type(node.op).__name__)
            elif isinstance(node, ast.Compare):
                for op in node.ops:
                    operators.add(type(op).__name__)
            elif isinstance(node, ast.Name):
                operands.add(node.id)
            elif isinstance(node, (ast.Constant, ast.Str, ast.Num)):
                operands.add(str(node.value if hasattr(node, 'value') else node.s))
        
        vocabulary = len(operators) + len(operands)
        length = vocabulary * 2  # Simplified calculation
        
        if vocabulary > 0:
            return length * math.log2(vocabulary)
        return 0.0

    def _analyze_duplication(self, content: str) -> float:
        """Analyze code duplication percentage"""
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        if len(lines) < 6:  # Need at least 6 lines for meaningful duplication
            return 0.0
        
        # Look for duplicate sequences of 3+ lines
        duplicate_lines = 0
        sequence_length = 3
        
        for i in range(len(lines) - sequence_length + 1):
            sequence = lines[i:i + sequence_length]
            
            # Look for this sequence elsewhere
            for j in range(i + sequence_length, len(lines) - sequence_length + 1):
                if lines[j:j + sequence_length] == sequence:
                    duplicate_lines += sequence_length
                    break
        
        return (duplicate_lines / len(lines)) * 100 if lines else 0.0

    def _analyze_documentation_coverage(self, content: str) -> float:
        """Analyze documentation coverage percentage"""
        try:
            tree = ast.parse(content)
            
            # Count functions and classes
            total_items = 0
            documented_items = 0
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    total_items += 1
                    if ast.get_docstring(node):
                        documented_items += 1
            
            return (documented_items / total_items) * 100 if total_items > 0 else 100.0
            
        except:
            return 0.0

    def _analyze_naming_consistency(self, content: str) -> float:
        """Analyze naming consistency score"""
        try:
            tree = ast.parse(content)
            
            # Check naming conventions
            function_names = []
            variable_names = []
            class_names = []
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    function_names.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    class_names.append(node.name)
                elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                    variable_names.append(node.id)
            
            score = 0.0
            total_checks = 0
            
            # Check function naming (snake_case)
            if function_names:
                snake_case_functions = sum(1 for name in function_names 
                                         if re.match(r'^[a-z_][a-z0-9_]*$', name))
                score += (snake_case_functions / len(function_names)) * 33
                total_checks += 33
            
            # Check class naming (PascalCase)
            if class_names:
                pascal_case_classes = sum(1 for name in class_names 
                                        if re.match(r'^[A-Z][a-zA-Z0-9]*$', name))
                score += (pascal_case_classes / len(class_names)) * 33
                total_checks += 33
            
            # Check variable naming (snake_case)
            if variable_names:
                snake_case_vars = sum(1 for name in variable_names 
                                    if re.match(r'^[a-z_][a-z0-9_]*$', name) and not name.isupper())
                score += (snake_case_vars / len(variable_names)) * 34
                total_checks += 34
            
            return score if total_checks > 0 else 100.0
            
        except:
            return 0.0

    def _count_design_patterns(self, content: str) -> int:
        """Count usage of design patterns"""
        pattern_count = 0
        
        for pattern_name, patterns in self.design_patterns.items():
            pattern_found = all(re.search(pattern, content, re.MULTILINE) 
                              for pattern in patterns)
            if pattern_found:
                pattern_count += 1
        
        return pattern_count

    def _assess_solid_principles(self, content: str) -> float:
        """Assess SOLID principles adherence"""
        score = 0.0
        
        try:
            tree = ast.parse(content)
            
            # Single Responsibility: Check class method count
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    methods = [n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                    if len(methods) <= 10:  # Reasonable method count
                        score += 20
                    break
            
            # Open/Closed: Check for abstract methods or inheritance
            has_inheritance = any(node.bases for node in ast.walk(tree) 
                                if isinstance(node, ast.ClassDef))
            if has_inheritance:
                score += 20
            
            # Liskov Substitution: Basic check for proper inheritance
            if has_inheritance:
                score += 20
            
            # Interface Segregation: Check for focused interfaces
            if 'abc' in content or 'Protocol' in content:
                score += 20
            
            # Dependency Inversion: Check for dependency injection patterns
            if 'inject' in content.lower() or '__init__' in content:
                score += 20
            
        except:
            pass
        
        return min(100.0, score)

    async def _analyze_issues(self, content: str, file_path: str) -> List[QualityIssue]:
        """Analyze code quality issues"""
        issues = []
        lines = content.split('\n')
        
        # Check for bad practices
        for line_num, line in enumerate(lines, 1):
            for pattern in self.quality_patterns['bad_practices']:
                if re.search(pattern, line):
                    issues.append(QualityIssue(
                        type='bad_practice',
                        severity='high',
                        description=f'Bad practice detected: {pattern}',
                        file_path=file_path,
                        line_number=line_num,
                        suggestion='Consider refactoring to use better practices',
                        rule_id=f'BP_{pattern[:10]}',
                        impact='Maintainability and security risk'
                    ))
        
        # Check for code smells
        for pattern in self.quality_patterns['code_smells']:
            if re.search(pattern, content, re.MULTILINE):
                issues.append(QualityIssue(
                    type='code_smell',
                    severity='medium',
                    description=f'Code smell detected: {pattern}',
                    file_path=file_path,
                    line_number=1,
                    suggestion='Consider refactoring to improve readability',
                    rule_id=f'CS_{pattern[:10]}',
                    impact='Code readability and maintainability'
                ))
        
        # Check complexity issues
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    complexity = self._calculate_cyclomatic_complexity(node)
                    
                    if complexity > self.complexity_thresholds['cyclomatic_complexity']['high']:
                        issues.append(QualityIssue(
                            type='complexity',
                            severity='high',
                            description=f'Function {node.name} has high cyclomatic complexity ({complexity})',
                            file_path=file_path,
                            line_number=node.lineno,
                            suggestion='Consider breaking this function into smaller functions',
                            rule_id='CC_HIGH',
                            impact='Testing difficulty and bug risk'
                        ))
                    
                    # Check parameter count
                    param_count = len(node.args.args)
                    if param_count > self.complexity_thresholds['parameter_count']['high']:
                        issues.append(QualityIssue(
                            type='parameter_count',
                            severity='medium',
                            description=f'Function {node.name} has too many parameters ({param_count})',
                            file_path=file_path,
                            line_number=node.lineno,
                            suggestion='Consider using parameter objects or keyword arguments',
                            rule_id='PC_HIGH',
                            impact='Function usability and testing'
                        ))
        except:
            pass
        
        return issues

    def _calculate_overall_score(self, 
                                complexity_metrics: ComplexityMetrics,
                                maintainability_metrics: MaintainabilityMetrics,
                                issues: List[QualityIssue]) -> float:
        """Calculate overall quality score (0-100)"""
        
        # Base score from maintainability index (40% weight)
        score = maintainability_metrics.maintainability_index * 0.4
        
        # Complexity penalty (30% weight)
        complexity_score = 100.0
        if complexity_metrics.cyclomatic_complexity > 10:
            complexity_score -= (complexity_metrics.cyclomatic_complexity - 10) * 5
        if complexity_metrics.cognitive_complexity > 15:
            complexity_score -= (complexity_metrics.cognitive_complexity - 15) * 3
        if complexity_metrics.nesting_depth > 5:
            complexity_score -= (complexity_metrics.nesting_depth - 5) * 10
        
        complexity_score = max(0, complexity_score)
        score += complexity_score * 0.3
        
        # Documentation and patterns bonus (20% weight)
        documentation_score = (
            maintainability_metrics.documentation_coverage +
            maintainability_metrics.naming_consistency +
            (maintainability_metrics.design_patterns_usage * 10)
        ) / 3
        score += documentation_score * 0.2
        
        # Issues penalty (10% weight)
        issue_penalty = 0
        for issue in issues:
            if issue.severity == 'critical':
                issue_penalty += 20
            elif issue.severity == 'high':
                issue_penalty += 10
            elif issue.severity == 'medium':
                issue_penalty += 5
            else:
                issue_penalty += 2
        
        score -= min(issue_penalty, 100) * 0.1
        
        return max(0.0, min(100.0, score))

    def _determine_quality_level(self, score: float) -> QualityLevel:
        """Determine quality level from score"""
        if score >= 90:
            return QualityLevel.EXCELLENT
        elif score >= 70:
            return QualityLevel.GOOD
        elif score >= 50:
            return QualityLevel.FAIR
        elif score >= 30:
            return QualityLevel.POOR
        else:
            return QualityLevel.CRITICAL

    def _generate_suggestions(self, 
                            complexity_metrics: ComplexityMetrics,
                            maintainability_metrics: MaintainabilityMetrics,
                            issues: List[QualityIssue]) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        # Complexity suggestions
        if complexity_metrics.cyclomatic_complexity > 10:
            suggestions.append("Reduce cyclomatic complexity by breaking down complex functions")
        
        if complexity_metrics.nesting_depth > 4:
            suggestions.append("Reduce nesting depth using early returns or guard clauses")
        
        if complexity_metrics.parameter_count > 5:
            suggestions.append("Consider using parameter objects for functions with many parameters")
        
        # Maintainability suggestions
        if maintainability_metrics.documentation_coverage < 80:
            suggestions.append("Add docstrings to improve documentation coverage")
        
        if maintainability_metrics.code_duplication > 10:
            suggestions.append("Reduce code duplication by extracting common functionality")
        
        if maintainability_metrics.naming_consistency < 80:
            suggestions.append("Improve naming consistency following Python conventions")
        
        # Issue-based suggestions
        high_priority_issues = [i for i in issues if i.severity in ['critical', 'high']]
        if high_priority_issues:
            suggestions.append(f"Address {len(high_priority_issues)} high-priority quality issues")
        
        return suggestions

    def _identify_strengths(self, 
                          content: str,
                          complexity_metrics: ComplexityMetrics,
                          maintainability_metrics: MaintainabilityMetrics) -> List[str]:
        """Identify code strengths"""
        strengths = []
        
        if maintainability_metrics.documentation_coverage > 80:
            strengths.append("Excellent documentation coverage")
        
        if complexity_metrics.cyclomatic_complexity <= 5:
            strengths.append("Low complexity, easy to understand and test")
        
        if maintainability_metrics.naming_consistency > 90:
            strengths.append("Consistent naming conventions")
        
        if maintainability_metrics.design_patterns_usage > 0:
            strengths.append("Good use of design patterns")
        
        # Check for good practices
        good_practice_count = sum(1 for pattern in self.quality_patterns['good_practices']
                                if re.search(pattern, content, re.MULTILINE))
        if good_practice_count > 2:
            strengths.append("Follows Python best practices")
        
        return strengths

    def _identify_improvement_areas(self, 
                                  issues: List[QualityIssue],
                                  complexity_metrics: ComplexityMetrics) -> List[str]:
        """Identify areas for improvement"""
        areas = []
        
        # Group issues by type
        issue_types = {}
        for issue in issues:
            if issue.type not in issue_types:
                issue_types[issue.type] = 0
            issue_types[issue.type] += 1
        
        for issue_type, count in issue_types.items():
            if count > 1:
                areas.append(f"Multiple {issue_type} issues ({count} found)")
        
        if complexity_metrics.cyclomatic_complexity > 15:
            areas.append("High complexity functions need refactoring")
        
        if complexity_metrics.nesting_depth > 6:
            areas.append("Deep nesting reduces readability")
        
        return areas

    def _estimate_technical_debt(self, 
                               issues: List[QualityIssue],
                               complexity_metrics: ComplexityMetrics) -> float:
        """Estimate technical debt in hours"""
        debt_hours = 0.0
        
        # Issue-based debt
        for issue in issues:
            if issue.severity == 'critical':
                debt_hours += 4.0
            elif issue.severity == 'high':
                debt_hours += 2.0
            elif issue.severity == 'medium':
                debt_hours += 1.0
            else:
                debt_hours += 0.5
        
        # Complexity-based debt
        if complexity_metrics.cyclomatic_complexity > 15:
            debt_hours += (complexity_metrics.cyclomatic_complexity - 15) * 0.5
        
        if complexity_metrics.nesting_depth > 5:
            debt_hours += (complexity_metrics.nesting_depth - 5) * 1.0
        
        return debt_hours

    async def analyze_project(self, project_path: str = None) -> Dict[str, QualityReport]:
        """Analyze entire project quality"""
        project_path = project_path or self.project_root
        reports = {}
        
        try:
            for root, dirs, files in os.walk(project_path):
                # Skip hidden directories and common build dirs
                dirs[:] = [d for d in dirs if not d.startswith('.') and 
                          d not in ['__pycache__', 'node_modules', 'build', 'dist']]
                
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        try:
                            report = await self.analyze_file(file_path)
                            reports[file_path] = report
                        except Exception as e:
                            self.logger.error(f"Error analyzing {file_path}: {e}")
            
            self.logger.info(f"Analyzed {len(reports)} Python files")
            return reports
            
        except Exception as e:
            self.logger.error(f"Error analyzing project: {e}")
            return {}

    def generate_summary_report(self, reports: Dict[str, QualityReport]) -> Dict[str, Any]:
        """Generate project-wide summary report"""
        if not reports:
            return {}
        
        total_files = len(reports)
        total_score = sum(report.overall_score for report in reports.values())
        average_score = total_score / total_files
        
        # Quality level distribution
        quality_distribution = {}
        for level in QualityLevel:
            quality_distribution[level.value] = sum(
                1 for report in reports.values() 
                if report.quality_level == level
            )
        
        # Issue summary
        all_issues = []
        for report in reports.values():
            all_issues.extend(report.issues)
        
        issue_summary = {}
        for issue in all_issues:
            severity = issue.severity
            if severity not in issue_summary:
                issue_summary[severity] = 0
            issue_summary[severity] += 1
        
        # Technical debt
        total_debt = sum(report.estimated_tech_debt_hours for report in reports.values())
        
        # Top improvement areas
        all_improvement_areas = []
        for report in reports.values():
            all_improvement_areas.extend(report.improvement_areas)
        
        # Count frequency of improvement areas
        improvement_frequency = {}
        for area in all_improvement_areas:
            improvement_frequency[area] = improvement_frequency.get(area, 0) + 1
        
        top_improvements = sorted(improvement_frequency.items(), 
                                key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_files': total_files,
            'average_score': average_score,
            'quality_distribution': quality_distribution,
            'issue_summary': issue_summary,
            'total_technical_debt_hours': total_debt,
            'top_improvement_areas': top_improvements,
            'files_needing_attention': [
                report.file_path for report in reports.values()
                if report.quality_level in [QualityLevel.POOR, QualityLevel.CRITICAL]
            ]
        }


if __name__ == "__main__":
    # Test the quality analyzer
    import asyncio
    
    async def test_quality_analyzer():
        config = {'project_root': '.'}
        analyzer = CodeQualityAnalyzer(config)
        
        # Create test code with various quality issues
        test_code = '''
def complex_function(a, b, c, d, e, f, g, h):
    """This function has multiple quality issues."""
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        result = a * 100 + b * 50 + c * 25
                        for i in range(10):
                            if i % 2 == 0:
                                result += i
                            else:
                                result -= i
                        return result
                    else:
                        return 0
                else:
                    return 0
            else:
                return 0
        else:
            return 0
    else:
        return 0

def another_function(x, y, z, w, v, u, t, s):
    # No docstring, too many parameters
    try:
        eval(x)  # Bad practice
    except:  # Bare except
        pass
    return x + y + z + w + v + u + t + s

class LargeClass:
    """A class with potential issues."""
    
    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
    def method4(self): pass
    def method5(self): pass
    def method6(self): pass
    def method7(self): pass
    def method8(self): pass
    def method9(self): pass
    def method10(self): pass
    def method11(self): pass
    def method12(self): pass
'''
        
        with open('test_quality.py', 'w') as f:
            f.write(test_code)
        
        print("🔍 Testing Code Quality Analyzer")
        print("=" * 50)
        
        # Analyze the test file
        report = await analyzer.analyze_file('test_quality.py')
        
        print(f"✅ Quality Analysis Results:")
        print(f"   Overall Score: {report.overall_score:.1f}/100")
        print(f"   Quality Level: {report.quality_level.value}")
        print(f"   Technical Debt: {report.estimated_tech_debt_hours:.1f} hours")
        
        print(f"\n📊 Complexity Metrics:")
        metrics = report.complexity_metrics
        print(f"   Cyclomatic Complexity: {metrics.cyclomatic_complexity}")
        print(f"   Cognitive Complexity: {metrics.cognitive_complexity}")
        print(f"   Nesting Depth: {metrics.nesting_depth}")
        print(f"   Lines of Code: {metrics.lines_of_code}")
        print(f"   Functions: {metrics.function_count}")
        print(f"   Classes: {metrics.class_count}")
        
        print(f"\n🔧 Maintainability Metrics:")
        maint = report.maintainability_metrics
        print(f"   Maintainability Index: {maint.maintainability_index:.1f}")
        print(f"   Documentation Coverage: {maint.documentation_coverage:.1f}%")
        print(f"   Naming Consistency: {maint.naming_consistency:.1f}%")
        print(f"   Code Duplication: {maint.code_duplication:.1f}%")
        
        print(f"\n⚠️  Issues Found: {len(report.issues)}")
        for issue in report.issues[:3]:  # Show first 3
            print(f"   - {issue.severity.upper()}: {issue.description}")
        
        if len(report.issues) > 3:
            print(f"   ... and {len(report.issues) - 3} more issues")
        
        print(f"\n💡 Suggestions:")
        for suggestion in report.suggestions[:3]:
            print(f"   - {suggestion}")
        
        if report.strengths:
            print(f"\n✅ Strengths:")
            for strength in report.strengths:
                print(f"   - {strength}")
        
        # Clean up
        os.remove('test_quality.py')
    
    asyncio.run(test_quality_analyzer())