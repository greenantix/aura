#!/usr/bin/env python3
"""
Aura Quick Demo Script
======================

A standalone demonstration of Aura's core capabilities without the full
microservices architecture. This showcases the key features in a simplified way.

Author: Aura - Level 9 Autonomous AI Coding Assistant
"""

import asyncio
import json
import time
import logging
import httpx
from pathlib import Path
from typing import Dict, Any, Optional, List
import ast
import os
from dataclasses import dataclass, asdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - AURA - %(levelname)s - %(message)s')
logger = logging.getLogger('aura_demo')


@dataclass
class CodeElement:
    """Represents a code element (function, class, etc.)"""
    name: str
    type: str  # 'function', 'class', 'method'
    line_number: int
    end_line: int
    docstring: Optional[str] = None
    complexity: int = 1
    parameters: List[str] = None
    returns: Optional[str] = None

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = []


@dataclass
class CodeAnalysis:
    """Results of code analysis"""
    file_path: str
    elements: List[CodeElement]
    metrics: Dict[str, Any]
    errors: List[str]
    warnings: List[str]
    timestamp: float


class SimpleASTVisitor(ast.NodeVisitor):
    """Simple AST visitor for Python code analysis"""
    
    def __init__(self):
        self.elements = []
        self.errors = []
        self.warnings = []
        self.current_class = None
        
    def visit_FunctionDef(self, node):
        """Visit function definitions"""
        try:
            # Get docstring
            docstring = None
            if (node.body and isinstance(node.body[0], ast.Expr) and 
                isinstance(node.body[0].value, ast.Constant) and 
                isinstance(node.body[0].value.value, str)):
                docstring = node.body[0].value.value
            
            # Get parameters
            parameters = [arg.arg for arg in node.args.args]
            
            # Calculate basic complexity (number of control flow statements)
            complexity = self._calculate_complexity(node)
            
            # Determine type
            element_type = 'method' if self.current_class else 'function'
            
            element = CodeElement(
                name=node.name,
                type=element_type,
                line_number=node.lineno,
                end_line=node.end_lineno or node.lineno,
                docstring=docstring,
                complexity=complexity,
                parameters=parameters
            )
            
            self.elements.append(element)
            
            # Check for issues
            if not docstring and not node.name.startswith('_'):
                self.warnings.append(f"Function '{node.name}' at line {node.lineno} lacks documentation")
            
            if complexity > 10:
                self.warnings.append(f"Function '{node.name}' at line {node.lineno} has high complexity ({complexity})")
                
        except Exception as e:
            self.errors.append(f"Error analyzing function '{node.name}': {str(e)}")
        
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        """Visit class definitions"""
        try:
            old_class = self.current_class
            self.current_class = node.name
            
            # Get docstring
            docstring = None
            if (node.body and isinstance(node.body[0], ast.Expr) and 
                isinstance(node.body[0].value, ast.Constant) and 
                isinstance(node.body[0].value.value, str)):
                docstring = node.body[0].value.value
            
            element = CodeElement(
                name=node.name,
                type='class',
                line_number=node.lineno,
                end_line=node.end_lineno or node.lineno,
                docstring=docstring
            )
            
            self.elements.append(element)
            
            # Check for issues
            if not docstring:
                self.warnings.append(f"Class '{node.name}' at line {node.lineno} lacks documentation")
            
            self.generic_visit(node)
            self.current_class = old_class
            
        except Exception as e:
            self.errors.append(f"Error analyzing class '{node.name}': {str(e)}")
    
    def _calculate_complexity(self, node):
        """Calculate cyclomatic complexity"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity


class SimpleLLMClient:
    """Simple LLM client for LM Studio"""
    
    def __init__(self, base_url: str = "http://localhost:1234"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.3) -> Optional[str]:
        """Generate response from LLM"""
        try:
            response = await self.client.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                logger.error(f"LLM request failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"LLM request error: {e}")
            return None
    
    async def check_health(self) -> bool:
        """Check if LLM is available"""
        try:
            response = await self.client.get(f"{self.base_url}/v1/models")
            return response.status_code == 200
        except:
            return False


class AuraDemo:
    """Simple Aura demonstration"""
    
    def __init__(self):
        self.llm = SimpleLLMClient()
        self.code_analyses = {}
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        self.code_vectors = None
        self.file_paths = []
        
    def print_banner(self):
        """Print Aura banner"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     ░█████╗░██╗░░░██╗██████╗░░█████╗░                       ║
