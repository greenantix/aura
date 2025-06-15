#!/usr/bin/env python3
"""
Test file for Aura VS Code Extension Analysis
============================================

This file contains various Python constructs to test the real-time
analysis capabilities of the Aura VS Code extension.
"""

import os
import sys
from typing import List, Dict, Optional


class DataProcessor:
    """A sample class to demonstrate code analysis."""
    
    def __init__(self, name: str):
        self.name = name
        self.data = []
        
    def process_data(self, input_data: List[Dict]) -> Optional[Dict]:
        """Process input data and return results."""
        if not input_data:
            return None
            
        results = {}
        for item in input_data:
            # This loop has high complexity - should be flagged
            for key, value in item.items():
                if key in results:
                    if isinstance(value, (int, float)):
                        results[key] += value
                    else:
                        results[key] = str(results[key]) + str(value)
                else:
                    results[key] = value
                    
        return results
    
    def complex_calculation(self, x, y, z):
        # Undocumented function - should be flagged
        if x > 0:
            if y > 0:
                if z > 0:
                    return x * y * z
                else:
                    return x * y
            else:
                if z > 0:
                    return x * z
                else:
                    return x
        else:
            return 0


def simple_function(param):
    """A simple function with documentation."""
    return param * 2


def problematic_function():
    # Missing docstring - should be flagged
    unused_variable = "This variable is never used"
    
    # Potential security issue - should be flagged
    user_input = input("Enter something: ")
    exec(user_input)  # Dangerous use of exec()
    
    return "done"


# Global variable without type hints
global_counter = 0

# Function with too many parameters
def function_with_many_params(a, b, c, d, e, f, g, h, i, j):
    return a + b + c + d + e + f + g + h + i + j


if __name__ == "__main__":
    processor = DataProcessor("test")
    
    # Sample data for testing
    test_data = [
        {"score": 10, "name": "test1"},
        {"score": 20, "name": "test2"},
        {"score": 15, "name": "test3"}
    ]
    
    result = processor.process_data(test_data)
    print(f"Processing result: {result}")
    
    # Call problematic function (should trigger security warnings)
    problematic_function()