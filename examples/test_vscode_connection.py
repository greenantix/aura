#!/usr/bin/env python3
"""
VSCode Extension Connection Test
===============================

Simple test to verify VSCode extension can connect to Aura backend.

Author: Aura - Level 9 Autonomous AI Coding Assistant
"""

import asyncio
import json
import time
from pathlib import Path


def create_test_workspace():
    """Create a test workspace for VSCode testing"""
    workspace_dir = Path("test_workspace")
    workspace_dir.mkdir(exist_ok=True)
    
    # Create a test Python file
    test_file = workspace_dir / "test_analysis.py"
    test_file.write_text('''
"""
Test Python file for Aura analysis
"""

def calculate_fibonacci(n: int) -> int:
    """Calculate the nth Fibonacci number.
    
    Args:
        n: The position in the Fibonacci sequence
        
    Returns:
        The nth Fibonacci number
    """
    if n <= 1:
        return n
    return calculate_fibonacci(n - 1) + calculate_fibonacci(n - 2)


def process_data(data_list):
    # Missing docstring
    result = []
    for item in data_list:
        if item > 0:
            result.append(item * 2)
        else:
            result.append(0)
    return result


class DataProcessor:
    """Simple data processor with some quality issues."""
    
    def __init__(self):
        self.count = 0
    
    def process(self, x):
        # Missing type hints and docstring
        if x > 10:
            if x < 100:
                if x % 2 == 0:
                    return x * 2
                else:
                    return x * 3
            else:
                return x
        else:
            return 0
''')
    
    # Create a test JavaScript file
    js_file = workspace_dir / "test_script.js"
    js_file.write_text('''
/**
 * Test JavaScript file for Aura analysis
 */

function calculateSum(numbers) {
    let sum = 0;
    for (let i = 0; i < numbers.length; i++) {
        sum += numbers[i];
    }
    return sum;
}

// Missing documentation
function processArray(arr) {
    if (arr.length > 0) {
        if (typeof arr[0] === 'number') {
            if (arr[0] > 0) {
                return arr.map(x => x * 2);
            } else {
                return arr.map(x => Math.abs(x));
            }
        } else {
            return [];
        }
    } else {
        return [];
    }
}

class Calculator {
    constructor() {
        this.result = 0;
    }
    
    add(x) {
        this.result += x;
        return this;
    }
    
    multiply(x) {
        this.result *= x;
        return this;
    }
    
    getResult() {
        return this.result;
    }
}
''')
    
    # Create VSCode workspace settings
    vscode_dir = workspace_dir / ".vscode"
    vscode_dir.mkdir(exist_ok=True)
    
    settings = {
        "aura.autoAnalysis": True,
        "aura.serverUrl": "tcp://localhost:5559",
        "aura.llmProvider": "lm_studio",
        "aura.analysisDepth": "detailed",
        "aura.showNotifications": True,
        "aura.themeColor": "purple"
    }
    
    settings_file = vscode_dir / "settings.json"
    settings_file.write_text(json.dumps(settings, indent=2))
    
    # Create workspace file
    workspace_config = {
        "folders": [
            {
                "path": "."
            }
        ],
        "settings": settings,
        "extensions": {
            "recommendations": [
                "aura-ai.aura-autonomous-assistant"
            ]
        }
    }
    
    workspace_file = workspace_dir / "aura_test.code-workspace"
    workspace_file.write_text(json.dumps(workspace_config, indent=2))
    
    return workspace_dir


def main():
    """Main test function"""
    print("🚀 Setting up VSCode Extension Test Environment")
    print("=" * 50)
    
    # Create test workspace
    workspace_dir = create_test_workspace()
    workspace_file = workspace_dir / "aura_test.code-workspace"
    
    print(f"✅ Created test workspace at: {workspace_dir}")
    print(f"📁 Files created:")
    for file in workspace_dir.rglob("*"):
        if file.is_file():
            print(f"   - {file.relative_to(workspace_dir)}")
    
    print(f"\n🔧 VSCode Extension Testing Instructions:")
    print(f"=" * 50)
    print(f"1. Open VSCode with the test workspace:")
    print(f"   code '{workspace_file.absolute()}'")
    print(f"")
    print(f"2. Look for Aura icon in the Activity Bar (robot icon)")
    print(f"")
    print(f"3. Test the following commands:")
    print(f"   - Ctrl+Alt+A (Cmd+Alt+A on Mac): Analyze current file")
    print(f"   - Ctrl+Alt+Q (Cmd+Alt+Q on Mac): Ask Aura a question")
    print(f"   - Right-click on a file → 'Analyze Current File'")
    print(f"")
    print(f"4. Check the Aura panels in the sidebar:")
    print(f"   - Dashboard")
    print(f"   - Code Analysis") 
    print(f"   - Suggestions")
    print(f"   - Chat with Aura")
    print(f"")
    print(f"5. Test auto-analysis by saving a file")
    print(f"")
    print(f"6. To start Aura backend server:")
    print(f"   cd /home/greenantix/AI/LLMdiver/aura")
    print(f"   python aura_main.py")
    print(f"")
    print(f"📝 Test Files for Analysis:")
    print(f"   - test_analysis.py (Python with quality issues)")
    print(f"   - test_script.js (JavaScript with complexity issues)")
    print(f"")
    print(f"🎯 Expected Behavior:")
    print(f"   - Extension should show up in Activity Bar")
    print(f"   - Commands should be available in Command Palette")
    print(f"   - Right-click context menus should show Aura options")
    print(f"   - Settings should be configurable in VSCode preferences")
    print(f"   - Auto-analysis should trigger on file save")
    print(f"")
    print(f"💡 Troubleshooting:")
    print(f"   - Check VSCode Developer Tools (Help → Toggle Developer Tools)")
    print(f"   - Look for Aura extension logs in Output panel")
    print(f"   - Ensure Aura backend is running on localhost:5559")
    print(f"   - Verify extension is enabled in Extensions panel")


if __name__ == "__main__":
    main()