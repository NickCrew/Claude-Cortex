# Acceleration Techniques

## NumPy for Numerical Operations

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

## Numba JIT Compilation

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

## Multiprocessing for CPU-Bound Work

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

## Cython for Critical Code

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
