---
name: python-performance-optimization
description: Python performance optimization patterns using profiling, algorithmic improvements, and acceleration techniques. Use when optimizing slow Python code, reducing memory usage, or improving application throughput and latency.
---

# Python Performance Optimization

Expert guidance for profiling, optimizing, and accelerating Python applications through systematic analysis, algorithmic improvements, efficient data structures, and acceleration techniques.

## When to Use This Skill

- Code runs too slowly for production requirements
- High CPU usage or memory consumption issues
- Need to reduce API response times or batch processing duration
- Application fails to scale under load
- Optimizing data processing pipelines or scientific computing
- Reducing cloud infrastructure costs through efficiency gains
- Profile-guided optimization after measuring performance bottlenecks

## Performance Methodology

### 1. Measure First, Optimize Second

**Always profile before optimizing:**
```python
import cProfile
import pstats
from pstats import SortKey

def profile_code():
    profiler = cProfile.Profile()
    profiler.enable()

    # Code to profile
    result = slow_function()

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats(SortKey.CUMULATIVE)
    stats.print_stats(20)  # Top 20 functions

    return result
```

**Key principle:**
- Never optimize without data
- Profile identifies actual bottlenecks (often surprising)
- 80/20 rule: 80% of time spent in 20% of code
- Optimize hot paths first for maximum impact

### 2. Line-by-Line Profiling

**Find exact slow lines with line_profiler:**
```python
# Install: pip install line-profiler
from line_profiler import LineProfiler

@profile  # Decorator for kernprof
def expensive_function(data):
    result = []
    for item in data:  # Which line is slow?
        processed = complex_calculation(item)
        result.append(processed)
    return result

# Run: kernprof -l -v script.py
```

**Memory profiling:**
```python
# Install: pip install memory-profiler
from memory_profiler import profile

@profile
def memory_heavy_function():
    large_list = [i**2 for i in range(10**6)]
    # Memory usage measured line-by-line
    filtered = [x for x in large_list if x % 2 == 0]
    return sum(filtered)

# Run: python -m memory_profiler script.py
```

## Algorithmic Optimization

### 3. Choose Optimal Data Structures

**Critical decisions impact performance dramatically:**
```python
# Slow: O(n) lookup for each item
def find_duplicates_slow(items):
    duplicates = []
    for i, item in enumerate(items):
        if item in items[:i]:  # O(n) list search
            duplicates.append(item)
    return duplicates
# Time: O(n²) for 10K items = ~100M operations

# Fast: O(1) lookup with set
def find_duplicates_fast(items):
    seen = set()
    duplicates = set()
    for item in items:
        if item in seen:  # O(1) set lookup
            duplicates.add(item)
        seen.add(item)
    return list(duplicates)
# Time: O(n) for 10K items = 10K operations (10,000x faster)
```

**Data structure selection guide:**
- **List**: Ordered, indexed access O(1), search O(n), insert/delete O(n)
- **Set**: Unordered, membership O(1), no duplicates
- **Dict**: Key-value, lookup O(1), ordered (Python 3.7+)
- **Deque**: Double-ended queue, fast append/pop from both ends O(1)
- **Heapq**: Priority queue, min-heap operations O(log n)
- **Array**: Fixed-type, memory efficient for numeric data

### 4. Avoid Nested Loops

**Replace nested iterations with efficient algorithms:**
```python
from collections import Counter

# Slow: O(n * m) nested loops
def count_matches_slow(list1, list2):
    matches = 0
    for item1 in list1:
        for item2 in list2:
            if item1 == item2:
                matches += 1
    return matches

# Fast: O(n + m) with Counter
def count_matches_fast(list1, list2):
    counter1 = Counter(list1)
    counter2 = Counter(list2)
    return sum(min(counter1[key], counter2[key])
               for key in counter1 if key in counter2)
```

### 5. List Comprehensions vs Loops

**Comprehensions are faster than explicit loops:**
```python
import timeit

# Standard loop: ~200ms for 1M items
def with_loop(n):
    result = []
    for i in range(n):
        result.append(i * 2)
    return result

# List comprehension: ~130ms (35% faster)
def with_comprehension(n):
    return [i * 2 for i in range(n)]

# Generator: ~0.001ms (memory efficient, lazy)
def with_generator(n):
    return (i * 2 for i in range(n))
```

