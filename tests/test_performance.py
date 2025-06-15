#!/usr/bin/env python3
"""
Performance Testing File for Aura Analysis
==========================================

This file tests the performance characteristics of the analysis system
with various scenarios that might cause slowdowns.
"""

import time
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Optional, Union, Tuple, Set
import asyncio
from dataclasses import dataclass
from enum import Enum


# Test 1: Large file simulation with many classes and functions
class LargeClass1:
    """First large class for performance testing."""
    
    def __init__(self, value: int):
        self.value = value
        self.data: List[int] = []
        self.mapping: Dict[str, Any] = {}
    
    def method_1(self) -> int:
        """Method 1 documentation."""
        return self.value * 2
    
    def method_2(self, param: str) -> str:
        """Method 2 documentation."""
        return f"Processed: {param}"
    
    def method_3(self, items: List[int]) -> List[int]:
        """Method 3 documentation."""
        return [item * 2 for item in items]
    
    def method_4(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Method 4 documentation."""
        result = {}
        for key, value in data.items():
            if isinstance(value, (int, float)):
                result[key] = value * 2
            else:
                result[key] = str(value).upper()
        return result
    
    def method_5(self) -> None:
        """Method 5 documentation."""
        self.data.extend(range(100))
    
    def method_6(self, condition: bool) -> Optional[str]:
        """Method 6 documentation."""
        if condition:
            return "True condition"
        return None
    
    def method_7(self, *args: int) -> int:
        """Method 7 documentation."""
        return sum(args)
    
    def method_8(self, **kwargs: Any) -> Dict[str, Any]:
        """Method 8 documentation."""
        return kwargs
    
    def method_9(self, callback: callable) -> Any:
        """Method 9 documentation."""
        return callback(self.value)
    
    def method_10(self) -> 'LargeClass1':
        """Method 10 documentation."""
        return LargeClass1(self.value + 1)


class LargeClass2:
    """Second large class for performance testing."""
    
    def __init__(self, name: str, age: int, email: str):
        self.name = name
        self.age = age
        self.email = email
        self.preferences: Set[str] = set()
        self.history: List[Tuple[str, int]] = []
    
    @property
    def full_info(self) -> str:
        """Property documentation."""
        return f"{self.name} ({self.age}) - {self.email}"
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Static method documentation."""
        return "@" in email and "." in email
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LargeClass2':
        """Class method documentation."""
        return cls(data['name'], data['age'], data['email'])
    
    def add_preference(self, pref: str) -> None:
        """Add preference documentation."""
        self.preferences.add(pref)
    
    def remove_preference(self, pref: str) -> bool:
        """Remove preference documentation."""
        if pref in self.preferences:
            self.preferences.remove(pref)
            return True
        return False
    
    def get_preferences(self) -> List[str]:
        """Get preferences documentation."""
        return list(self.preferences)
    
    def add_history_entry(self, action: str, timestamp: int) -> None:
        """Add history entry documentation."""
        self.history.append((action, timestamp))
    
    def get_recent_history(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get recent history documentation."""
        return self.history[-limit:]
    
    def clear_history(self) -> int:
        """Clear history documentation."""
        count = len(self.history)
        self.history.clear()
        return count


# Test 2: Many standalone functions
def function_1(a: int, b: int) -> int:
    """Function 1 documentation."""
    return a + b

def function_2(items: List[str]) -> List[str]:
    """Function 2 documentation."""
    return [item.upper() for item in items]

def function_3(data: Dict[str, Any]) -> bool:
    """Function 3 documentation."""
    return len(data) > 0

def function_4(value: Union[int, str]) -> str:
    """Function 4 documentation."""
    if isinstance(value, int):
        return str(value)
    return value.strip()

def function_5(*args: Any, **kwargs: Any) -> Tuple[tuple, dict]:
    """Function 5 documentation."""
    return args, kwargs

def function_6(condition: bool) -> Optional[int]:
    """Function 6 documentation."""
    return 42 if condition else None

def function_7(callback: callable, value: Any) -> Any:
    """Function 7 documentation."""
    try:
        return callback(value)
    except Exception:
        return None

def function_8(items: List[int], threshold: int = 10) -> List[int]:
    """Function 8 documentation."""
    return [item for item in items if item > threshold]

def function_9(text: str, pattern: str) -> bool:
    """Function 9 documentation."""
    return pattern.lower() in text.lower()

def function_10(matrix: List[List[int]]) -> List[List[int]]:
    """Function 10 documentation."""
    return [[cell * 2 for cell in row] for row in matrix]

# Test 3: Complex type annotations and dataclasses
@dataclass
class DataClassExample:
    """Dataclass for testing complex type annotations."""
    id: int
    name: str
    scores: List[float]
    metadata: Dict[str, Union[str, int, bool]]
    optional_field: Optional[str] = None
    
    def calculate_average(self) -> float:
        """Calculate average score."""
        return sum(self.scores) / len(self.scores) if self.scores else 0.0
    
    def update_metadata(self, key: str, value: Union[str, int, bool]) -> None:
        """Update metadata entry."""
        self.metadata[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'scores': self.scores,
            'metadata': self.metadata,
            'optional_field': self.optional_field
        }

# Test 4: Enums and complex inheritance
class StatusEnum(Enum):
    """Status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class BaseProcessor:
    """Base processor class."""
    
    def __init__(self, name: str):
        self.name = name
        self.status = StatusEnum.PENDING
    
    def start_processing(self) -> None:
        """Start processing."""
        self.status = StatusEnum.PROCESSING
    
    def complete_processing(self) -> None:
        """Complete processing."""
        self.status = StatusEnum.COMPLETED
    
    def fail_processing(self) -> None:
        """Fail processing."""
        self.status = StatusEnum.FAILED

class DataProcessor(BaseProcessor):
    """Data processor implementation."""
    
    def __init__(self, name: str, chunk_size: int = 1000):
        super().__init__(name)
        self.chunk_size = chunk_size
        self.processed_items = 0
    
    def process_chunk(self, data: List[Any]) -> List[Any]:
        """Process a chunk of data."""
        self.start_processing()
        try:
            result = []
            for item in data:
                processed_item = self._process_single_item(item)
                result.append(processed_item)
                self.processed_items += 1
            self.complete_processing()
            return result
        except Exception:
            self.fail_processing()
            raise
    
    def _process_single_item(self, item: Any) -> Any:
        """Process a single item."""
        if isinstance(item, str):
            return item.strip().upper()
        elif isinstance(item, (int, float)):
            return item * 2
        elif isinstance(item, dict):
            return {k: v for k, v in item.items() if v is not None}
        else:
            return str(item)

# Test 5: Async functions
async def async_function_1(delay: float) -> str:
    """Async function 1 documentation."""
    await asyncio.sleep(delay)
    return f"Completed after {delay} seconds"

async def async_function_2(data: List[Any]) -> List[Any]:
    """Async function 2 documentation."""
    result = []
    for item in data:
        await asyncio.sleep(0.01)  # Simulate async work
        result.append(item)
    return result

async def async_function_3(url: str) -> Dict[str, Any]:
    """Async function 3 documentation."""
    await asyncio.sleep(0.1)  # Simulate network request
    return {"url": url, "status": "success", "timestamp": time.time()}

# Test 6: Threading and concurrency
class ThreadedProcessor:
    """Threaded processor for performance testing."""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.results: List[Any] = []
        self.lock = threading.Lock()
    
    def process_items(self, items: List[Any]) -> List[Any]:
        """Process items using thread pool."""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self._process_item, item) for item in items]
            results = [future.result() for future in futures]
        return results
    
    def _process_item(self, item: Any) -> Any:
        """Process single item in thread."""
        with self.lock:
            self.results.append(item)
        
        # Simulate processing time
        time.sleep(0.01)
        return f"Processed: {item}"

