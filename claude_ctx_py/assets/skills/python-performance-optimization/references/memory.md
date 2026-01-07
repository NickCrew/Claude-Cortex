# Memory Optimization

## Generators for Large Datasets

**Avoid loading entire datasets into memory:**
```python
# Memory inefficient: Loads entire file
def read_large_file_bad(filepath):
    with open(filepath) as f:
        lines = f.readlines()  # 1GB file = 1GB RAM
    return [line.strip() for line in lines]

# Memory efficient: Process line by line
def read_large_file_good(filepath):
    with open(filepath) as f:
        for line in f:  # Only current line in memory
            yield line.strip()

# Usage: Process 1GB file with constant memory
for line in read_large_file_good('large.txt'):
    process(line)  # Only processes one line at a time
```

**Generator patterns:**
```python
# Infinite sequences (impossible with lists)
def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

# Pipeline processing
def process_pipeline(data):
    filtered = (x for x in data if x > 0)
    squared = (x**2 for x in filtered)
    normalized = (x / 100 for x in squared)
    return list(normalized)  # Lazy evaluation until consumed
```

## Slots for Classes

**Reduce memory overhead for many instances:**
```python
import sys

# Standard class: ~400 bytes per instance
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# With __slots__: ~200 bytes per instance (50% reduction)
class PointOptimized:
    __slots__ = ['x', 'y']  # No __dict__, fixed attributes

    def __init__(self, x, y):
        self.x = x
        self.y = y

# For 1M instances: Save ~200MB RAM
```

**Use slots when:**
- Creating many instances (thousands+)
- Fixed set of attributes known upfront
- Memory is constrained
- Don't need dynamic attribute addition

## Memoization for Expensive Calculations

**Cache results to avoid recomputation:**
```python
from functools import lru_cache

# Without cache: Exponential time O(2^n)
def fibonacci_slow(n):
    if n < 2:
        return n
    return fibonacci_slow(n-1) + fibonacci_slow(n-2)
# fibonacci_slow(35) = ~5 seconds

# With cache: Linear time O(n)
@lru_cache(maxsize=None)
def fibonacci_fast(n):
    if n < 2:
        return n
    return fibonacci_fast(n-1) + fibonacci_fast(n-2)
# fibonacci_fast(35) = ~0.0001 seconds (50,000x faster)
```

**Custom caching strategies:**
```python
from functools import wraps

def timed_cache(seconds):
    """Cache with time-based expiration."""
    import time
    cache = {}

    def decorator(func):
        @wraps(func)
        def wrapper(*args):
            now = time.time()
            if args in cache:
                result, timestamp = cache[args]
                if now - timestamp < seconds:
                    return result
            result = func(*args)
            cache[args] = (result, now)
            return result
        return wrapper
    return decorator

@timed_cache(seconds=300)
def fetch_expensive_data(api_key):
    # Result cached for 5 minutes
    return call_expensive_api(api_key)
```

## Lazy Evaluation

**Defer computation until needed:**
```python
class LazyProperty:
    """Computed once, cached thereafter."""

    def __init__(self, function):
        self.function = function
        self.name = function.__name__

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        value = self.function(obj)
        setattr(obj, self.name, value)  # Replace descriptor
        return value

class DataProcessor:
    def __init__(self, filepath):
        self.filepath = filepath

    @LazyProperty
    def data(self):
        # Expensive: Only loaded when accessed
        print("Loading data...")
        with open(self.filepath) as f:
            return f.read()

processor = DataProcessor('large.txt')
# No data loaded yet
result = processor.data  # Loads now
cached = processor.data  # Returns cached value
```
