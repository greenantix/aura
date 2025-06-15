
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
