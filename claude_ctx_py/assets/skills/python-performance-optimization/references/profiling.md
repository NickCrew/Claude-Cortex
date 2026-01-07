# Profiling Python Code

## cProfile - Function-Level Profiling

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

## Line-by-Line Profiling

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

## Memory Profiling

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
