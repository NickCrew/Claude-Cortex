# Algorithmic Optimization

## Choose Optimal Data Structures

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

## Avoid Nested Loops

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

## List Comprehensions vs Loops

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

## Database Query Optimization

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