**When to use each:**
- List comprehension: Need full list immediately
- Generator: Process items one at a time (memory efficient)
- Map/filter: Functional style with named functions

## Memory Optimization

### 6. Generators for Large Datasets

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

### 7. Slots for Classes

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

### 8. Memoization for Expensive Calculations

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

## String and I/O Optimization

### 9. String Concatenation

**Avoid repeated string concatenation:**
```python
# Slow: O(n²) due to string immutability
def join_slow(items):
    result = ""
    for item in items:
        result += item  # Creates new string each time
    return result
# 10K items = ~500ms

# Fast: O(n) with join
def join_fast(items):
    return "".join(items)
# 10K items = ~5ms (100x faster)

# For complex formatting
from io import StringIO

def build_string(items):
    buffer = StringIO()
    for item in items:
        buffer.write(f"Item: {item}\n")
    return buffer.getvalue()
```

### 10. Efficient File I/O

**Batch operations reduce system call overhead:**
```python
# Slow: Many small writes (syscall overhead)
def write_slow(data):
    with open('output.txt', 'w') as f:
        for item in data:
            f.write(f"{item}\n")  # One syscall per line

# Fast: Buffered writes
def write_fast(data):
    with open('output.txt', 'w', buffering=65536) as f:  # 64KB buffer
        f.write('\n'.join(map(str, data)))
```

## Acceleration Techniques

### 11. NumPy for Numerical Operations

**Vectorized operations are dramatically faster:**
```python
import numpy as np

# Pure Python: ~500ms for 1M items
def sum_squares_python(n):
    return sum(i**2 for i in range(n))

# NumPy: ~5ms (100x faster)
def sum_squares_numpy(n):
    arr = np.arange(n)
    return np.sum(arr**2)

# Vectorized operations avoid Python loops
data = np.random.rand(1000000)
result = data * 2 + 3  # Single operation on entire array
```

### 12. Numba JIT Compilation

**Compile Python to machine code:**
```python
from numba import jit

# Standard Python: ~2000ms
def monte_carlo_pi(n):
    inside = 0
    for _ in range(n):
        x, y = np.random.random(), np.random.random()
        if x*x + y*y <= 1:
            inside += 1
    return 4 * inside / n

# With JIT: ~50ms (40x faster)
@jit(nopython=True)
def monte_carlo_pi_fast(n):
    inside = 0
    for _ in range(n):
        x, y = np.random.random(), np.random.random()
        if x*x + y*y <= 1:
            inside += 1
    return 4 * inside / n

# First call compiles, subsequent calls are fast
```

**When to use Numba:**
- Numerical algorithms with loops
- Functions called repeatedly
- Array operations not vectorizable
- Need C/Fortran speed without leaving Python

### 13. Multiprocessing for CPU-Bound Work

**Bypass GIL for parallel CPU processing:**
```python
from multiprocessing import Pool
import time

def expensive_cpu_task(n):
    """Simulate CPU-intensive work."""
    return sum(i*i for i in range(n))

# Sequential: ~8 seconds for 8 tasks
def process_sequential(tasks):
    return [expensive_cpu_task(t) for t in tasks]

# Parallel: ~2 seconds with 4 cores (4x speedup)
def process_parallel(tasks, workers=4):
    with Pool(workers) as pool:
        return pool.map(expensive_cpu_task, tasks)

tasks = [10**7] * 8
results = process_parallel(tasks)  # Uses all CPU cores
```

**Multiprocessing guidelines:**
- Use for CPU-bound tasks (computation, not I/O)
- Each process has separate memory (no shared state issues)
- Overhead from process creation and data serialization
- Ideal for embarrassingly parallel problems

### 14. Cython for Critical Code

**Compile Python to C for maximum speed:**
```python
# Python file: expensive.pyx
# cython: language_level=3

def compute_intensive(int n):
    cdef int i, total = 0  # C type declarations
    for i in range(n):
        total += i * i
    return total

# setup.py
from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("expensive.pyx")
)

# Build: python setup.py build_ext --inplace
# Usage: from expensive import compute_intensive
# Speed: 50-100x faster than pure Python
```

**Cython use cases:**
- Performance-critical inner loops
- Interfacing with C libraries
- Numerical computations
- When Numba isn't sufficient

