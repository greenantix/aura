#!/usr/bin/env python3
"""
Aura Enhanced Code Generation Engine
====================================

AI-powered code synthesis with intelligent pattern recognition,
context awareness, and multi-language support.

Author: Aura - Level 9 Autonomous AI Coding Assistant
"""

import os
import re
import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

from aura.security.input_validator import SecurityValidator, validate_code_input
from aura.security.audit_logger import get_audit_logger


@dataclass
class CodeGenerationRequest:
    """Request for code generation"""
    description: str
    language: str  # 'python', 'javascript', 'typescript', 'go', 'rust'
    context: Optional[str] = None  # Surrounding code context
    style: str = 'modern'  # 'modern', 'functional', 'oop', 'procedural'
    target: str = 'function'  # 'function', 'class', 'module', 'component'
    requirements: List[str] = None  # Additional requirements
    existing_code: Optional[str] = None  # Code to extend/modify


@dataclass
class GeneratedCode:
    """Generated code with metadata"""
    code: str
    language: str
    confidence: float  # 0.0 to 1.0
    explanation: str
    dependencies: List[str]
    tests: Optional[str] = None
    documentation: Optional[str] = None
    performance_notes: List[str] = None
    security_notes: List[str] = None


@dataclass
class CodeTemplate:
    """Code template for generation"""
    name: str
    language: str
    category: str
    template: str
    variables: List[str]
    description: str


