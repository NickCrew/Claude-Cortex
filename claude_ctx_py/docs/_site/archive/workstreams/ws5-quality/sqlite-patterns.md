# SQLite Resource Management Patterns

**Purpose**: Standards and patterns for safe SQLite database operations
**Last Updated**: 2025-11-27

## Quick Reference

### ✅ REQUIRED Pattern: Context Manager

```python
with sqlite3.connect(db_path) as conn:
    cursor = conn.execute("SELECT ...")
    results = cursor.fetchall()
    # Automatic commit on success
    # Automatic rollback on exception
    # Automatic connection close
```

### ❌ FORBIDDEN Pattern: Manual Management

```python
conn = sqlite3.connect(db_path)
cursor = conn.execute("SELECT ...")
results = cursor.fetchall()
conn.close()
# ❌ No automatic cleanup
# ❌ Connection leaks on exception
# ❌ No transaction management
```

## Core Patterns

### Pattern 1: Simple Query (Read-Only)

**Use Case**: Reading data without modifications

```python
def get_skill_stats(self, skill_name: str) -> Dict[str, Any]:
    """Fetch statistics for a skill."""
    with sqlite3.connect(self.db_path) as conn:
        cursor = conn.execute(
            """
            SELECT COUNT(*) as total, AVG(rating) as avg_rating
            FROM skill_ratings
            WHERE skill_name = ?
            """,
            (skill_name,)
        )
        row = cursor.fetchone()
        return {
            "total": row[0],
            "avg_rating": row[1]
        }
```

**Benefits**:
- ✅ Automatic connection cleanup
- ✅ Safe parameter binding with `?` placeholders
- ✅ No SQL injection risk

### Pattern 2: Single Write Operation

**Use Case**: Inserting or updating data

```python
def record_rating(self, skill: str, rating: int) -> None:
    """Record a skill rating."""
    with sqlite3.connect(self.db_path) as conn:
        conn.execute(
            """
            INSERT INTO skill_ratings (skill_name, rating, timestamp)
            VALUES (?, ?, ?)
            """,
            (skill, rating, datetime.now(timezone.utc).isoformat())
        )
        conn.commit()  # Explicit commit for clarity
```

**Benefits**:
- ✅ Automatic rollback if INSERT fails
- ✅ Connection closed even on error
- ✅ Explicit commit() for readability

**Note**: Context manager commits automatically on exit, but explicit `conn.commit()` improves readability.

### Pattern 3: Multiple Operations (Transaction)

**Use Case**: Multiple related operations that should succeed or fail together

```python
def transfer_rating(self, from_skill: str, to_skill: str, rating_id: int) -> None:
    """Move a rating from one skill to another (transaction)."""
    with sqlite3.connect(self.db_path) as conn:
        # All operations in one transaction
        conn.execute(
            "DELETE FROM skill_ratings WHERE id = ? AND skill_name = ?",
            (rating_id, from_skill)
        )
        conn.execute(
            """
            INSERT INTO skill_ratings (skill_name, rating, timestamp)
            SELECT ?, rating, timestamp FROM skill_ratings WHERE id = ?
            """,
            (to_skill, rating_id)
        )
        conn.commit()
        # If any operation fails, ALL are rolled back
```

**Benefits**:
- ✅ Atomic operations (all or nothing)
- ✅ Automatic rollback on any error
- ✅ Data consistency guaranteed

### Pattern 4: Complex Query with Error Handling

**Use Case**: Operations that may fail due to data issues

```python
def get_recommendations(self, context_hash: str) -> List[str]:
    """Get skill recommendations with robust error handling."""
    try:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT successful_skills, success_rate
                FROM context_patterns
                WHERE context_hash = ?
                ORDER BY success_rate DESC
                LIMIT 10
                """,
                (context_hash,)
            )

            recommendations = []
            for row in cursor.fetchall():
                try:
                    # Parse JSON data with error handling
                    skills = json.loads(row[0])
                    recommendations.extend(skills)
                except json.JSONDecodeError:
                    # Skip corrupted data, continue processing
                    continue

            return recommendations

    except sqlite3.Error as exc:
        raise MetricsFileError(
            str(self.db_path),
            "query recommendations",
            f"Database error: {exc}"
        ) from exc
```

**Benefits**:
- ✅ Graceful handling of corrupted data
- ✅ Preserves exception chain
- ✅ Clear error messages
- ✅ Continues processing on partial failures

### Pattern 5: Database Initialization

**Use Case**: Creating tables and indexes

```python
def _init_database(self) -> None:
    """Initialize database schema."""
    self.db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(self.db_path) as conn:
        # Create tables
        conn.execute("""
            CREATE TABLE IF NOT EXISTS skill_ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_name TEXT NOT NULL,
                rating INTEGER NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)

        # Create indexes
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_skill_name
            ON skill_ratings(skill_name)
        """)

        conn.commit()
```