## Common Performance Patterns

### 15. Lazy Evaluation

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

### 16. Database Query Optimization

**Minimize database round trips:**
```python
import sqlite3

# Slow: N+1 query problem
def get_users_with_posts_slow(db):
    cursor = db.cursor()
    users = cursor.execute("SELECT id, name FROM users").fetchall()

    result = []
    for user_id, name in users:
        # One query per user!
        posts = cursor.execute(
            "SELECT title FROM posts WHERE user_id = ?",
            (user_id,)
        ).fetchall()
        result.append({'name': name, 'posts': posts})
    return result

# Fast: Single JOIN query
def get_users_with_posts_fast(db):
    cursor = db.cursor()
    query = """
        SELECT u.name, p.title
        FROM users u
        LEFT JOIN posts p ON u.id = p.user_id
    """
    rows = cursor.execute(query).fetchall()

    # Group in Python (one query total)
    from itertools import groupby
    result = []
    for name, posts in groupby(rows, key=lambda x: x[0]):
        result.append({
            'name': name,
            'posts': [p[1] for p in posts if p[1]]
        })
    return result
```

**Database optimization checklist:**
- Add indexes for frequently queried columns
- Use bulk inserts instead of individual INSERTs
- Select only needed columns, not `SELECT *`
- Use connection pooling for web applications
- Consider read replicas for read-heavy workloads

### 17. Avoid Premature Optimization

**Focus on algorithmic improvements first:**
```python
# DON'T optimize this:
def process_small_list(items):  # items always < 100
    return [x * 2 for x in items]
# Already fast enough

# DO optimize this:
def process_large_dataset(items):  # items = millions
    # Algorithmic improvement matters here
    return optimized_algorithm(items)
```

**Optimization priority:**
1. Algorithm complexity (O(n²) → O(n log n))
2. Data structure choice (list → set for lookups)
3. Language features (comprehensions, built-ins)
4. Caching and memoization
5. Compiled extensions (NumPy, Numba, Cython)
6. Parallelism (multiprocessing, async)

## Profiling Tools Summary

**CPU profiling:**
- `cProfile`: Standard library, function-level profiling
- `line_profiler`: Line-by-line time measurement
- `py-spy`: Sampling profiler (no code changes needed)

**Memory profiling:**
- `memory_profiler`: Line-by-line memory usage
- `tracemalloc`: Built-in memory tracking
- `pympler`: Detailed memory analysis

**Visualization:**
- `snakeviz`: Interactive cProfile visualization
- `pyinstrument`: Statistical profiler with HTML output
- `gprof2dot`: Convert profiling data to graphs

## Performance Testing

**Benchmark improvements to verify gains:**
```python
import timeit

def benchmark_function(func, setup="", number=1000):
    """Measure function execution time."""
    timer = timeit.Timer(
        stmt=f"{func.__name__}()",
        setup=setup,
        globals=globals()
    )
    time_taken = timer.timeit(number=number)
    print(f"{func.__name__}: {time_taken/number*1000:.3f}ms per call")
    return time_taken

# Compare implementations
benchmark_function(slow_version)
benchmark_function(fast_version)
```

## Best Practices Summary

1. **Profile before optimizing** - Measure to find real bottlenecks
2. **Optimize algorithms first** - O(n²) → O(n) beats micro-optimizations
3. **Use appropriate data structures** - Set/dict for lookups, not lists
4. **Leverage built-ins** - C-implemented built-ins are faster than pure Python
5. **Avoid premature optimization** - Optimize hot paths identified by profiling
6. **Use generators for large data** - Reduce memory usage with lazy evaluation
7. **Batch operations** - Minimize overhead from syscalls and network requests
8. **Cache expensive computations** - Use `@lru_cache` or custom caching
9. **Consider NumPy/Numba** - Vectorization and JIT for numerical code
10. **Parallelize CPU-bound work** - Use multiprocessing to utilize all cores

## Resources

- **Python Performance**: https://wiki.python.org/moin/PythonSpeed
- **cProfile**: https://docs.python.org/3/library/profile.html
- **NumPy**: https://numpy.org/doc/stable/user/absolute_beginners.html
- **Numba**: https://numba.pydata.org/
- **Cython**: https://cython.readthedocs.io/
- **High Performance Python** (Book by Gorelick & Ozsvald)
