# Aura Developer Guide

## Overview

Welcome to the Aura development ecosystem. This guide provides comprehensive information for developers who want to contribute to, extend, or integrate with the Aura autonomous AI coding assistant.

## Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Architecture Overview](#architecture-overview)
3. [Core Components](#core-components)
4. [Development Workflow](#development-workflow)
5. [Testing Guidelines](#testing-guidelines)
6. [Code Standards](#code-standards)
7. [Creating Extensions](#creating-extensions)
8. [API Development](#api-development)
9. [Debugging and Profiling](#debugging-and-profiling)
10. [Deployment](#deployment)
11. [Contributing Guidelines](#contributing-guidelines)

## Development Environment Setup

### Prerequisites

#### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+), macOS (10.15+), Windows 10+ with WSL2
- **Python**: 3.8+ (recommended: 3.10+)
- **Node.js**: 16+ (for VS Code extension development)
- **Git**: Latest version
- **Memory**: 8GB+ RAM (16GB recommended)
- **Storage**: 10GB+ free space

#### Required Tools
```bash
# Python development
sudo apt-get install python3-dev python3-pip python3-venv

# Node.js and npm
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# VS Code (for extension development)
sudo snap install code --classic

# ZeroMQ development libraries
sudo apt-get install libzmq3-dev

# Additional development tools
sudo apt-get install build-essential git curl wget
```

### Repository Setup

#### Cloning the Repository
```bash
git clone https://github.com/your-org/aura.git
cd aura
```

#### Python Environment Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install Aura in development mode
pip install -e .
```

#### VS Code Extension Setup
```bash
cd vscode/
npm install
npm run compile
```

#### Environment Configuration
```bash
# Copy example configuration
cp config/example.json config/local.json

# Set environment variables
export AURA_CONFIG_PATH=./config/local.json
export AURA_LOG_LEVEL=DEBUG
export AURA_LLM_PROVIDER=lm_studio
```

### Development Tools Setup

#### LM Studio Configuration
1. Download and install LM Studio
2. Load a coding-capable model (recommended: CodeLlama 13B or similar)
3. Start the local server on port 1234
4. Verify connection: `curl http://localhost:1234/v1/models`

#### IDE Configuration

##### VS Code Setup
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "typescript.preferences.includePackageJsonAutoImports": "auto"
}
```

##### Required VS Code Extensions
- Python
- Pylance
- TypeScript and JavaScript Language Features
- GitLens
- Thunder Client (for API testing)

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                     Development Stack                          │
├─────────────────────────────────────────────────────────────────┤
│  Frontend: VS Code Extension (TypeScript)                      │
│  Backend: Python Services (asyncio)                            │
│  Communication: ZeroMQ Message Bus                             │
│  AI: LM Studio/Ollama (Local LLMs)                            │
│  Storage: File-based (JSON/SQLite)                            │
│  Testing: pytest, Jest, Artillery                             │
└─────────────────────────────────────────────────────────────────┘
```

### Key Design Patterns

#### Dependency Injection
```python
# Core DI container
from core import aura_di

@aura_service
class MyService:
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

# Registration
aura_di.register_service('my_service', MyService)
```

#### Async/Await Patterns
```python
import asyncio

class AsyncService:
    async def process_request(self, request: Request) -> Response:
        # Non-blocking operations
        result = await self.analyze_code(request.code)
        await self.save_result(result)
        return Response(data=result)
```

#### Message Bus Communication
```python
from core import MessageBus, MessageType

async def handle_analysis_request(message):
    result = await analyze_file(message.payload['file_path'])
    response = Message(
        type=MessageType.RESPONSE,
        source='python_intelligence',
        target=message.source,
        payload={'analysis': result}
    )
    await message_bus.send(response)
```

## Core Components

### Python Intelligence Service

#### File Structure
```
intelligence/
├── __init__.py
├── python_analyzer.py      # Main Python analysis
├── self_analyzer.py        # Self-improvement analysis
├── research_agent.py       # Autonomous research
├── go/
│   └── ast_analyzer.py     # Go language analysis
└── rust/
    └── memory_analyzer.py  # Rust memory analysis
```

#### Creating a New Analyzer
```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class LanguageAnalyzer(ABC):
    """Base class for language-specific analyzers"""
    
    @abstractmethod
    async def analyze_file(self, file_path: str) -> AnalysisResult:
        """Analyze a single file"""
        pass
    
    @abstractmethod
    async def get_suggestions(self, analysis: AnalysisResult) -> List[Suggestion]:
        """Generate improvement suggestions"""
        pass

class JavaScriptAnalyzer(LanguageAnalyzer):
    """JavaScript/TypeScript analyzer implementation"""
    
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
    
    async def analyze_file(self, file_path: str) -> AnalysisResult:
        # Implementation for JavaScript analysis
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Parse AST using JavaScript parser
        ast = self._parse_javascript(content)
        
        # Extract metrics
        metrics = self._calculate_metrics(ast)
        
        # Detect issues
        issues = await self._detect_issues(ast, content)
        
        return AnalysisResult(
            file_path=file_path,
            metrics=metrics,
            issues=issues,
            suggestions=await self.get_suggestions(analysis)
        )
```

### LLM Provider Service

#### Adding a New Provider
```python
from abc import ABC, abstractmethod

class BaseLLMProvider(ABC):
    """Base class for LLM providers"""
    
    @abstractmethod
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response from the model"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if provider is available"""
        pass

class CustomLLMProvider(BaseLLMProvider):
    """Custom LLM provider implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        self.base_url = config['base_url']
        self.api_key = config.get('api_key')
    
    async def generate_response(self, prompt: str, **kwargs) -> str:
        # Implementation for custom LLM API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "model": kwargs.get('model', 'default'),
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": kwargs.get('temperature', 0.7)
                },
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            return response.json()['choices'][0]['message']['content']
    
    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except:
            return False
```

### VS Code Extension Development

#### Adding a New Panel
```typescript
// src/providers/myCustomProvider.ts
import * as vscode from 'vscode';
import { AuraConnection } from '../connection';

export class MyCustomProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'aura.myCustom';
    
    constructor(
        private readonly extensionUri: vscode.Uri,
        private connection: AuraConnection
    ) {}
    
    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        token: vscode.CancellationToken
    ) {
        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this.extensionUri]
        };
        
        webviewView.webview.html = this.getHtmlForWebview(webviewView.webview);
        
        webviewView.webview.onDidReceiveMessage(async data => {
            switch (data.type) {
                case 'customAction':
                    await this.handleCustomAction(data.payload);
                    break;
            }
        });
    }
    
    private getHtmlForWebview(webview: vscode.Webview): string {
        return `
            <!DOCTYPE html>
            <html>
            <head>
                <title>My Custom Panel</title>
            </head>
            <body>
                <h2>Custom Functionality</h2>
                <button onclick="performAction()">Execute</button>
                <script>
                    const vscode = acquireVsCodeApi();
                    function performAction() {
                        vscode.postMessage({
                            type: 'customAction',
                            payload: { action: 'execute' }
                        });
                    }
                </script>
            </body>
            </html>
        `;
    }
}
```

## Development Workflow

### Git Workflow

#### Branch Naming
- **Feature branches**: `feature/description` (e.g., `feature/javascript-analyzer`)
- **Bug fixes**: `fix/issue-number` (e.g., `fix/memory-leak-123`)
- **Hotfixes**: `hotfix/critical-issue`
- **Documentation**: `docs/section-name`

#### Commit Messages
```bash
# Use semantic commit format
git commit -m "feat(intelligence): add JavaScript AST analyzer

- Implement JavaScript/TypeScript parsing
- Add complexity metrics calculation
- Include ESLint-style issue detection
- Support modern JS features (async/await, destructuring)

Closes #142"
```

#### Pull Request Process
1. **Create feature branch** from `main`
2. **Implement changes** with tests
3. **Update documentation** if needed
4. **Run full test suite**: `npm run test:all`
5. **Create pull request** with detailed description
6. **Code review** by maintainers
7. **Address feedback** and update branch
8. **Squash and merge** after approval

### Development Commands

#### Python Development
```bash
# Run specific service
python -m aura.intelligence.python_analyzer

# Run tests
pytest tests/ -v
pytest tests/test_python_analyzer.py::test_complexity_calculation

# Code formatting
black aura/ tests/
isort aura/ tests/

# Linting
flake8 aura/
mypy aura/

# Security scanning
bandit -r aura/
```

#### VS Code Extension Development
```bash
# Compile TypeScript
npm run compile

# Watch mode for development
npm run watch

# Run tests
npm test

# Package extension
npm run package

# Install local development version
code --install-extension aura-*.vsix
```

#### System Testing
```bash
# Start Aura system
python aura_main.py

# Run integration tests
python -m pytest tests/integration/

# Performance testing
python -m pytest tests/performance/ --benchmark-only

# Load testing
artillery run tests/load/api-load-test.yml
```

## Testing Guidelines

### Test Structure

#### Python Tests
```python
# tests/test_python_analyzer.py
import pytest
from unittest.mock import Mock, patch
from aura.intelligence.python_analyzer import PythonAnalyzer

class TestPythonAnalyzer:
    
    @pytest.fixture
    def analyzer(self):
        mock_llm = Mock()
        return PythonAnalyzer(mock_llm)
    
    @pytest.fixture
    def sample_code(self):
        return '''
def complex_function(a, b, c):
    if a > 0:
        if b > 0:
            if c > 0:
                return a + b + c
            else:
                return a + b
        else:
            return a
    else:
        return 0
'''
    
    async def test_complexity_calculation(self, analyzer, sample_code):
        result = await analyzer.calculate_complexity(sample_code)
        assert result.cyclomatic_complexity == 4
        assert result.cognitive_complexity >= 3
    
    async def test_issue_detection(self, analyzer, sample_code):
        issues = await analyzer.detect_issues(sample_code)
        assert any(issue.type == 'complexity' for issue in issues)
    
    @patch('aura.intelligence.python_analyzer.ast.parse')
    def test_parse_error_handling(self, mock_parse, analyzer):
        mock_parse.side_effect = SyntaxError("Invalid syntax")
        
        with pytest.raises(AnalysisError):
            await analyzer.analyze_file("invalid.py")
```

#### TypeScript Tests
```typescript
// tests/extension.test.ts
import * as assert from 'assert';
import * as vscode from 'vscode';
import { AuraExtension } from '../src/extension';

suite('Extension Test Suite', () => {
    vscode.window.showInformationMessage('Start all tests.');
    
    test('Extension activation', async () => {
        const extension = vscode.extensions.getExtension('aura.autonomous-assistant');
        assert.ok(extension);
        
        await extension?.activate();
        assert.strictEqual(extension?.isActive, true);
    });
    
    test('Chat provider initialization', async () => {
        const mockContext = {
            subscriptions: [],
            extensionUri: vscode.Uri.file('/mock/path')
        } as vscode.ExtensionContext;
        
        const auraExt = new AuraExtension(mockContext);
        await auraExt.initialize();
        
        assert.ok(auraExt.chatProvider);
    });
});
```

### Test Coverage

#### Coverage Requirements
- **Unit tests**: 90%+ line coverage
- **Integration tests**: All API endpoints
- **E2E tests**: Critical user workflows
- **Performance tests**: Response time requirements

#### Running Coverage
```bash
# Python coverage
coverage run -m pytest tests/
coverage report --show-missing
coverage html  # Generate HTML report

# TypeScript coverage
npm run test:coverage
```

## Code Standards

### Python Style Guide

#### Code Formatting
```python
# Use Black formatter with line length 88
# Use isort for import sorting
# Follow PEP 8 guidelines

# Good example
from typing import List, Optional, Dict, Any
import asyncio

class CodeAnalyzer:
    """Analyzes code for quality and complexity metrics."""
    
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self._cache: Dict[str, Any] = {}
    
    async def analyze_file(self, file_path: str) -> Optional[AnalysisResult]:
        """Analyze a single file for issues and metrics.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            Analysis result or None if file cannot be analyzed
            
        Raises:
            AnalysisError: If analysis fails due to syntax errors
        """
        try:
            content = await self._read_file(file_path)
            return await self._perform_analysis(content)
        except FileNotFoundError:
            logger.warning(f"File not found: {file_path}")
            return None
```

#### Error Handling
```python
# Custom exceptions
class AuraError(Exception):
    """Base exception for Aura errors"""
    pass

class AnalysisError(AuraError):
    """Raised when code analysis fails"""
    pass

class ConfigurationError(AuraError):
    """Raised when configuration is invalid"""
    pass

# Proper error handling
async def safe_analysis(file_path: str) -> Optional[AnalysisResult]:
    try:
        return await analyze_file(file_path)
    except AnalysisError as e:
        logger.error(f"Analysis failed for {file_path}: {e}")
        return None
    except Exception as e:
        logger.exception(f"Unexpected error analyzing {file_path}")
        raise AnalysisError(f"Analysis failed: {e}") from e
```

### TypeScript Style Guide

#### Code Organization
```typescript
// Use explicit types and interfaces
interface AnalysisRequest {
    filePath: string;
    language: string;
    options?: AnalysisOptions;
}

interface AnalysisOptions {
    includeMetrics: boolean;
    detectionLevel: 'basic' | 'advanced' | 'comprehensive';
}

// Use async/await for asynchronous operations
class AuraService {
    private readonly connection: AuraConnection;
    
    constructor(connection: AuraConnection) {
        this.connection = connection;
    }
    
    public async analyzeFile(request: AnalysisRequest): Promise<AnalysisResult> {
        try {
            const response = await this.connection.sendRequest({
                type: 'ANALYZE_FILE',
                payload: request
            });
            
            return this.parseAnalysisResult(response);
        } catch (error) {
            this.handleError('File analysis failed', error);
            throw error;
        }
    }
    
    private handleError(message: string, error: unknown): void {
        console.error(`[AuraService] ${message}:`, error);
    }
}
```

### Documentation Standards

#### Python Docstrings
```python
def calculate_complexity(code: str, method: str = 'cyclomatic') -> ComplexityResult:
    """Calculate code complexity using specified method.
    
    This function analyzes the provided code and calculates complexity
    metrics to help assess code maintainability and readability.
    
    Args:
        code: The source code to analyze
        method: Complexity calculation method ('cyclomatic', 'cognitive', 'halstead')
    
    Returns:
        ComplexityResult containing various complexity metrics
    
    Raises:
        ValueError: If method is not supported
        SyntaxError: If code contains syntax errors
    
    Example:
        >>> code = "def hello(): return 'world'"
        >>> result = calculate_complexity(code)
        >>> result.cyclomatic_complexity
        1
    """
```

#### TypeScript Documentation
```typescript
/**
 * Provides intelligent code analysis and AI-powered suggestions
 * for VS Code integration.
 * 
 * @example
 * ```typescript
 * const provider = new AuraCodeAnalysisProvider(connection);
 * const analysis = await provider.analyzeCurrentFile();
 * console.log(`Found ${analysis.issues.length} issues`);
 * ```
 */
export class AuraCodeAnalysisProvider implements vscode.TreeDataProvider<CodeAnalysisItem> {
    /**
     * Analyzes the currently active file in the editor.
     * 
     * @returns Promise resolving to analysis results
     * @throws {AnalysisError} When analysis fails
     */
    public async analyzeCurrentFile(): Promise<FileAnalysis> {
        // Implementation
    }
}
```

## Creating Extensions

### Language Analyzer Extension

#### Step 1: Create Analyzer Class
```python
# aura/intelligence/languages/kotlin/analyzer.py
from typing import List, Dict, Any
from aura.intelligence.base import LanguageAnalyzer
from aura.models import AnalysisResult, Issue, Suggestion

class KotlinAnalyzer(LanguageAnalyzer):
    """Kotlin language analyzer with Android-specific insights"""
    
    LANGUAGE = 'kotlin'
    FILE_EXTENSIONS = ['.kt', '.kts']
    
    def __init__(self, llm_provider):
        super().__init__(llm_provider)
        self._parser = KotlinParser()
    
    async def analyze_file(self, file_path: str) -> AnalysisResult:
        """Analyze Kotlin file for Android best practices"""
        content = await self._read_file(file_path)
        
        # Parse Kotlin AST
        ast = self._parser.parse(content)
        
        # Calculate metrics
        metrics = self._calculate_metrics(ast)
        
        # Detect Android-specific issues
        issues = await self._detect_android_issues(ast, content)
        
        # Generate suggestions
        suggestions = await self._generate_suggestions(ast, issues)
        
        return AnalysisResult(
            file_path=file_path,
            language=self.LANGUAGE,
            metrics=metrics,
            issues=issues,
            suggestions=suggestions
        )
    
    async def _detect_android_issues(self, ast, content: str) -> List[Issue]:
        """Detect Android-specific code issues"""
        issues = []
        
        # Check for memory leaks
        if self._has_context_leak(ast):
            issues.append(Issue(
                type='memory_leak',
                severity='high',
                message='Potential context leak detected',
                suggestion='Use weak references or application context'
            ))
        
        # Check for UI thread violations
        if self._has_ui_thread_violation(ast):
            issues.append(Issue(
                type='ui_thread',
                severity='medium',
                message='Potential UI thread blocking operation',
                suggestion='Use coroutines or background thread'
            ))
        
        return issues
```

#### Step 2: Register Analyzer
```python
# aura/intelligence/__init__.py
from .languages.kotlin.analyzer import KotlinAnalyzer

def register_analyzers():
    """Register all available language analyzers"""
    analyzers = {
        'python': PythonAnalyzer,
        'javascript': JavaScriptAnalyzer,
        'typescript': TypeScriptAnalyzer,
        'kotlin': KotlinAnalyzer,  # New analyzer
    }
    
    return analyzers
```

### VS Code Command Extension

#### Step 3: Add VS Code Commands
```typescript
// src/commands/kotlinCommands.ts
import * as vscode from 'vscode';
import { AuraConnection } from '../connection';

export class KotlinCommands {
    constructor(private connection: AuraConnection) {}
    
    public registerCommands(context: vscode.ExtensionContext): void {
        const commands = [
            vscode.commands.registerCommand(
                'aura.analyzeAndroidPerformance',
                this.analyzeAndroidPerformance.bind(this)
            ),
            vscode.commands.registerCommand(
                'aura.generateKotlinTests',
                this.generateKotlinTests.bind(this)
            )
        ];
        
        context.subscriptions.push(...commands);
    }
    
    private async analyzeAndroidPerformance(): Promise<void> {
        const editor = vscode.window.activeTextEditor;
        if (!editor || !editor.document.fileName.endsWith('.kt')) {
            vscode.window.showWarningMessage('Please open a Kotlin file');
            return;
        }
        
        try {
            const analysis = await this.connection.analyzeFile(
                editor.document.fileName,
                { includeAndroidAnalysis: true }
            );
            
            this.showPerformanceReport(analysis);
        } catch (error) {
            vscode.window.showErrorMessage(`Analysis failed: ${error}`);
        }
    }
}
```

## API Development

### REST API Endpoints

#### Creating New Endpoints
```python
# aura/api/routes/analysis.py
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from aura.models import AnalysisRequest, AnalysisResult
from aura.services import AnalysisService

router = APIRouter(prefix="/api/v1/analysis", tags=["analysis"])

@router.post("/file", response_model=AnalysisResult)
async def analyze_file(
    request: AnalysisRequest,
    service: AnalysisService = Depends(get_analysis_service)
) -> AnalysisResult:
    """Analyze a single file for issues and metrics"""
    try:
        result = await service.analyze_file(
            file_path=request.file_path,
            language=request.language,
            options=request.options
        )
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{file_path:path}", response_model=List[AnalysisResult])
async def get_analysis_history(
    file_path: str,
    limit: Optional[int] = 10,
    service: AnalysisService = Depends(get_analysis_service)
) -> List[AnalysisResult]:
    """Get analysis history for a file"""
    return await service.get_analysis_history(file_path, limit)
```

### Message Bus Integration

#### Custom Message Handlers
```python
# aura/services/custom_service.py
from aura.core import AuraService, MessageType
from aura.core.messaging import message_handler

class CustomAnalysisService(AuraService):
    """Custom analysis service with specialized capabilities"""
    
    def __init__(self, config):
        super().__init__("custom_analysis", config)
        self.specialized_analyzer = SpecializedAnalyzer()
    
    @message_handler(MessageType.CUSTOM_ANALYSIS_REQUEST)
    async def handle_custom_analysis(self, message):
        """Handle custom analysis requests"""
        try:
            file_path = message.payload['file_path']
            analysis_type = message.payload['type']
            
            result = await self.specialized_analyzer.analyze(
                file_path, 
                analysis_type
            )
            
            await self.send_response(message, {
                'status': 'success',
                'result': result
            })
        except Exception as e:
            await self.send_error(message, str(e))
    
    async def start_service(self):
        """Start the custom analysis service"""
        await super().start_service()
        await self.specialized_analyzer.initialize()
```

## Debugging and Profiling

### Debug Configuration

#### VS Code Debug Settings
```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug Aura Main",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/aura_main.py",
            "console": "integratedTerminal",
            "env": {
                "AURA_LOG_LEVEL": "DEBUG",
                "AURA_CONFIG_PATH": "./config/debug.json"
            },
            "args": ["--debug"]
        },
        {
            "name": "Debug Python Analyzer",
            "type": "python",
            "request": "launch",
            "module": "aura.intelligence.python_analyzer",
            "console": "integratedTerminal",
            "args": ["--file", "${file}"]
        },
        {
            "name": "Debug VS Code Extension",
            "type": "extensionHost",
            "request": "launch",
            "args": ["--extensionDevelopmentPath=${workspaceFolder}/vscode"],
            "outFiles": ["${workspaceFolder}/vscode/out/**/*.js"]
        }
    ]
}
```

### Performance Profiling

#### Python Profiling
```python
# utils/profiler.py
import cProfile
import pstats
from functools import wraps

def profile_function(func):
    """Decorator to profile function execution"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        result = func(*args, **kwargs)
        pr.disable()
        
        stats = pstats.Stats(pr)
        stats.sort_stats('cumulative')
        stats.print_stats(20)  # Top 20 functions
        
        return result
    return wrapper

# Usage
@profile_function
async def analyze_large_file(file_path: str):
    # Implementation
    pass
```

#### Memory Profiling
```python
# utils/memory_profiler.py
import tracemalloc
import asyncio
from typing import Any

class MemoryProfiler:
    """Memory usage profiler for Aura services"""
    
    def __init__(self):
        self.snapshots = []
    
    def start_profiling(self):
        """Start memory profiling"""
        tracemalloc.start()
        self.take_snapshot("start")
    
    def take_snapshot(self, label: str):
        """Take a memory snapshot"""
        if tracemalloc.is_tracing():
            snapshot = tracemalloc.take_snapshot()
            self.snapshots.append((label, snapshot))
    
    def compare_snapshots(self, label1: str, label2: str):
        """Compare two memory snapshots"""
        snap1 = next(s for l, s in self.snapshots if l == label1)
        snap2 = next(s for l, s in self.snapshots if l == label2)
        
        top_stats = snap2.compare_to(snap1, 'lineno')
        
        print(f"Memory comparison: {label1} -> {label2}")
        for stat in top_stats[:10]:
            print(stat)
```

## Deployment

### Local Development Deployment

#### Docker Setup
```dockerfile
# Dockerfile.dev
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libzmq3-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements*.txt ./
RUN pip install -r requirements-dev.txt

# Copy source code
COPY . .

# Install Aura in development mode
RUN pip install -e .

# Expose ports
EXPOSE 5559 5560 8080

# Development command
CMD ["python", "aura_main.py", "--dev"]
```

#### Docker Compose
```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  aura:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "5559:5559"  # Message bus frontend
      - "5560:5560"  # Message bus backend
      - "8080:8080"  # Web GUI
    volumes:
      - .:/app
      - /app/venv
    environment:
      - AURA_LOG_LEVEL=DEBUG
      - AURA_CONFIG_PATH=/app/config/development.json
    depends_on:
      - lm-studio

  lm-studio:
    image: lmstudio/server
    ports:
      - "1234:1234"
    volumes:
      - ./models:/models
    environment:
      - MODEL_PATH=/models/CodeLlama-13B-Instruct
```

### Production Deployment

#### Production Configuration
```python
# config/production.py
import os

PRODUCTION_CONFIG = {
    "logging": {
        "level": "INFO",
        "format": "json",
        "handlers": ["file", "syslog"]
    },
    "security": {
        "enable_authentication": True,
        "token_expiry": 3600,
        "rate_limiting": {
            "requests_per_minute": 100,
            "burst_size": 20
        }
    },
    "performance": {
        "max_concurrent_analysis": 10,
        "cache_size": 1000,
        "request_timeout": 30
    },
    "monitoring": {
        "enable_metrics": True,
        "metrics_port": 9090,
        "health_check_interval": 30
    }
}
```

#### Kubernetes Deployment
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aura-services
spec:
  replicas: 3
  selector:
    matchLabels:
      app: aura
  template:
    metadata:
      labels:
        app: aura
    spec:
      containers:
      - name: aura
        image: aura:latest
        ports:
        - containerPort: 5559
        - containerPort: 8080
        env:
        - name: AURA_CONFIG_PATH
          value: "/etc/aura/production.json"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        volumeMounts:
        - name: config
          mountPath: /etc/aura
      volumes:
      - name: config
        configMap:
          name: aura-config
```

## Contributing Guidelines

### Code Review Process

#### Pre-Review Checklist
- [ ] Code follows style guidelines
- [ ] Tests are written and passing
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] Performance impact assessed
- [ ] Breaking changes documented

#### Review Criteria
1. **Functionality**: Does the code work as intended?
2. **Design**: Is the solution well-architected?
3. **Complexity**: Is the code easy to understand and maintain?
4. **Testing**: Are there adequate tests with good coverage?
5. **Performance**: Are there any performance implications?
6. **Security**: Are there any security concerns?

### Release Process

#### Version Numbering
- **Major** (X.0.0): Breaking changes
- **Minor** (0.X.0): New features, backward compatible
- **Patch** (0.0.X): Bug fixes, backward compatible

#### Release Checklist
1. Update version numbers
2. Update CHANGELOG.md
3. Run full test suite
4. Create release branch
5. Tag release in Git
6. Build and publish artifacts
7. Update documentation
8. Announce release

---

**This developer guide provides the foundation for contributing to Aura's continued evolution. As the system grows more autonomous, the development process itself becomes more intelligent and self-improving.**