**Benefits**:
- ✅ Idempotent (safe to run multiple times)
- ✅ Automatic schema creation
- ✅ Single transaction for all schema changes

### Pattern 6: Conditional Updates

**Use Case**: Update or insert based on existence

```python
def update_metrics(self, skill: str, metrics: Dict[str, Any]) -> None:
    """Update or insert skill metrics."""
    with sqlite3.connect(self.db_path) as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO skill_metrics
            (skill_name, avg_rating, total_ratings, last_updated)
            VALUES (?, ?, ?, ?)
            """,
            (
                skill,
                metrics["avg_rating"],
                metrics["total_ratings"],
                datetime.now(timezone.utc).isoformat()
            )
        )
        conn.commit()
```

**Benefits**:
- ✅ Upsert operation (update or insert)
- ✅ No need for separate SELECT
- ✅ Atomic operation

## Advanced Patterns

### Pattern 7: Row Factory for Named Access

**Use Case**: Access results by column name instead of index

```python
def get_skill_details(self, skill_name: str) -> Dict[str, Any]:
    """Get skill details with named column access."""
    with sqlite3.connect(self.db_path) as conn:
        # Enable row factory for named access
        conn.row_factory = sqlite3.Row

        cursor = conn.execute(
            "SELECT skill_name, avg_rating, total_ratings FROM skills WHERE skill_name = ?",
            (skill_name,)
        )
        row = cursor.fetchone()

        if not row:
            return {}

        # Access by column name
        return {
            "name": row["skill_name"],
            "rating": row["avg_rating"],
            "total": row["total_ratings"]
        }
```

