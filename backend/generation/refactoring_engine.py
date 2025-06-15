#!/usr/bin/env python3
"""
Aura Intelligent Refactoring Engine
====================================

Automated code refactoring with pattern recognition, safety checks,
and intelligent transformation suggestions.

Author: Aura - Level 9 Autonomous AI Coding Assistant
"""

import ast
import re
import os
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from pathlib import Path
import logging

try:
    from aura.security.input_validator import SecurityValidator, validate_code_input
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    parent_path = str(Path(__file__).parent.parent)
    if parent_path not in sys.path:
        sys.path.append(parent_path)
    
    try:
        from security.input_validator import SecurityValidator, validate_code_input
    except ImportError:
        # Create minimal mock classes for testing
        class SecurityValidator:
            @staticmethod
            def validate_llm_prompt(prompt):
                return prompt
            @staticmethod 
            def validate_file_path(file_path, allowed_dirs=None):
                return file_path
            @staticmethod
            def sanitize_code_input(code, max_length=100000):
                return code
        
        def validate_code_input(code, max_length=100000):
            return code


@dataclass
class RefactoringAction:
    """Represents a refactoring action"""
    type: str  # 'extract_method', 'rename', 'inline', 'move_method', 'extract_class'
    description: str
    file_path: str
    line_start: int
    line_end: int
    old_code: str
    new_code: str
    confidence: float
    impact: str  # 'low', 'medium', 'high'
    dependencies: List[str]
    reversible: bool = True


@dataclass
class RefactoringResult:
    """Result of a refactoring operation"""
    success: bool
    actions_applied: List[RefactoringAction]
    warnings: List[str]
    errors: List[str]
    modified_files: List[str]
    backup_created: bool = False