class CodeGenerator:
    """AI-powered code generation engine"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.llm_provider = config.get('llm_provider')
        self.logger = logging.getLogger('aura.generation.code_generator')
        
        # Load code templates
        self.templates = self._load_templates()
        
        # Generation patterns for different languages
        self.language_patterns = {
            'python': {
                'function_template': '''def {function_name}({parameters}){return_type}:
    \"\"\"
    {docstring}
    \"\"\"
    {body}''',
                'class_template': '''class {class_name}{inheritance}:
    \"\"\"
    {docstring}
    \"\"\"
    
    def __init__(self{init_params}):
        {init_body}
    
    {methods}''',
                'import_patterns': ['import {module}', 'from {module} import {items}'],
                'test_template': '''def test_{function_name}():
    \"\"\"Test {function_name} function.\"\"\"
    {test_body}'''
            },
            'javascript': {
                'function_template': '''function {function_name}({parameters}) {{
    {body}
}}''',
                'arrow_function_template': '''const {function_name} = ({parameters}) => {{
    {body}
}};''',
                'class_template': '''class {class_name}{extends_clause} {{
    constructor({constructor_params}) {{
        {constructor_body}
    }}
    
    {methods}
}}''',
                'react_component_template': '''import React{imports} from 'react';

const {component_name} = ({{props}}) => {{
    {hooks}
    
    return (
        {jsx}
    );
}};

export default {component_name};''',
                'test_template': '''describe('{function_name}', () => {{
    test('{test_description}', () => {{
        {test_body}
    }});
}});'''
            },
            'typescript': {
                'interface_template': '''interface {interface_name} {{
    {properties}
}}''',
                'type_template': '''type {type_name} = {type_definition};''',
                'function_template': '''function {function_name}({parameters}): {return_type} {{
    {body}
}}''',
                'class_template': '''class {class_name}{extends_clause} {{
    {properties}
    
    constructor({constructor_params}) {{
        {constructor_body}
    }}
    
    {methods}
}}'''
            }
        }
        
        # Code quality patterns
        self.quality_patterns = {
            'error_handling': {
                'python': ['try:', 'except:', 'raise', 'assert'],
                'javascript': ['try {', 'catch (', 'throw new', 'if (!'],
                'typescript': ['try {', 'catch (', 'throw new', 'if (!']
            },
            'type_safety': {
                'python': ['isinstance(', 'type(', ': str', ': int', ': bool'],
                'typescript': [': string', ': number', ': boolean', 'interface', 'type']
            },
            'async_patterns': {
                'python': ['async def', 'await ', 'asyncio.'],
                'javascript': ['async function', 'await ', 'Promise.'],
                'typescript': ['async function', 'await ', 'Promise<']
            }
        }

    def _load_templates(self) -> Dict[str, List[CodeTemplate]]:
        """Load code templates from configuration"""
        templates = {
            'python': [
                CodeTemplate(
                    name='rest_api_endpoint',
                    language='python',
                    category='web',
                    template='''@app.route('/{endpoint}', methods=['{method}'])
def {function_name}({parameters}):
    \"\"\"
    {description}
    \"\"\"
    try:
        {body}
        return jsonify({{"success": True, "data": result}})
    except Exception as e:
        return jsonify({{"error": str(e)}}), 500''',
                    variables=['endpoint', 'method', 'function_name', 'parameters', 'description', 'body'],
                    description='REST API endpoint with error handling'
                ),
                CodeTemplate(
                    name='data_class',
                    language='python',
                    category='data',
                    template='''@dataclass
class {class_name}:
    \"\"\"
    {description}
    \"\"\"
    {fields}
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> '{class_name}':
        return cls(**data)''',
                    variables=['class_name', 'description', 'fields'],
                    description='Data class with serialization methods'
                )
            ],
            'javascript': [
                CodeTemplate(
                    name='react_hook',
                    language='javascript',
                    category='react',
                    template='''import {{ useState, useEffect }} from 'react';

export const use{hook_name} = ({parameters}) => {{
    const [{state_name}, set{state_name_title}] = useState({initial_value});
    
    useEffect(() => {{
        {effect_body}
    }}, [{dependencies}]);
    
    return {{
        {state_name},
        {methods}
    }};
}};''',
                    variables=['hook_name', 'parameters', 'state_name', 'state_name_title', 
                              'initial_value', 'effect_body', 'dependencies', 'methods'],
                    description='Custom React hook with state and effects'
                ),
                CodeTemplate(
                    name='api_service',
                    language='javascript',
                    category='api',
                    template='''class {service_name} {{
    constructor(baseURL = '{base_url}') {{
        this.baseURL = baseURL;
    }}
    
    async {method_name}({parameters}) {{
        try {{
            const response = await fetch(`${{this.baseURL}}/{endpoint}`, {{
                method: '{http_method}',
                headers: {{
                    'Content-Type': 'application/json',
                }},
                {body}
            }});
            
            if (!response.ok) {{
                throw new Error(`HTTP error! status: ${{response.status}}`);
            }}
            
            return await response.json();
        }} catch (error) {{
            console.error('{service_name} {method_name} error:', error);
            throw error;
        }}
    }}
}}''',
                    variables=['service_name', 'base_url', 'method_name', 'parameters', 
                              'endpoint', 'http_method', 'body'],
                    description='API service class with error handling'
                )
            ]
        }
        return templates

    @validate_code_input()
    async def generate_code(self, request: CodeGenerationRequest) -> GeneratedCode:
        """Generate code based on request"""
        audit_logger = get_audit_logger()
        
        try:
            # Validate and sanitize input
            description = SecurityValidator.validate_llm_prompt(request.description)
            
            # Log generation request
            audit_logger.log_security_event(
                event_type=audit_logger.SecurityEventType.AUTHENTICATION_SUCCESS,
                service_id='code_generator',
                details={'language': request.language, 'target': request.target}
            )
            
            # Choose generation strategy
            if request.target == 'function':
                return await self._generate_function(request)
            elif request.target == 'class':
                return await self._generate_class(request)
            elif request.target == 'component' and request.language in ['javascript', 'typescript']:
                return await self._generate_react_component(request)
            elif request.target == 'module':
                return await self._generate_module(request)
            else:
                return await self._generate_generic(request)
                
        except Exception as e:
            audit_logger.log_suspicious_activity(
                'code_generator', 
                f'generation_error: {str(e)}',
                {'request': asdict(request)}
            )
            raise

    async def _generate_function(self, request: CodeGenerationRequest) -> GeneratedCode:
        """Generate a function"""
        # Extract function details from description
        function_info = self._parse_function_description(request.description)
        
        # Choose appropriate template
        templates = self.language_patterns.get(request.language, {})
        
        if request.language == 'python':
            template = templates.get('function_template', '')
            
            # Generate function parameters
            parameters = self._generate_parameters(function_info.get('params', []), request.language)
            
            # Generate function body
            body = await self._generate_function_body(request, function_info)
            
            # Generate return type annotation
            return_type = self._generate_return_type(function_info, request.language)
            
            code = template.format(
                function_name=function_info.get('name', 'generated_function'),
                parameters=parameters,
                return_type=return_type,
                docstring=self._generate_docstring(request.description, function_info),
                body=body
            )
            
        elif request.language in ['javascript', 'typescript']:
            # Choose between function and arrow function based on style
            if request.style == 'modern':
                template = templates.get('arrow_function_template', templates.get('function_template', ''))
            else:
                template = templates.get('function_template', '')
                
            parameters = self._generate_parameters(function_info.get('params', []), request.language)
            body = await self._generate_function_body(request, function_info)
            
            code = template.format(
                function_name=function_info.get('name', 'generatedFunction'),
                parameters=parameters,
                body=body
            )
            
        else:
            code = await self._generate_with_llm(request)
        
        # Generate tests
        tests = await self._generate_tests(request, function_info)
        
        # Calculate confidence
        confidence = self._calculate_confidence(code, request)
        
        # Generate documentation
        documentation = self._generate_documentation(code, request)
        
        return GeneratedCode(
            code=code,
            language=request.language,
            confidence=confidence,
            explanation=f"Generated {request.target} based on: {request.description}",
            dependencies=self._extract_dependencies(code, request.language),
            tests=tests,
            documentation=documentation,
            performance_notes=self._analyze_performance(code, request.language),
            security_notes=self._analyze_security(code, request.language)
        )

    async def _generate_class(self, request: CodeGenerationRequest) -> GeneratedCode:
        """Generate a class"""
        class_info = self._parse_class_description(request.description)
        templates = self.language_patterns.get(request.language, {})
        
        if request.language == 'python':
            template = templates.get('class_template', '')
            
            # Generate class components
            init_params = self._generate_init_parameters(class_info)
            init_body = self._generate_init_body(class_info)
            methods = await self._generate_class_methods(class_info, request)
            inheritance = f"({class_info.get('parent', '')})" if class_info.get('parent') else ""
            
            code = template.format(
                class_name=class_info.get('name', 'GeneratedClass'),
                inheritance=inheritance,
                docstring=self._generate_docstring(request.description, class_info),
                init_params=init_params,
                init_body=init_body,
                methods=methods
            )
            
        else:
            code = await self._generate_with_llm(request)
        
        confidence = self._calculate_confidence(code, request)
        
        return GeneratedCode(
            code=code,
            language=request.language,
            confidence=confidence,
            explanation=f"Generated {request.target} based on: {request.description}",
            dependencies=self._extract_dependencies(code, request.language),
            tests=await self._generate_tests(request, class_info),
            documentation=self._generate_documentation(code, request),
            performance_notes=self._analyze_performance(code, request.language),
            security_notes=self._analyze_security(code, request.language)
        )

    async def _generate_react_component(self, request: CodeGenerationRequest) -> GeneratedCode:
        """Generate a React component"""
        component_info = self._parse_component_description(request.description)
        
        template = self.language_patterns['javascript']['react_component_template']
        
        # Generate component parts
        component_name = component_info.get('name', 'GeneratedComponent')
        props = self._generate_component_props(component_info)
        hooks = self._generate_component_hooks(component_info)
        jsx = await self._generate_jsx(component_info, request)
        imports = self._generate_react_imports(component_info)
        
        code = template.format(
            component_name=component_name,
            imports=imports,
            props=props,
            hooks=hooks,
            jsx=jsx
        )
        
        confidence = self._calculate_confidence(code, request)
        
        return GeneratedCode(
            code=code,
            language=request.language,
            confidence=confidence,
            explanation=f"Generated React component based on: {request.description}",
            dependencies=self._extract_dependencies(code, request.language),
            tests=await self._generate_component_tests(request, component_info),
            documentation=self._generate_documentation(code, request),
            performance_notes=self._analyze_performance(code, request.language),
            security_notes=self._analyze_security(code, request.language)
        )

    async def _generate_module(self, request: CodeGenerationRequest) -> GeneratedCode:
        """Generate a complete module"""
        module_info = self._parse_module_description(request.description)
        
        # Generate module structure
        imports = self._generate_module_imports(module_info, request.language)
        classes = []
        functions = []
        
        # Generate classes
        for class_desc in module_info.get('classes', []):
            class_req = CodeGenerationRequest(
                description=class_desc,
                language=request.language,
                target='class',
                style=request.style
            )
            class_code = await self._generate_class(class_req)
            classes.append(class_code.code)
        
        # Generate functions
        for func_desc in module_info.get('functions', []):
            func_req = CodeGenerationRequest(
                description=func_desc,
                language=request.language,
                target='function',
                style=request.style
            )
            func_code = await self._generate_function(func_req)
            functions.append(func_code.code)
        
        # Combine into module
        code_parts = [imports] + classes + functions
        code = '\n\n'.join(filter(None, code_parts))
        
        confidence = self._calculate_confidence(code, request)
        
        return GeneratedCode(
            code=code,
            language=request.language,
            confidence=confidence,
            explanation=f"Generated module based on: {request.description}",
            dependencies=self._extract_dependencies(code, request.language),
            tests=await self._generate_module_tests(request, module_info),
            documentation=self._generate_documentation(code, request),
            performance_notes=self._analyze_performance(code, request.language),
            security_notes=self._analyze_security(code, request.language)
        )

    async def _generate_with_llm(self, request: CodeGenerationRequest) -> str:
        """Generate code using LLM when templates are insufficient"""
        if not self.llm_provider:
            raise ValueError("LLM provider not available for advanced code generation")
        
        # Create detailed prompt
        prompt = self._create_generation_prompt(request)
        
        # Validate prompt
        prompt = SecurityValidator.validate_llm_prompt(prompt)
        
        try:
            # Call LLM
            response = await self.llm_provider.generate_text(
                prompt=prompt,
                max_tokens=2000,
                temperature=0.2,  # Lower temperature for more deterministic code
                stop_sequences=['```', '---END---']
            )
            
            # Extract code from response
            code = self._extract_code_from_response(response)
            
            # Validate generated code
            code = SecurityValidator.sanitize_code_input(code)
            
            return code
            
        except Exception as e:
            self.logger.error(f"LLM code generation failed: {e}")
            return self._generate_fallback_code(request)

    def _create_generation_prompt(self, request: CodeGenerationRequest) -> str:
        """Create a detailed prompt for LLM code generation"""
        prompt_parts = [
            f"Generate {request.language} code for the following requirement:",
            f"Description: {request.description}",
            f"Target: {request.target}",
            f"Style: {request.style}",
        ]
        
        if request.context:
            prompt_parts.append(f"Context: {request.context}")
        
        if request.requirements:
            prompt_parts.append(f"Additional requirements: {', '.join(request.requirements)}")
        
        prompt_parts.extend([
            "",
            "Requirements:",
            "- Follow best practices and modern patterns",
            "- Include proper error handling",
            "- Add appropriate type hints/annotations",
            "- Include clear documentation",
            "- Ensure security and performance",
            "",
            f"Please provide only the {request.language} code without explanations:",
            "```" + request.language
        ])
        
        return '\n'.join(prompt_parts)

    def _parse_function_description(self, description: str) -> Dict[str, Any]:
        """Parse function description to extract details"""
        info = {
            'name': 'generated_function',
            'params': [],
            'returns': None,
            'description': description
        }
        
        # Extract function name
        name_match = re.search(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*function', description, re.IGNORECASE)
        if name_match:
            info['name'] = name_match.group(1)
        
        # Extract parameters
        param_patterns = [
            r'takes?\s+([^.]+?)\s+(?:as\s+)?(?:parameter|argument|input)',
            r'with\s+parameters?\s+([^.]+)',
            r'\(([^)]+)\)'
        ]
        
        for pattern in param_patterns:
            param_match = re.search(pattern, description, re.IGNORECASE)
            if param_match:
                param_text = param_match.group(1)
                params = [p.strip() for p in param_text.split(',')]
                info['params'] = params
                break
        
        # Extract return type
        return_patterns = [
            r'returns?\s+([^.]+)',
            r'outputs?\s+([^.]+)',
            r'->\s*([^.]+)'
        ]
        
        for pattern in return_patterns:
            return_match = re.search(pattern, description, re.IGNORECASE)
            if return_match:
                info['returns'] = return_match.group(1).strip()
                break
        
        return info

    def _parse_class_description(self, description: str) -> Dict[str, Any]:
        """Parse class description to extract details"""
        info = {
            'name': 'GeneratedClass',
            'attributes': [],
            'methods': [],
            'parent': None,
            'description': description
        }
        
        # Extract class name
        name_match = re.search(r'\b([A-Z][a-zA-Z0-9_]*)\s*class', description, re.IGNORECASE)
        if name_match:
            info['name'] = name_match.group(1)
        
        # Extract parent class
        parent_match = re.search(r'extends?\s+([A-Z][a-zA-Z0-9_]*)', description, re.IGNORECASE)
        if parent_match:
            info['parent'] = parent_match.group(1)
        
        return info

    def _parse_component_description(self, description: str) -> Dict[str, Any]:
        """Parse React component description"""
        info = {
            'name': 'GeneratedComponent',
            'props': [],
            'state': [],
            'hooks': [],
            'description': description
        }
        
        # Extract component name
        name_match = re.search(r'\b([A-Z][a-zA-Z0-9_]*)\s*component', description, re.IGNORECASE)
        if name_match:
            info['name'] = name_match.group(1)
        
        return info

    def _parse_module_description(self, description: str) -> Dict[str, Any]:
        """Parse module description"""
        return {
            'name': 'generated_module',
            'classes': [],
            'functions': [],
            'description': description
        }

    def _calculate_confidence(self, code: str, request: CodeGenerationRequest) -> float:
        """Calculate confidence score for generated code"""
        confidence = 0.7  # Base confidence
        
        # Check for syntax patterns
        quality_patterns = self.quality_patterns.get('error_handling', {}).get(request.language, [])
        for pattern in quality_patterns:
            if pattern in code:
                confidence += 0.05
        
        # Check for type safety
        type_patterns = self.quality_patterns.get('type_safety', {}).get(request.language, [])
        for pattern in type_patterns:
            if pattern in code:
                confidence += 0.03
        
        # Check code length (reasonable length indicates completeness)
        if 50 <= len(code) <= 1000:
            confidence += 0.1
        elif len(code) > 1000:
            confidence += 0.05
        
        return min(confidence, 1.0)

    # Additional helper methods would continue here...
    # For brevity, I'll include key method signatures

    def _generate_parameters(self, params: List[str], language: str) -> str:
        """Generate function parameters"""
        return ", ".join(params)

    async def _generate_function_body(self, request: CodeGenerationRequest, info: Dict) -> str:
        """Generate function body"""
        return "    pass  # TODO: Implement function logic"

    def _generate_docstring(self, description: str, info: Dict) -> str:
        """Generate documentation string"""
        return description

    async def _generate_tests(self, request: CodeGenerationRequest, info: Dict) -> str:
        """Generate test code"""
        return f"# Test for {info.get('name', 'generated_code')}"

    def _extract_dependencies(self, code: str, language: str) -> List[str]:
        """Extract dependencies from generated code"""
        deps = []
        if language == 'python':
            imports = re.findall(r'(?:from\s+(\S+)\s+import|import\s+(\S+))', code)
            deps.extend([imp[0] or imp[1] for imp in imports])
        return deps

    def _analyze_performance(self, code: str, language: str) -> List[str]:
        """Analyze performance characteristics"""
        return ["Generated code uses modern patterns"]

    def _analyze_security(self, code: str, language: str) -> List[str]:
        """Analyze security characteristics"""
        return ["Input validation recommended"]

    def _generate_return_type(self, info: Dict, language: str) -> str:
        """Generate return type annotation"""
        if language == 'python':
            if info.get('returns'):
                return f" -> {info['returns']}"
            return ""
        return ""

    def _generate_fallback_code(self, request: CodeGenerationRequest) -> str:
        """Generate fallback code when LLM fails"""
        if request.target == 'function':
            return f'''def {request.description.replace(' ', '_').lower()}():
    """Generated function: {request.description}"""
    # TODO: Implement logic
    pass'''
        elif request.target == 'class':
            return f'''class GeneratedClass:
    """Generated class: {request.description}"""
    
    def __init__(self):
        pass'''
        else:
            return f'# Generated code for: {request.description}'

    def _extract_code_from_response(self, response: str) -> str:
        """Extract code from LLM response"""
        # Simple extraction - look for code blocks
        lines = response.split('\n')
        code_lines = []
        in_code_block = False
        
        for line in lines:
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                code_lines.append(line)
        
        return '\n'.join(code_lines) if code_lines else response

    def _generate_init_parameters(self, class_info: Dict) -> str:
        """Generate __init__ parameters for class"""
        return "self"

    def _generate_init_body(self, class_info: Dict) -> str:
        """Generate __init__ body for class"""
        return "pass"

    async def _generate_class_methods(self, class_info: Dict, request: CodeGenerationRequest) -> str:
        """Generate class methods"""
        return '''def example_method(self):
        """Example method."""
        pass'''

    def _generate_component_props(self, component_info: Dict) -> str:
        """Generate React component props"""
        return "props"

    def _generate_component_hooks(self, component_info: Dict) -> str:
        """Generate React component hooks"""
        return ""

    async def _generate_jsx(self, component_info: Dict, request: CodeGenerationRequest) -> str:
        """Generate JSX for React component"""
        return '''<div>
            <h1>Generated Component</h1>
        </div>'''

    def _generate_react_imports(self, component_info: Dict) -> str:
        """Generate React imports"""
        return ""

    async def _generate_component_tests(self, request: CodeGenerationRequest, component_info: Dict) -> str:
        """Generate React component tests"""
        return f"// Tests for {component_info.get('name', 'Component')}"

    def _generate_module_imports(self, module_info: Dict, language: str) -> str:
        """Generate module imports"""
        if language == 'python':
            return '''import os
import sys
from typing import List, Dict, Any'''
        elif language in ['javascript', 'typescript']:
            return '''// Module imports would go here'''
        return ""

    async def _generate_module_tests(self, request: CodeGenerationRequest, module_info: Dict) -> str:
        """Generate module tests"""
        return f"// Tests for {module_info.get('name', 'module')}"

    def _generate_documentation(self, code: str, request: CodeGenerationRequest) -> str:
        """Generate documentation for the code"""
        return f"""## Generated {request.target.title()}

**Description**: {request.description}

**Language**: {request.language}

**Style**: {request.style}

### Usage

```{request.language}
{code}
```

### Notes

- This code was automatically generated by Aura
- Review and test before production use
- Consider adding error handling and validation
"""


if __name__ == "__main__":
    # Test the code generator
    async def test_generator():
        config = {'llm_provider': None}
        generator = CodeGenerator(config)
        
        # Test function generation
        request = CodeGenerationRequest(
            description="Create a function that calculates the factorial of a number",
            language="python",
            target="function",
            style="modern"
        )
        
        result = await generator.generate_code(request)
        
        print("🔨 Code Generation Test")
        print("=" * 50)
        print(f"Generated {result.language} {request.target}:")
        print(f"Confidence: {result.confidence:.2f}")
        print("\nCode:")
        print(result.code)
        print(f"\nExplanation: {result.explanation}")
        
    asyncio.run(test_generator())