**Benefits**:
- ✅ More readable code
- ✅ Self-documenting
- ✅ Refactoring-safe (column order doesn't matter)

### Pattern 8: Batch Operations

**Use Case**: Inserting many records efficiently

```python
def record_batch_ratings(self, ratings: List[Tuple[str, int, str]]) -> None:
    """Record multiple ratings efficiently."""
    with sqlite3.connect(self.db_path) as conn:
        # Use executemany for batch operations
        conn.executemany(
            """
            INSERT INTO skill_ratings (skill_name, rating, timestamp)
            VALUES (?, ?, ?)
            """,
            ratings
        )
        conn.commit()
```

**Benefits**:
- ✅ Much faster than individual INSERTs
- ✅ Single transaction for all records
- ✅ Automatic rollback if any fails

### Pattern 9: Connection with Timeout

**Use Case**: Prevent indefinite blocking on locked databases

```python
def get_stats_with_timeout(self, skill: str) -> Dict[str, Any]:
    """Query with timeout to prevent blocking."""
    with sqlite3.connect(self.db_path, timeout=5.0) as conn:
        cursor = conn.execute(
            "SELECT * FROM skill_ratings WHERE skill_name = ?",
            (skill,)
        )
        return cursor.fetchall()
```

**Benefits**:
- ✅ Prevents indefinite blocking
- ✅ Fails fast on contention
- ✅ Better for concurrent access

## Common Pitfalls

### Pitfall 1: Forgetting Placeholders

```python
# ❌ WRONG: SQL injection risk
skill_name = "test'; DROP TABLE skills; --"
conn.execute(f"SELECT * FROM skills WHERE name = '{skill_name}'")

# ✅ CORRECT: Safe parameter binding
conn.execute("SELECT * FROM skills WHERE name = ?", (skill_name,))
```

### Pitfall 2: Multiple Connections

```python
# ❌ WRONG: Multiple connections to same database
conn1 = sqlite3.connect(db_path)
conn2 = sqlite3.connect(db_path)
# Risk of locking issues and data corruption

# ✅ CORRECT: Reuse single connection
with sqlite3.connect(db_path) as conn:
    # All operations with same connection
    conn.execute("INSERT ...")
    conn.execute("UPDATE ...")
```

### Pitfall 3: Catching Too Broadly

```python
# ❌ WRONG: Catches all exceptions
try:
    with sqlite3.connect(db_path) as conn:
        conn.execute("SELECT ...")
except Exception:
    pass  # Silently fails, hard to debug

# ✅ CORRECT: Catch specific exceptions
try:
    with sqlite3.connect(db_path) as conn:
        conn.execute("SELECT ...")
except sqlite3.Error as exc:
    raise MetricsFileError(
        str(db_path), "query", str(exc)
    ) from exc
```

### Pitfall 4: No Error on Missing File

```python
# ❌ WRONG: Creates database if missing
conn = sqlite3.connect("/wrong/path/db.sqlite")
# Silently creates file, hard to debug

# ✅ CORRECT: Validate path exists
if not db_path.exists():
    raise FileNotFoundError(f"Database not found: {db_path}")
with sqlite3.connect(db_path) as conn:
    # ...
```

## Testing Patterns

### Pattern: Verify Resource Cleanup

```python
def test_no_resource_leak(tmp_path):
    """Verify database connections are properly closed."""
    db_path = tmp_path / "test.db"

    recommender = SkillRecommender(home=tmp_path)

    # Perform operations
    recommender.get_recommendation_stats()

    # Verify no open connections
    import gc
    gc.collect()  # Force garbage collection

    # Should be able to delete database (no locks)
    db_path.unlink()  # Should not raise "file in use" error
```

### Pattern: Test Transaction Rollback

```python
def test_rollback_on_error(tmp_path):
    """Verify automatic rollback on error."""
    db_path = tmp_path / "test.db"

    recommender = SkillRecommender(home=tmp_path)

    # Record initial state
    with sqlite3.connect(db_path) as conn:
        initial_count = conn.execute("SELECT COUNT(*) FROM ratings").fetchone()[0]

    # Attempt operation that will fail
    with pytest.raises(ValueError):
        recommender.record_invalid_rating()  # Should rollback

    # Verify rollback occurred
    with sqlite3.connect(db_path) as conn:
        final_count = conn.execute("SELECT COUNT(*) FROM ratings").fetchone()[0]

    assert final_count == initial_count, "Transaction should have rolled back"
```

## Migration Guide

### Migrating from Manual to Context Manager

**Before**:
```python
def get_stats(self, skill: str) -> Dict[str, Any]:
    conn = sqlite3.connect(self.db_path)
    cursor = conn.execute("SELECT * FROM stats WHERE skill = ?", (skill,))
    row = cursor.fetchone()
    conn.close()
    return {"total": row[0], "avg": row[1]}
```

**After**:
```python
def get_stats(self, skill: str) -> Dict[str, Any]:
    with sqlite3.connect(self.db_path) as conn:
        cursor = conn.execute("SELECT * FROM stats WHERE skill = ?", (skill,))
        row = cursor.fetchone()
        return {"total": row[0], "avg": row[1]}
```

**Changes**:
1. ✅ Removed `conn = ` assignment
2. ✅ Added `with` statement
3. ✅ Indented operations
4. ✅ Removed `conn.close()`
5. ✅ Added error handling (optional but recommended)

## Performance Considerations

### 1. Connection Pooling

For high-concurrency scenarios, consider connection pooling:

```python
from contextlib import contextmanager

class DatabasePool:
    def __init__(self, db_path: Path, pool_size: int = 5):
        self.db_path = db_path
        self.pool = [sqlite3.connect(db_path) for _ in range(pool_size)]
        self.available = self.pool.copy()

    @contextmanager
    def connection(self):
        conn = self.available.pop()
        try:
            yield conn
        finally:
            self.available.append(conn)
```

### 2. Write-Ahead Logging (WAL)

Enable WAL mode for better concurrent read performance:

```python
def _init_database(self) -> None:
    with sqlite3.connect(self.db_path) as conn:
        # Enable WAL mode for better concurrency
        conn.execute("PRAGMA journal_mode=WAL")
        # ... create tables ...
```

### 3. Batch Commits

For bulk operations, use transactions:

```python
def import_ratings(self, ratings: List[Dict[str, Any]]) -> None:
    """Import many ratings in a single transaction."""
    with sqlite3.connect(self.db_path) as conn:
        # Disable auto-commit for better performance
        for rating in ratings:
            conn.execute(
                "INSERT INTO ratings VALUES (?, ?, ?)",
                (rating["skill"], rating["stars"], rating["timestamp"])
            )
        # Single commit for all operations
        conn.commit()
```

## Linting Rules

Add these to your `.pylintrc` or `pyproject.toml`:

```toml
[tool.pylint.messages_control]
# Require context managers for database connections
enable = [
    "unidiomatic-typecheck",
    "consider-using-with"
]
```

## Pre-commit Hook

Add to `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: check-sqlite-pattern
      name: Check SQLite context managers
      entry: grep -r "= sqlite3.connect" --include="*.py"
      language: system
      pass_filenames: false
      # Fail if pattern found (should use 'with sqlite3.connect')
```

## Summary

### ✅ Always Use
- Context managers (`with sqlite3.connect()`)
- Parameter binding (`?` placeholders)
- Specific exception handling (`sqlite3.Error`)
- Explicit commits for clarity
- Row factories for named access

### ❌ Never Use
- Manual connection management
- String interpolation in SQL
- Broad exception catching
- Multiple simultaneous connections
- Unprotected file paths

### 🎯 Best Practices
1. One connection per operation
2. Short-lived connections
3. Explicit transactions
4. Proper error handling
5. Resource cleanup verification in tests

## References

- [Python sqlite3 documentation](https://docs.python.org/3/library/sqlite3.html)
- [SQLite transaction guide](https://www.sqlite.org/lang_transaction.html)
- [Context managers (PEP 343)](https://peps.python.org/pep-0343/)
