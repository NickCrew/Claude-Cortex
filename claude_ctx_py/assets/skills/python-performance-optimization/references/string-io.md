# String and I/O Optimization

## String Concatenation

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

## Efficient File I/O

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
