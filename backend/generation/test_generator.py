#!/usr/bin/env python3
"""
Aura Intelligent Test Generator
===============================

Automated test creation with coverage analysis, edge case detection,
and intelligent test scenario generation.

Author: Aura - Level 9 Autonomous AI Coding Assistant
"""

import ast
import re
import os
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from pathlib import Path
import logging

from aura.security.input_validator import SecurityValidator, validate_code_input


@dataclass
class TestCase:
    """Represents a single test case"""
    name: str
    description: str
    test_type: str  # 'unit', 'integration', 'edge_case', 'error_case'
    setup: Optional[str] = None
    test_code: str = ""
    assertions: List[str] = None
    cleanup: Optional[str] = None
    dependencies: List[str] = None


@dataclass
class TestSuite:
    """Collection of test cases for a module/function"""
    target_function: str
    target_file: str
    test_cases: List[TestCase]
    coverage_percentage: float
    framework: str  # 'pytest', 'unittest', 'jest', 'mocha'
    setup_code: Optional[str] = None
    teardown_code: Optional[str] = None


class TestGenerator:
    """Intelligent test case generator"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.project_root = config.get('project_root', '.')
        self.test_framework = config.get('test_framework', 'pytest')
        self.logger = logging.getLogger('aura.generation.test_generator')
        
        # Test templates for different frameworks
        self.test_templates = {
            'pytest': {
                'function_test': '''def test_{function_name}_{test_type}():
    \"\"\"Test {function_name} - {description}.\"\"\"
    # Arrange
    {setup}
    
    # Act
    result = {function_call}
    
    # Assert
    {assertions}''',
                'class_test': '''class Test{class_name}:
    \"\"\"Test suite for {class_name}.\"\"\"
    
    def setup_method(self):
        \"\"\"Set up test fixtures.\"\"\"
        {setup}
    
    {test_methods}''',
                'fixture': '''@pytest.fixture
def {fixture_name}():
    \"\"\"Fixture for {description}.\"\"\"
    {fixture_code}
    return {return_value}'''
            },
            'unittest': {
                'function_test': '''def test_{function_name}_{test_type}(self):
    \"\"\"Test {function_name} - {description}.\"\"\"
    # Arrange
    {setup}
    
    # Act
    result = {function_call}
    
    # Assert
    {assertions}''',
                'class_test': '''class Test{class_name}(unittest.TestCase):
    \"\"\"Test suite for {class_name}.\"\"\"
    
    def setUp(self):
        \"\"\"Set up test fixtures.\"\"\"
        {setup}
    
    {test_methods}'''
            },
            'jest': {
                'function_test': '''test('{function_name} - {description}', () => {{
    // Arrange
    {setup}
    
    // Act
    const result = {function_call};
    
    // Assert
    {assertions}
}});''',
                'class_test': '''describe('{class_name}', () => {{
    let instance;
    
    beforeEach(() => {{
        {setup}
    }});
    
    {test_methods}
}});'''
            }
        }
        
        # Common test patterns
        self.test_patterns = {
            'boundary_values': {
                'numeric': [0, 1, -1, 'max_value', 'min_value'],
                'string': ['', 'single_char', 'very_long_string'],
                'list': [[], '[single_item]', '[multiple_items]']
            },
            'error_conditions': {
                'python': ['None', 'empty_list', 'invalid_type', 'out_of_range'],
                'javascript': ['null', 'undefined', 'empty_array', 'invalid_type']
            },
            'common_scenarios': [
                'happy_path', 'edge_case', 'error_handling', 'boundary_conditions'
            ]
        }

    @validate_code_input()
    async def generate_tests(self, file_path: str, target_function: str = None) -> TestSuite:
        """Generate comprehensive tests for a file or specific function"""
        try:
            # Validate file path
            file_path = SecurityValidator.validate_file_path(file_path, [self.project_root])
            
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Validate code content
            content = SecurityValidator.sanitize_code_input(content)
            
            # Parse the code
            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                self.logger.error(f"Syntax error in {file_path}: {e}")
                return TestSuite(
                    target_function=target_function or 'unknown',
                    target_file=file_path,
                    test_cases=[],
                    coverage_percentage=0.0,
                    framework=self.test_framework
                )
            
            # Analyze functions to test
            functions_to_test = self._extract_functions(tree)
            
            if target_function:
                functions_to_test = [f for f in functions_to_test if f['name'] == target_function]
            
            # Generate test cases for each function
            all_test_cases = []
            for func_info in functions_to_test:
                test_cases = await self._generate_function_tests(func_info, content, file_path)
                all_test_cases.extend(test_cases)
            
            # Calculate coverage estimate
            coverage = self._estimate_coverage(all_test_cases, functions_to_test)
            
            return TestSuite(
                target_function=target_function or 'all_functions',
                target_file=file_path,
                test_cases=all_test_cases,
                coverage_percentage=coverage,
                framework=self.test_framework,
                setup_code=self._generate_setup_code(file_path),
                teardown_code=self._generate_teardown_code()
            )
            
        except Exception as e:
            self.logger.error(f"Error generating tests: {e}")
            return TestSuite(
                target_function=target_function or 'error',
                target_file=file_path,
                test_cases=[],
                coverage_percentage=0.0,
                framework=self.test_framework
            )

    async def _generate_function_tests(self, func_info: Dict, content: str, file_path: str) -> List[TestCase]:
        """Generate test cases for a specific function"""
        test_cases = []
        
        # Generate happy path test
        happy_path = self._generate_happy_path_test(func_info)
        test_cases.append(happy_path)
        
        # Generate edge case tests
        edge_cases = self._generate_edge_case_tests(func_info)
        test_cases.extend(edge_cases)
        
        # Generate error condition tests
        error_tests = self._generate_error_tests(func_info)
        test_cases.extend(error_tests)
        
        # Generate boundary value tests
        boundary_tests = self._generate_boundary_tests(func_info)
        test_cases.extend(boundary_tests)
        
        return test_cases

    def _extract_functions(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract function information from AST"""
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Skip private methods (starting with _)
                if node.name.startswith('_'):
                    continue
                
                func_info = {
                    'name': node.name,
                    'args': [arg.arg for arg in node.args.args],
                    'defaults': len(node.args.defaults),
                    'returns': self._get_return_type(node),
                    'docstring': ast.get_docstring(node),
                    'line_number': node.lineno,
                    'is_async': isinstance(node, ast.AsyncFunctionDef),
                    'decorators': [self._get_decorator_name(dec) for dec in node.decorator_list],
                    'complexity': self._calculate_complexity(node)
                }
                
                functions.append(func_info)
        
        return functions

    def _generate_happy_path_test(self, func_info: Dict[str, Any]) -> TestCase:
        """Generate a happy path test case"""
        function_name = func_info['name']
        args = func_info['args']
        
        # Generate sample arguments
        sample_args = self._generate_sample_arguments(args)
        function_call = f"{function_name}({', '.join(sample_args)})"
        
        # Generate basic assertion
        if func_info['returns']:
            assertion = f"assert result is not None"
        else:
            assertion = f"assert True  # Function executed successfully"
        
        test_code = self.test_templates[self.test_framework]['function_test'].format(
            function_name=function_name,
            test_type='happy_path',
            description='normal operation with valid inputs',
            setup=self._generate_test_setup(func_info),
            function_call=function_call,
            assertions=assertion
        )
        
        return TestCase(
            name=f"test_{function_name}_happy_path",
            description=f"Test {function_name} with valid inputs",
            test_type='unit',
            test_code=test_code,
            assertions=[assertion],
            dependencies=[]
        )

    def _generate_edge_case_tests(self, func_info: Dict[str, Any]) -> List[TestCase]:
        """Generate edge case test cases"""
        test_cases = []
        function_name = func_info['name']
        args = func_info['args']
        
        # Generate tests for boundary values
        for arg_name in args:
            if arg_name in ['self', 'cls']:  # Skip class/instance references
                continue
                
            edge_values = self._get_edge_values_for_parameter(arg_name)
            
            for edge_value in edge_values:
                # Create test arguments with edge value
                test_args = self._generate_sample_arguments(args)
                arg_index = args.index(arg_name)
                if arg_index < len(test_args):
                    test_args[arg_index] = edge_value
                
                function_call = f"{function_name}({', '.join(test_args)})"
                
                test_code = self.test_templates[self.test_framework]['function_test'].format(
                    function_name=function_name,
                    test_type=f'edge_case_{arg_name}_{edge_value}',
                    description=f'edge case with {arg_name}={edge_value}',
                    setup=self._generate_test_setup(func_info),
                    function_call=function_call,
                    assertions="assert result is not None  # Edge case handled"
                )
                
                test_case = TestCase(
                    name=f"test_{function_name}_edge_case_{arg_name}_{edge_value}",
                    description=f"Test {function_name} with edge case {arg_name}={edge_value}",
                    test_type='edge_case',
                    test_code=test_code,
                    assertions=["assert result is not None"],
                    dependencies=[]
                )
                test_cases.append(test_case)
        
        return test_cases

    def _generate_error_tests(self, func_info: Dict[str, Any]) -> List[TestCase]:
        """Generate error condition test cases"""
        test_cases = []
        function_name = func_info['name']
        args = func_info['args']
        
        error_conditions = [
            ('None', 'TypeError'),
            ('invalid_type', 'TypeError'),
            ('empty_string', 'ValueError'),
            ('negative_number', 'ValueError')
        ]
        
        for error_value, expected_exception in error_conditions:
            if not args or len(args) <= 1:  # Skip if no meaningful args
                continue
                
            test_args = self._generate_sample_arguments(args)
            if len(test_args) > 1:  # Replace first non-self argument
                test_args[1] = error_value
            
            function_call = f"{function_name}({', '.join(test_args)})"
            
            test_code = f'''def test_{function_name}_error_{error_value}():
    """Test {function_name} raises {expected_exception} with {error_value}."""
    with pytest.raises({expected_exception}):
        {function_call}'''
            
            test_case = TestCase(
                name=f"test_{function_name}_error_{error_value}",
                description=f"Test {function_name} raises {expected_exception} with {error_value}",
                test_type='error_case',
                test_code=test_code,
                assertions=[f"pytest.raises({expected_exception})"],
                dependencies=['pytest']
            )
            test_cases.append(test_case)
        
        return test_cases

    def _generate_boundary_tests(self, func_info: Dict[str, Any]) -> List[TestCase]:
        """Generate boundary value test cases"""
        test_cases = []
        function_name = func_info['name']
        
        # Common boundary values
        boundary_values = [
            ('zero', '0'),
            ('one', '1'),
            ('negative_one', '-1'),
            ('empty_list', '[]'),
            ('empty_string', '""')
        ]
        
        for boundary_name, boundary_value in boundary_values:
            test_code = f'''def test_{function_name}_boundary_{boundary_name}():
    """Test {function_name} with boundary value {boundary_value}."""
    result = {function_name}({boundary_value})
    assert result is not None  # Boundary case handled'''
            
            test_case = TestCase(
                name=f"test_{function_name}_boundary_{boundary_name}",
                description=f"Test {function_name} with boundary value {boundary_value}",
                test_type='edge_case',
                test_code=test_code,
                assertions=["assert result is not None"],
                dependencies=[]
            )
            test_cases.append(test_case)
        
        return test_cases

    def _generate_sample_arguments(self, args: List[str]) -> List[str]:
        """Generate sample arguments for function call"""
        sample_args = []
        
        for arg in args:
            if arg in ['self', 'cls']:
                continue  # Skip class/instance references
            elif 'id' in arg.lower():
                sample_args.append('1')
            elif 'name' in arg.lower():
                sample_args.append('"test_name"')
            elif 'count' in arg.lower() or 'num' in arg.lower():
                sample_args.append('10')
            elif 'list' in arg.lower() or 'items' in arg.lower():
                sample_args.append('[1, 2, 3]')
            elif 'dict' in arg.lower() or 'data' in arg.lower():
                sample_args.append('{"key": "value"}')
            elif 'bool' in arg.lower() or 'flag' in arg.lower():
                sample_args.append('True')
            else:
                sample_args.append('"test_value"')
        
        return sample_args

    def _get_edge_values_for_parameter(self, param_name: str) -> List[str]:
        """Get edge values for a parameter based on its name"""
        if 'id' in param_name.lower():
            return ['0', '1', '-1']
        elif 'count' in param_name.lower() or 'num' in param_name.lower():
            return ['0', '1', '100', '-1']
        elif 'name' in param_name.lower() or 'str' in param_name.lower():
            return ['""', '"a"', '"very_long_string"']
        elif 'list' in param_name.lower():
            return ['[]', '[1]', '[1, 2, 3]']
        else:
            return ['None', '""', '0']

    def _generate_test_setup(self, func_info: Dict[str, Any]) -> str:
        """Generate setup code for tests"""
        setup_lines = []
        
        # Mock external dependencies if needed
        if 'request' in str(func_info.get('args', [])):
            setup_lines.append("mock_request = Mock()")
        
        if 'database' in str(func_info.get('args', [])):
            setup_lines.append("mock_db = Mock()")
        
        return '\n    '.join(setup_lines) if setup_lines else "pass"

    def _generate_setup_code(self, file_path: str) -> str:
        """Generate setup code for the entire test suite"""
        file_name = Path(file_path).stem
        
        setup_code = f'''import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from {file_name} import *'''
        
        return setup_code

    def _generate_teardown_code(self) -> str:
        """Generate teardown code for cleanup"""
        return '''# Cleanup code would go here if needed'''

    def _estimate_coverage(self, test_cases: List[TestCase], functions: List[Dict]) -> float:
        """Estimate test coverage percentage"""
        if not functions:
            return 0.0
        
        # Simple heuristic: coverage based on test types
        coverage_weights = {
            'unit': 0.3,
            'edge_case': 0.2,
            'error_case': 0.3,
            'integration': 0.2
        }
        
        total_coverage = 0.0
        for test_case in test_cases:
            total_coverage += coverage_weights.get(test_case.test_type, 0.1)
        
        # Normalize by number of functions
        average_coverage = total_coverage / len(functions)
        
        return min(average_coverage * 100, 100.0)

    def _get_return_type(self, node: ast.FunctionDef) -> Optional[str]:
        """Extract return type from function annotation"""
        if node.returns:
            return ast.unparse(node.returns) if hasattr(ast, 'unparse') else 'Unknown'
        return None

    def _get_decorator_name(self, decorator: ast.expr) -> str:
        """Extract decorator name"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return decorator.attr
        else:
            return 'unknown_decorator'

    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of function"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity

    async def write_test_file(self, test_suite: TestSuite, output_path: str = None) -> str:
        """Write generated tests to a file"""
        if not output_path:
            base_name = Path(test_suite.target_file).stem
            output_path = f"test_{base_name}.py"
        
        # Generate complete test file content
        content_parts = [
            test_suite.setup_code or "",
            "",
            ""
        ]
        
        # Add test cases
        for test_case in test_suite.test_cases:
            content_parts.append(test_case.test_code)
            content_parts.append("")
        
        # Add teardown if present
        if test_suite.teardown_code:
            content_parts.append(test_suite.teardown_code)
        
        content = "\n".join(content_parts)
        
        # Validate generated test code
        try:
            ast.parse(content)
        except SyntaxError as e:
            self.logger.error(f"Generated test code has syntax errors: {e}")
            return ""
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.logger.info(f"Generated {len(test_suite.test_cases)} tests in {output_path}")
        return output_path


if __name__ == "__main__":
    # Test the test generator
    async def test_generator():
        config = {
            'project_root': '.',
            'test_framework': 'pytest'
        }
        
        generator = TestGenerator(config)
        
        # Create test subject
        test_subject = '''
def calculate_factorial(n):
    """Calculate factorial of a number."""
    if n < 0:
        raise ValueError("Negative numbers not allowed")
    if n == 0 or n == 1:
        return 1
    return n * calculate_factorial(n - 1)

def divide_numbers(a, b):
    """Divide two numbers."""
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b

class Calculator:
    """Simple calculator class."""
    
    def add(self, a, b):
        """Add two numbers."""
        return a + b
    
    def multiply(self, a, b):
        """Multiply two numbers."""
        return a * b
'''
        
        with open('test_subject.py', 'w') as f:
            f.write(test_subject)
        
        # Generate tests
        test_suite = await generator.generate_tests('test_subject.py')
        
        print("🧪 Test Generator Results")
        print("=" * 50)
        print(f"Target: {test_suite.target_file}")
        print(f"Framework: {test_suite.framework}")
        print(f"Test Cases: {len(test_suite.test_cases)}")
        print(f"Estimated Coverage: {test_suite.coverage_percentage:.1f}%")
        
        print("\nGenerated Test Cases:")
        for i, test_case in enumerate(test_suite.test_cases, 1):
            print(f"{i}. {test_case.name}")
            print(f"   Type: {test_case.test_type}")
            print(f"   Description: {test_case.description}")
        
        # Write test file
        test_file = await generator.write_test_file(test_suite, 'generated_tests.py')
        print(f"\n✅ Tests written to: {test_file}")
        
        # Clean up
        os.remove('test_subject.py')
        if os.path.exists('generated_tests.py'):
            os.remove('generated_tests.py')
    
    import asyncio
    asyncio.run(test_generator())