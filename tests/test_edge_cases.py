#!/usr/bin/env python3
"""
Edge Cases Test File for Aura Analysis
=====================================

This file tests various edge cases and potential issues
that could break the analysis system.
"""

# Test 1: Very long lines (should handle gracefully)
def function_with_very_long_line():
    """This function has an extremely long line that might cause issues with the analysis system and should be handled gracefully without breaking the parser or causing performance issues."""
    very_long_variable_name_that_exceeds_normal_limits = "This is a very long string that contains a lot of text and might cause issues with parsing or analysis systems that don't handle long lines properly"
    return very_long_variable_name_that_exceeds_normal_limits

# Test 2: Deeply nested structures
def deeply_nested_function():
    """Test deeply nested control structures."""
    for i in range(10):
        if i > 5:
            for j in range(i):
                if j % 2 == 0:
                    for k in range(j):
                        if k > 0:
                            try:
                                if k % 3 == 0:
                                    print(f"Complex nesting: {i}, {j}, {k}")
                                else:
                                    continue
                            except Exception as e:
                                if str(e):
                                    pass
                                else:
                                    break

# Test 3: Unicode and special characters
def unicode_test_函数():
    """测试 Unicode 字符处理"""
    emoji_var = "🚀🔥💻⚡️🎯"
    special_chars = "àáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ"
    return f"{emoji_var} {special_chars}"

# Test 4: Empty functions and classes
class EmptyClass:
    pass

def empty_function():
    pass

# Test 5: Complex decorators and metaclasses
from functools import wraps
from typing import Any, Callable

def complex_decorator(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            result = func(*args, **kwargs)
            return result
        except Exception:
            return None
    return wrapper

class MetaTest(type):
    def __new__(cls, name, bases, attrs):
        return super().__new__(cls, name, bases, attrs)

class ComplexClass(metaclass=MetaTest):
    @complex_decorator
    def complex_method(self):
        return "complex"

# Test 6: Dynamic code generation (should flag as risky)
def dynamic_code_execution():
    """This function uses dynamic code execution which should be flagged."""
    code_string = "print('Dynamic code')"
    exec(code_string)  # Should be flagged as security risk
    
    # Also test eval
    expression = "2 + 2"
    result = eval(expression)  # Should also be flagged
    
    return result

# Test 7: File operations without error handling
def risky_file_operations():
    """File operations that could fail."""
    # Should flag missing error handling
    with open('/nonexistent/file.txt', 'r') as f:
        content = f.read()
    
    # Should flag potential path traversal
    user_filename = "../../../etc/passwd"
    with open(user_filename, 'r') as f:
        data = f.read()
    
    return content, data

# Test 8: Massive function with too many responsibilities
def massive_function_with_too_many_responsibilities(param1, param2, param3, param4, param5, param6, param7, param8, param9, param10):
    """This function does way too many things and should be flagged for refactoring."""
    # Database operations
    connection = None
    cursor = None
    
    # File processing
    files_processed = []
    errors = []
    
    # Network requests
    responses = []
    
    # Mathematical calculations
    calculations = []
    
    # String processing
    processed_strings = []
    
    # Data validation
    validation_errors = []
    
    # Logging
    log_entries = []
    
    # Configuration management
    config_values = {}
    
    # Cache management
    cache_data = {}
    
    # This function clearly violates single responsibility principle
    for i in range(100):
        if i % 2 == 0:
            if param1:
                if param2:
                    if param3:
                        calculations.append(i * param1 * param2 * param3)
                        if len(calculations) > 50:
                            processed_strings.append(str(calculations[-1]))
                            if param4:
                                validation_errors.append("Too many calculations")
                                if param5:
                                    log_entries.append(f"Error at iteration {i}")
                                    if param6:
                                        config_values[f"key_{i}"] = param6
                                        if param7:
                                            cache_data[f"cache_{i}"] = param7
    
    return {
        'calculations': calculations,
        'strings': processed_strings,
        'errors': validation_errors,
        'logs': log_entries,
        'config': config_values,
        'cache': cache_data
    }

# Test 9: Circular imports simulation (in comments to avoid actual issues)
# from circular_module import CircularClass  # This would cause circular import

# Test 10: Memory-intensive operations
def memory_intensive_function():
    """Function that could consume a lot of memory."""
    # Large list creation
    massive_list = [i for i in range(1000000)]
    
    # Nested list comprehension
    nested_data = [[j for j in range(1000)] for i in range(1000)]
    
    # Dictionary with many entries
    large_dict = {f"key_{i}": f"value_{i}" * 100 for i in range(10000)}
    
    return len(massive_list) + len(nested_data) + len(large_dict)

# Test 11: Unusual syntax patterns
class ContextManagerTest:
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

# Test 12: Generator with complex logic
def complex_generator():
    """Generator with complex nested logic."""
    for i in range(100):
        if i % 2 == 0:
            for j in range(i):
                if j % 3 == 0:
                    try:
                        yield i * j
                    except GeneratorExit:
                        break
                    except Exception:
                        continue
                else:
                    yield j
        else:
            yield i

if __name__ == "__main__":
    # Test execution
    print("Running edge case tests...")
    
    # Test each function
    try:
        function_with_very_long_line()
        deeply_nested_function()
        unicode_test_函数()
        
        empty_obj = EmptyClass()
        empty_function()
        
        complex_obj = ComplexClass()
        complex_obj.complex_method()
        
        dynamic_code_execution()  # Should trigger security warnings
        
        # Skip risky file operations in testing
        # risky_file_operations()
        
        result = massive_function_with_too_many_responsibilities(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
        print(f"Massive function result keys: {list(result.keys())}")
        
        memory_result = memory_intensive_function()
        print(f"Memory intensive result: {memory_result}")
        
        with ContextManagerTest() as cm:
            pass
        
        gen = complex_generator()
        first_values = [next(gen) for _ in range(10)]
        print(f"Generator first 10 values: {first_values}")
        
    except Exception as e:
        print(f"Error during testing: {e}")
    
    print("Edge case testing complete.")