# Test 7: Complex decorators and context managers
def timing_decorator(func: callable) -> callable:
    """Decorator to time function execution."""
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            print(f"{func.__name__} took {end_time - start_time:.4f} seconds")
    return wrapper

class ResourceManager:
    """Context manager for resource handling."""
    
    def __init__(self, resource_name: str):
        self.resource_name = resource_name
        self.resource = None
    
    def __enter__(self) -> 'ResourceManager':
        print(f"Acquiring resource: {self.resource_name}")
        self.resource = f"Resource_{self.resource_name}"
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        print(f"Releasing resource: {self.resource_name}")
        self.resource = None

@timing_decorator
def complex_calculation(iterations: int) -> float:
    """Perform complex calculation."""
    result = 0.0
    for i in range(iterations):
        result += (i ** 0.5) * (i % 7) / (i + 1)
    return result

# Test 8: Large main function with many operations
def main():
    """Main function with comprehensive testing."""
    print("Starting performance testing...")
    
    # Test class instantiation
    obj1 = LargeClass1(100)
    obj2 = LargeClass2("Test User", 25, "test@example.com")
    
    # Test method calls
    result1 = obj1.method_1()
    result2 = obj1.method_3([1, 2, 3, 4, 5])
    result3 = obj1.method_4({"a": 1, "b": "test", "c": 3.14})
    
    # Test dataclass
    data_obj = DataClassExample(
        id=1,
        name="Test Data",
        scores=[85.5, 92.0, 78.5, 96.5],
        metadata={"category": "test", "priority": 1, "active": True}
    )
    average = data_obj.calculate_average()
    
    # Test processor
    processor = DataProcessor("TestProcessor", chunk_size=100)
    test_data = [i for i in range(1000)]
    chunks = [test_data[i:i+100] for i in range(0, len(test_data), 100)]
    
    for chunk in chunks:
        processed_chunk = processor.process_chunk(chunk)
    
    # Test threading
    threaded_processor = ThreadedProcessor(max_workers=4)
    threaded_results = threaded_processor.process_items(list(range(50)))
    
    # Test complex calculation
    calc_result = complex_calculation(10000)
    
    # Test context manager
    with ResourceManager("TestResource") as rm:
        print(f"Using resource: {rm.resource}")
    
    print(f"Performance testing complete.")
    print(f"Data object average: {average}")
    print(f"Processed items: {processor.processed_items}")
    print(f"Calculation result: {calc_result:.4f}")
    print(f"Threaded results count: {len(threaded_results)}")

if __name__ == "__main__":
    main()