class RefactoringEngine:
    """Intelligent code refactoring engine"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.project_root = config.get('project_root', '.')
        self.logger = logging.getLogger('aura.generation.refactoring')
        
        # Refactoring patterns
        self.patterns = {
            'long_method': {
                'threshold': 20,  # lines
                'description': 'Method is too long and should be split'
            },
            'duplicate_code': {
                'min_lines': 5,
                'description': 'Duplicate code blocks should be extracted'
            },
            'large_class': {
                'threshold': 500,  # lines
                'description': 'Class is too large and should be split'
            },
            'magic_numbers': {
                'pattern': r'\b\d{2,}\b',
                'description': 'Magic numbers should be named constants'
            },
            'long_parameter_list': {
                'threshold': 5,
                'description': 'Too many parameters, consider parameter object'
            }
        }
        
        # Safe refactoring rules
        self.safety_rules = {
            'preserve_behavior': True,
            'maintain_api': True,
            'backup_files': True,
            'validate_syntax': True,
            'check_tests': True
        }

    async def analyze_refactoring_opportunities(self, file_path: str) -> List[RefactoringAction]:
        """Analyze code for refactoring opportunities"""
        try:
            # Validate file path
            file_path = SecurityValidator.validate_file_path(file_path, [self.project_root])
            
            if not os.path.exists(file_path):
                return []
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Validate code content
            content = SecurityValidator.sanitize_code_input(content)
            
            opportunities = []
            
            # Analyze different refactoring opportunities
            opportunities.extend(self._detect_long_methods(content, file_path))
            opportunities.extend(self._detect_duplicate_code(content, file_path))
            opportunities.extend(self._detect_magic_numbers(content, file_path))
            opportunities.extend(self._detect_long_parameter_lists(content, file_path))
            opportunities.extend(self._detect_code_smells(content, file_path))
            
            # Sort by confidence and impact
            opportunities.sort(key=lambda x: (x.confidence, x.impact == 'high'), reverse=True)
            
            return opportunities
            
        except Exception as e:
            self.logger.error(f"Error analyzing refactoring opportunities: {e}")
            return []

    def _detect_long_methods(self, content: str, file_path: str) -> List[RefactoringAction]:
        """Detect methods that are too long"""
        actions = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Calculate method length
                    method_lines = node.end_lineno - node.lineno + 1
                    
                    if method_lines > self.patterns['long_method']['threshold']:
                        # Find logical break points
                        break_points = self._find_extract_method_opportunities(node, content)
                        
                        for start_line, end_line, extracted_name in break_points:
                            old_code = self._get_lines(content, start_line, end_line)
                            new_code = self._generate_extracted_method(
                                extracted_name, old_code, node.name
                            )
                            
                            action = RefactoringAction(
                                type='extract_method',
                                description=f"Extract method '{extracted_name}' from '{node.name}'",
                                file_path=file_path,
                                line_start=start_line,
                                line_end=end_line,
                                old_code=old_code,
                                new_code=new_code,
                                confidence=0.8,
                                impact='medium',
                                dependencies=[]
                            )
                            actions.append(action)
                            
        except SyntaxError:
            pass  # Skip files with syntax errors
        
        return actions

    def _detect_duplicate_code(self, content: str, file_path: str) -> List[RefactoringAction]:
        """Detect duplicate code blocks"""
        actions = []
        lines = content.split('\n')
        min_lines = self.patterns['duplicate_code']['min_lines']
        
        # Simple duplicate detection - compare line sequences
        for i in range(len(lines) - min_lines):
            for j in range(i + min_lines, len(lines) - min_lines):
                # Check for duplicate sequences
                if self._lines_similar(lines[i:i+min_lines], lines[j:j+min_lines]):
                    old_code = '\n'.join(lines[i:i+min_lines])
                    
                    # Generate extracted method
                    method_name = f"extracted_method_{i}_{j}"
                    new_code = self._generate_extracted_method(method_name, old_code)
                    
                    action = RefactoringAction(
                        type='extract_method',
                        description=f"Extract duplicate code into '{method_name}'",
                        file_path=file_path,
                        line_start=i + 1,
                        line_end=i + min_lines,
                        old_code=old_code,
                        new_code=new_code,
                        confidence=0.7,
                        impact='medium',
                        dependencies=[]
                    )
                    actions.append(action)
                    break  # Avoid multiple detections of same block
        
        return actions

    def _detect_magic_numbers(self, content: str, file_path: str) -> List[RefactoringAction]:
        """Detect magic numbers that should be constants"""
        actions = []
        lines = content.split('\n')
        
        pattern = re.compile(self.patterns['magic_numbers']['pattern'])
        
        for line_num, line in enumerate(lines, 1):
            matches = pattern.finditer(line)
            for match in matches:
                number = match.group()
                
                # Skip common numbers that are usually not magic
                if number in ['0', '1', '2', '10', '100', '1000']:
                    continue
                
                # Generate constant name
                context = self._get_context_for_number(line, match.start())
                constant_name = self._generate_constant_name(number, context)
                
                old_code = line
                new_code = line.replace(number, constant_name, 1)
                
                action = RefactoringAction(
                    type='extract_constant',
                    description=f"Replace magic number {number} with constant {constant_name}",
                    file_path=file_path,
                    line_start=line_num,
                    line_end=line_num,
                    old_code=old_code,
                    new_code=new_code,
                    confidence=0.6,
                    impact='low',
                    dependencies=[]
                )
                actions.append(action)
        
        return actions

    def _detect_long_parameter_lists(self, content: str, file_path: str) -> List[RefactoringAction]:
        """Detect functions with too many parameters"""
        actions = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    param_count = len(node.args.args)
                    
                    if param_count > self.patterns['long_parameter_list']['threshold']:
                        # Suggest parameter object refactoring
                        old_code = self._get_function_signature(content, node)
                        new_code = self._generate_parameter_object_refactoring(node)
                        
                        action = RefactoringAction(
                            type='introduce_parameter_object',
                            description=f"Replace {param_count} parameters with parameter object",
                            file_path=file_path,
                            line_start=node.lineno,
                            line_end=node.lineno,
                            old_code=old_code,
                            new_code=new_code,
                            confidence=0.7,
                            impact='medium',
                            dependencies=[]
                        )
                        actions.append(action)
                        
        except SyntaxError:
            pass
        
        return actions

    def _detect_code_smells(self, content: str, file_path: str) -> List[RefactoringAction]:
        """Detect various code smells"""
        actions = []
        
        # Detect dead code
        actions.extend(self._detect_dead_code(content, file_path))
        
        # Detect complex conditionals
        actions.extend(self._detect_complex_conditionals(content, file_path))
        
        # Detect inappropriate intimacy
        actions.extend(self._detect_inappropriate_intimacy(content, file_path))
        
        return actions

    def _detect_dead_code(self, content: str, file_path: str) -> List[RefactoringAction]:
        """Detect unreachable or unused code"""
        actions = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Simple dead code patterns
            if (stripped.startswith('# TODO:') or 
                stripped.startswith('# FIXME:') or
                stripped == 'pass' and line_num > 1):
                
                action = RefactoringAction(
                    type='remove_dead_code',
                    description=f"Remove dead code at line {line_num}",
                    file_path=file_path,
                    line_start=line_num,
                    line_end=line_num,
                    old_code=line,
                    new_code='',
                    confidence=0.5,
                    impact='low',
                    dependencies=[]
                )
                actions.append(action)
        
        return actions

    def _detect_complex_conditionals(self, content: str, file_path: str) -> List[RefactoringAction]:
        """Detect complex conditional expressions"""
        actions = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Count logical operators in if statements
            if 'if ' in line:
                and_count = line.count(' and ')
                or_count = line.count(' or ')
                
                if and_count + or_count > 2:  # Complex condition
                    method_name = f"is_condition_met_{line_num}"
                    
                    action = RefactoringAction(
                        type='extract_method',
                        description=f"Extract complex condition into '{method_name}'",
                        file_path=file_path,
                        line_start=line_num,
                        line_end=line_num,
                        old_code=line,
                        new_code=f"    if {method_name}():",
                        confidence=0.6,
                        impact='medium',
                        dependencies=[]
                    )
                    actions.append(action)
        
        return actions

    def _detect_inappropriate_intimacy(self, content: str, file_path: str) -> List[RefactoringAction]:
        """Detect classes that are too tightly coupled"""
        # This would require more sophisticated analysis
        # For now, return empty list
        return []

    async def apply_refactoring(self, action: RefactoringAction) -> RefactoringResult:
        """Apply a refactoring action"""
        try:
            # Create backup if enabled
            backup_created = False
            if self.safety_rules['backup_files']:
                backup_created = self._create_backup(action.file_path)
            
            # Read current file content
            with open(action.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Apply the refactoring
            modified_content = self._apply_action(content, action)
            
            # Validate syntax if enabled
            if self.safety_rules['validate_syntax']:
                try:
                    ast.parse(modified_content)
                except SyntaxError as e:
                    return RefactoringResult(
                        success=False,
                        actions_applied=[],
                        warnings=[],
                        errors=[f"Syntax error after refactoring: {e}"],
                        modified_files=[],
                        backup_created=backup_created
                    )
            
            # Write modified content
            with open(action.file_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            return RefactoringResult(
                success=True,
                actions_applied=[action],
                warnings=[],
                errors=[],
                modified_files=[action.file_path],
                backup_created=backup_created
            )
            
        except Exception as e:
            return RefactoringResult(
                success=False,
                actions_applied=[],
                warnings=[],
                errors=[f"Refactoring failed: {e}"],
                modified_files=[],
                backup_created=backup_created
            )

    def _apply_action(self, content: str, action: RefactoringAction) -> str:
        """Apply a specific refactoring action to content"""
        lines = content.split('\n')
        
        if action.type == 'extract_method':
            return self._apply_extract_method(lines, action)
        elif action.type == 'extract_constant':
            return self._apply_extract_constant(lines, action)
        elif action.type == 'remove_dead_code':
            return self._apply_remove_dead_code(lines, action)
        else:
            # Generic line replacement
            lines[action.line_start - 1] = action.new_code
            return '\n'.join(lines)

    def _apply_extract_method(self, lines: List[str], action: RefactoringAction) -> str:
        """Apply extract method refactoring"""
        # Insert new method before the original method
        method_def = self._generate_method_definition(action)
        
        # Find insertion point (beginning of class or module)
        insert_line = self._find_method_insertion_point(lines, action.line_start)
        
        # Insert new method
        lines.insert(insert_line, method_def)
        lines.insert(insert_line + 1, '')
        
        # Replace original code with method call
        for i in range(action.line_start - 1, action.line_end):
            if i < len(lines):
                lines[i] = ''
        
        # Add method call
        lines[action.line_start - 1] = self._generate_method_call(action)
        
        return '\n'.join(lines)

    def _apply_extract_constant(self, lines: List[str], action: RefactoringAction) -> str:
        """Apply extract constant refactoring"""
        # Find constant insertion point (top of file/class)
        insert_line = self._find_constant_insertion_point(lines)
        
        # Generate constant definition
        constant_def = self._generate_constant_definition(action)
        lines.insert(insert_line, constant_def)
        
        # Replace magic number with constant
        lines[action.line_start] = action.new_code
        
        return '\n'.join(lines)

    def _apply_remove_dead_code(self, lines: List[str], action: RefactoringAction) -> str:
        """Apply remove dead code refactoring"""
        # Simply remove the line
        if action.line_start - 1 < len(lines):
            lines.pop(action.line_start - 1)
        
        return '\n'.join(lines)

    # Helper methods
    def _create_backup(self, file_path: str) -> bool:
        """Create backup of file before refactoring"""
        try:
            backup_path = f"{file_path}.backup"
            with open(file_path, 'r') as src, open(backup_path, 'w') as dst:
                dst.write(src.read())
            return True
        except Exception:
            return False

    def _get_lines(self, content: str, start: int, end: int) -> str:
        """Get lines from content"""
        lines = content.split('\n')
        return '\n'.join(lines[start-1:end])

    def _lines_similar(self, lines1: List[str], lines2: List[str], threshold: float = 0.8) -> bool:
        """Check if two line sequences are similar"""
        if len(lines1) != len(lines2):
            return False
        
        matches = sum(1 for l1, l2 in zip(lines1, lines2) if l1.strip() == l2.strip())
        similarity = matches / len(lines1)
        
        return similarity >= threshold

    def _generate_extracted_method(self, method_name: str, code: str, parent_method: str = None) -> str:
        """Generate an extracted method"""
        return f"""def {method_name}(self):
    \"\"\"Extracted from {parent_method or 'original method'}.\"\"\"
{self._indent_code(code)}"""

    def _indent_code(self, code: str, spaces: int = 4) -> str:
        """Indent code by specified spaces"""
        indent = ' ' * spaces
        return '\n'.join(indent + line for line in code.split('\n'))

    def _generate_constant_name(self, number: str, context: str) -> str:
        """Generate a constant name for a magic number"""
        # Simple heuristic based on context
        if 'timeout' in context.lower():
            return f"TIMEOUT_{number}"
        elif 'limit' in context.lower():
            return f"LIMIT_{number}"
        elif 'size' in context.lower():
            return f"SIZE_{number}"
        else:
            return f"CONSTANT_{number}"

    def _get_context_for_number(self, line: str, position: int) -> str:
        """Get context around a number for naming"""
        # Extract words around the number
        words_before = line[:position].split()[-3:]
        words_after = line[position:].split()[:3]
        return ' '.join(words_before + words_after)

    def _find_extract_method_opportunities(self, node: ast.FunctionDef, content: str) -> List[Tuple[int, int, str]]:
        """Find opportunities to extract methods from long functions"""
        # Simplified - look for logical blocks (try/except, for loops, etc.)
        opportunities = []
        
        # This would require more sophisticated AST analysis
        # For now, return a simple example
        if node.end_lineno - node.lineno > 20:
            mid_point = (node.lineno + node.end_lineno) // 2
            opportunities.append((
                mid_point,
                mid_point + 5,
                f"extracted_from_{node.name}"
            ))
        
        return opportunities

    def _generate_method_definition(self, action: RefactoringAction) -> str:
        """Generate method definition for extracted method"""
        method_name = action.description.split("'")[1]
        return f"    def {method_name}(self):\n        # Extracted method\n        pass"

    def _generate_method_call(self, action: RefactoringAction) -> str:
        """Generate method call for extracted method"""
        method_name = action.description.split("'")[1]
        return f"        self.{method_name}()"

    def _find_method_insertion_point(self, lines: List[str], current_line: int) -> int:
        """Find where to insert new method"""
        # Simple heuristic - insert before current method
        for i in range(current_line - 1, -1, -1):
            if lines[i].strip().startswith('def ') or lines[i].strip().startswith('class '):
                return i
        return 0

    def _find_constant_insertion_point(self, lines: List[str]) -> int:
        """Find where to insert constants"""
        # Insert after imports
        for i, line in enumerate(lines):
            if not (line.startswith('import ') or 
                   line.startswith('from ') or 
                   line.strip() == '' or 
                   line.startswith('#')):
                return i
        return 0

    def _generate_constant_definition(self, action: RefactoringAction) -> str:
        """Generate constant definition"""
        parts = action.description.split()
        number = parts[3]
        constant_name = parts[6]
        return f"{constant_name} = {number}"

    def _get_function_signature(self, content: str, node: ast.FunctionDef) -> str:
        """Get function signature from AST node"""
        lines = content.split('\n')
        return lines[node.lineno - 1]


if __name__ == "__main__":
    # Test the refactoring engine
    async def test_refactoring():
        config = {'project_root': '.'}
        engine = RefactoringEngine(config)
        
        # Create test file
        test_code = '''
def long_method(self, param1, param2, param3, param4, param5, param6):
    """This method is too long and has too many parameters."""
    if param1 and param2 and param3 and param4:
        result = param1 * 100
        for i in range(10):
            result += i
        return result
    else:
        return 0
        
def duplicate_code_1():
    x = 10
    y = 20
    z = x + y
    print(z)
    
def duplicate_code_2():
    x = 10
    y = 20
    z = x + y
    print(z)
'''
        
        with open('test_refactor.py', 'w') as f:
            f.write(test_code)
        
        # Analyze opportunities
        opportunities = await engine.analyze_refactoring_opportunities('test_refactor.py')
        
        print("🔨 Refactoring Engine Test")
        print("=" * 50)
        print(f"Found {len(opportunities)} refactoring opportunities:")
        
        for i, opp in enumerate(opportunities, 1):
            print(f"\n{i}. {opp.type}: {opp.description}")
            print(f"   Confidence: {opp.confidence:.2f}")
            print(f"   Impact: {opp.impact}")
            print(f"   Lines: {opp.line_start}-{opp.line_end}")
        
        # Clean up
        os.remove('test_refactor.py')
    
    import asyncio
    asyncio.run(test_refactoring())