║     ██╔══██╗██║░░░██║██╔══██╗██╔══██╗                       ║
║     ███████║██║░░░██║██████╔╝███████║                       ║
║     ██╔══██║██║░░░██║██╔══██╗██╔══██║                       ║
║     ██║░░██║╚██████╔╝██║░░██║██║░░██║                       ║
║     ╚═╝░░╚═╝░╚═════╝░╚═╝░░╚═╝╚═╝░░╚═╝                       ║
║                                                              ║
║         Level 9 Autonomous AI Coding Assistant              ║
║                    Quick Demo                               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    async def check_llm_connection(self) -> bool:
        """Check LLM connection"""
        print("🔍 Checking LM Studio connection...")
        if await self.llm.check_health():
            print("✅ LM Studio is running and accessible")
            return True
        else:
            print("❌ LM Studio is not accessible. Please ensure it's running on localhost:1234")
            return False
    
    def analyze_file(self, file_path: str) -> CodeAnalysis:
        """Analyze a Python file"""
        print(f"🔍 Analyzing file: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            # Parse AST
            tree = ast.parse(source_code)
            visitor = SimpleASTVisitor()
            visitor.visit(tree)
            
            # Calculate metrics
            lines = source_code.split('\n')
            metrics = {
                'lines_of_code': len([line for line in lines if line.strip() and not line.strip().startswith('#')]),
                'total_lines': len(lines),
                'functions_count': len([e for e in visitor.elements if e.type == 'function']),
                'classes_count': len([e for e in visitor.elements if e.type == 'class']),
                'methods_count': len([e for e in visitor.elements if e.type == 'method']),
                'average_complexity': np.mean([e.complexity for e in visitor.elements if e.type in ['function', 'method']]) if visitor.elements else 0,
                'documentation_coverage': len([e for e in visitor.elements if e.docstring]) / len(visitor.elements) if visitor.elements else 0
            }
            
            analysis = CodeAnalysis(
                file_path=file_path,
                elements=visitor.elements,
                metrics=metrics,
                errors=visitor.errors,
                warnings=visitor.warnings,
                timestamp=time.time()
            )
            
            self.code_analyses[file_path] = analysis
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {e}")
            return CodeAnalysis(
                file_path=file_path,
                elements=[],
                metrics={},
                errors=[str(e)],
                warnings=[],
                timestamp=time.time()
            )
    
    def scan_codebase(self, directory: str = ".") -> List[CodeAnalysis]:
        """Scan entire codebase"""
        print(f"🔍 Scanning codebase in: {directory}")
        
        analyses = []
        python_files = list(Path(directory).rglob("*.py"))
        
        print(f"Found {len(python_files)} Python files")
        
        for file_path in python_files:
            if 'venv' in str(file_path) or '__pycache__' in str(file_path):
                continue
                
            analysis = self.analyze_file(str(file_path))
            analyses.append(analysis)
        
        # Build search index
        if analyses:
            texts = []
            self.file_paths = []
            
            for analysis in analyses:
                # Create searchable text from code elements
                text_parts = []
                for element in analysis.elements:
                    text_parts.append(f"{element.name} {element.type}")
                    if element.docstring:
                        text_parts.append(element.docstring)
                
                texts.append(" ".join(text_parts))
                self.file_paths.append(analysis.file_path)
            
            if texts:
                self.code_vectors = self.vectorizer.fit_transform(texts)
        
        return analyses
    
    def find_similar_code(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find similar code using semantic search"""
        if self.code_vectors is None:
            print("❌ No codebase indexed. Please run scan first.")
            return []
        
        print(f"🔍 Searching for: '{query}'")
        
        # Vectorize query
        query_vector = self.vectorizer.transform([query])
        
        # Calculate similarities
        similarities = cosine_similarity(query_vector, self.code_vectors).flatten()
        
        # Get top results
        top_indices = similarities.argsort()[-limit:][::-1]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.1:  # Minimum similarity threshold
                results.append({
                    'file_path': self.file_paths[idx],
                    'similarity': float(similarities[idx]),
                    'analysis': self.code_analyses[self.file_paths[idx]]
                })
        
        return results
    
    async def ask_aura(self, question: str) -> Optional[str]:
        """Ask Aura a question using LLM"""
        print(f"🤖 Aura is thinking about: '{question}'")
        
        # Create context from current codebase
        context_parts = []
        if self.code_analyses:
            context_parts.append("Current codebase analysis:")
            for file_path, analysis in list(self.code_analyses.items())[:3]:  # Top 3 files
                context_parts.append(f"\nFile: {file_path}")
                context_parts.append(f"- Functions: {analysis.metrics.get('functions_count', 0)}")
                context_parts.append(f"- Classes: {analysis.metrics.get('classes_count', 0)}")
                context_parts.append(f"- Lines of code: {analysis.metrics.get('lines_of_code', 0)}")
        
        context = "\n".join(context_parts)
        
        prompt = f"""You are Aura, a Level 9 Autonomous AI Coding Assistant. You help with code analysis, development, and architecture decisions.

{context}

Question: {question}

Please provide a helpful, technical response based on the codebase analysis above."""
        
        response = await self.llm.generate(prompt, max_tokens=1500, temperature=0.3)
        return response
    
    def display_analysis(self, analysis: CodeAnalysis):
        """Display code analysis results"""
        print(f"\n📊 Analysis Results for: {analysis.file_path}")
        print("=" * 60)
        
        # Metrics
        metrics = analysis.metrics
        print(f"📈 Metrics:")
        print(f"  • Lines of code: {metrics.get('lines_of_code', 0)}")
        print(f"  • Functions: {metrics.get('functions_count', 0)}")
        print(f"  • Classes: {metrics.get('classes_count', 0)}")
        print(f"  • Methods: {metrics.get('methods_count', 0)}")
        print(f"  • Average complexity: {metrics.get('average_complexity', 0):.1f}")
        print(f"  • Documentation coverage: {metrics.get('documentation_coverage', 0):.1%}")
        
        # Elements
        if analysis.elements:
            print(f"\n🔧 Code Elements:")
            for element in analysis.elements[:10]:  # Top 10
                doc_status = "📝" if element.docstring else "❌"
                print(f"  • {element.type.title()}: {element.name} (Line {element.line_number}) {doc_status}")
        
        # Issues
        if analysis.errors:
            print(f"\n❌ Errors:")
            for error in analysis.errors:
                print(f"  • {error}")
        
        if analysis.warnings:
            print(f"\n⚠️  Warnings:")
            for warning in analysis.warnings:
                print(f"  • {warning}")
    
    def display_search_results(self, results: List[Dict[str, Any]]):
        """Display search results"""
        if not results:
            print("No similar code found")
            return
        
        print(f"\n🔍 Search Results:")
        print("=" * 60)
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['file_path']} (Similarity: {result['similarity']:.1%})")
            analysis = result['analysis']
            elements_count = len(analysis.elements)
            print(f"   Elements: {elements_count}, Lines: {analysis.metrics.get('lines_of_code', 0)}")
    
    def display_codebase_summary(self, analyses: List[CodeAnalysis]):
        """Display codebase summary"""
        if not analyses:
            print("No files analyzed")
            return
        
        print(f"\n📊 Codebase Summary:")
        print("=" * 60)
        
        total_files = len(analyses)
        total_functions = sum(a.metrics.get('functions_count', 0) for a in analyses)
        total_classes = sum(a.metrics.get('classes_count', 0) for a in analyses)
        total_lines = sum(a.metrics.get('lines_of_code', 0) for a in analyses)
        total_issues = sum(len(a.errors) + len(a.warnings) for a in analyses)
        
        print(f"📁 Files analyzed: {total_files}")
        print(f"🔧 Total functions: {total_functions}")
        print(f"📦 Total classes: {total_classes}")
        print(f"📝 Total lines of code: {total_lines}")
        print(f"⚠️  Total issues found: {total_issues}")
        
        # Top files by complexity
        complex_files = sorted(analyses, key=lambda a: a.metrics.get('average_complexity', 0), reverse=True)[:5]
        if complex_files:
            print(f"\n🔥 Most complex files:")
            for analysis in complex_files:
                complexity = analysis.metrics.get('average_complexity', 0)
                if complexity > 0:
                    print(f"  • {analysis.file_path}: {complexity:.1f}")


async def main():
    """Main demo function"""
    demo = AuraDemo()
    demo.print_banner()
    
    # Check LLM connection
    llm_available = await demo.check_llm_connection()
    
    print("\n🚀 Starting Aura Demo...")
    print("=" * 60)
    
    # Demo 1: Analyze current file
    print("\n1️⃣ Analyzing current file...")
    current_file = __file__
    analysis = demo.analyze_file(current_file)
    demo.display_analysis(analysis)
    
    # Demo 2: Scan codebase
    print("\n2️⃣ Scanning codebase...")
    analyses = demo.scan_codebase()
    demo.display_codebase_summary(analyses)
    
    # Demo 3: Semantic search
    print("\n3️⃣ Semantic code search...")
    search_results = demo.find_similar_code("function analysis code")
    demo.display_search_results(search_results)
    
    # Demo 4: Ask Aura (if LLM available)
    if llm_available:
        print("\n4️⃣ Asking Aura...")
        question = "What does this codebase do and how is it structured?"
        response = await demo.ask_aura(question)
        if response:
            print(f"\n🤖 Aura's Response:")
            print("-" * 40)
            print(response)
        else:
            print("❌ Could not get response from Aura")
    else:
        print("\n4️⃣ Skipping LLM demo (LM Studio not available)")
    
    print("\n✅ Aura Demo Complete!")
    print("=" * 60)
    print("🎯 Key Features Demonstrated:")
    print("  • Python code analysis with AST parsing")
    print("  • Codebase metrics and complexity analysis")
    print("  • Semantic code search using TF-IDF")
    print("  • Issue detection and documentation coverage")
    if llm_available:
        print("  • AI-powered code assistance with LM Studio")
    print("\n💡 This is just a taste of Aura's full capabilities!")


if __name__ == "__main__":
    asyncio.run(main())