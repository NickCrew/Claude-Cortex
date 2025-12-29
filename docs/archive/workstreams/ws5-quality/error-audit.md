# Error Handling Audit Report

**Date**: 2025-11-27
**Auditor**: WS5 Quality Team
**Scope**: Complete codebase error handling analysis

## Executive Summary

The claude-ctx-plugin project demonstrates **strong error handling foundations** with a well-designed exception hierarchy and comprehensive utility functions. However, there are **critical resource management issues** in SQLite operations and **deprecation warnings** from datetime usage that require immediate attention.

### Key Findings

✅ **Strengths**:
- Well-structured exception hierarchy with 20+ custom exception types
- Comprehensive error utilities for file operations
- Consistent error message formatting with recovery hints
- Good separation between error types and domains

⚠️ **Issues**:
- 7 SQLite connections without proper resource cleanup (HIGH)
- 13 instances of deprecated `datetime.utcnow()` (MEDIUM)
- Inconsistent error handling patterns across similar operations
- Missing error handling in some edge cases

## 1. SQLite Resource Management Issues

### Issue Summary

**Severity**: HIGH
**Impact**: Resource leaks, file handle exhaustion
**Affected Module**: `claude_ctx_py/skill_recommender.py`

### Detailed Analysis

#### Problem Pattern

The `SkillRecommender` class uses manual connection management:

```python
# UNSAFE PATTERN (current code)
conn = sqlite3.connect(self.db_path)
cursor = conn.execute("SELECT ...")
# ... process results ...
conn.close()
```

**Issues with this pattern**:
1. ❌ No exception handling - connection leaks if error occurs
2. ❌ No automatic rollback on failure
3. ❌ Manual close() can be forgotten
4. ❌ ResourceWarning in tests and production

#### Locations Requiring Fix

**File**: `claude_ctx_py/skill_recommender.py`

| Line | Method | Issue | Priority |
|------|--------|-------|----------|
| 101 | `_init_database()` | Manual close, no error handling | HIGH |
| 369 | `_pattern_based_recommendations()` | Manual close, no error handling | HIGH |
| 444 | `_record_recommendations()` | Manual close, no error handling | HIGH |
| 458 | `record_activation()` | Manual close, no error handling | HIGH |
| 479 | `learn_from_feedback()` | Manual close, complex logic, no error handling | CRITICAL |
| 517 | `get_recommendation_stats()` | Manual close, no error handling | HIGH |
| 578 | `record_feedback()` | Manual close, complex logic, no error handling | CRITICAL |

#### Recommended Fix

**Pattern**: Use context managers for automatic cleanup

```python
# SAFE PATTERN (recommended)
with sqlite3.connect(self.db_path) as conn:
    cursor = conn.execute("SELECT ...")
    # ... process results ...
    # Automatic commit on success
    # Automatic rollback on exception
    # Automatic connection close
```

**Benefits**:
- ✅ Automatic resource cleanup
- ✅ Automatic transaction management
- ✅ Exception-safe
- ✅ No ResourceWarnings

#### Reference Implementation

`skill_rating.py` already uses this pattern correctly:

```python
# Line 89 in skill_rating.py - GOOD EXAMPLE
with sqlite3.connect(self.db_path) as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS skill_ratings (
            ...
        )
    """)
    conn.commit()
```

### Recommended Actions

1. **Immediate**: Convert all 7 SQLite operations to context managers
2. **Short-term**: Add linting rule to prevent future violations
3. **Medium-term**: Add integration tests for resource cleanup
4. **Long-term**: Consider connection pooling for performance

### Implementation Example

**Before** (`skill_recommender.py` line 369):
```python
def _pattern_based_recommendations(self, context: SessionContext) -> List[SkillRecommendation]:
    recommendations: List[SkillRecommendation] = []
    context_hash = self._compute_context_hash(context)

    conn = sqlite3.connect(self.db_path)
    cursor = conn.execute("""
        SELECT successful_skills, success_rate
        FROM context_patterns
        WHERE success_rate > 0.7
        ORDER BY last_updated DESC
        LIMIT 10
    """)

    skill_scores: Counter[str] = Counter()
    for row in cursor.fetchall():
        try:
            skills = json.loads(row[0])
            success_rate = row[1]
            for skill in skills:
                skill_scores[skill] += success_rate
        except (json.JSONDecodeError, Exception):
            continue

    conn.close()  # ❌ UNSAFE: Won't execute if exception occurs

    # ... rest of method
```

**After** (recommended):
```python
def _pattern_based_recommendations(self, context: SessionContext) -> List[SkillRecommendation]:
    recommendations: List[SkillRecommendation] = []
    context_hash = self._compute_context_hash(context)

    with sqlite3.connect(self.db_path) as conn:  # ✅ SAFE: Auto cleanup
        cursor = conn.execute("""
            SELECT successful_skills, success_rate
            FROM context_patterns
            WHERE success_rate > 0.7
            ORDER BY last_updated DESC
            LIMIT 10
        """)

        skill_scores: Counter[str] = Counter()
        for row in cursor.fetchall():
            try:
                skills = json.loads(row[0])
                success_rate = row[1]
                for skill in skills:
                    skill_scores[skill] += success_rate
            except (json.JSONDecodeError, Exception):
                continue
    # Connection automatically closed here, even if exception occurred

    # ... rest of method
```

## 2. Deprecated datetime.utcnow() Usage

### Issue Summary

**Severity**: MEDIUM
**Impact**: DeprecationWarnings, future compatibility issues
**Python Version**: Deprecated in Python 3.12+

### Detailed Analysis

#### Problem

`datetime.utcnow()` is deprecated and will be removed in future Python versions. It returns a timezone-naive datetime which can cause bugs when compared with timezone-aware datetimes.

#### Locations Requiring Fix

| File | Line | Context | Priority |
|------|------|---------|----------|
| `claude_ctx_py/analytics.py` | 193 | cutoff_date calculation | HIGH |
| `claude_ctx_py/analytics.py` | 283 | cutoff calculation | HIGH |
| `claude_ctx_py/analytics.py` | 346 | timestamp generation | HIGH |
| `claude_ctx_py/analytics.py` | 367 | export timestamp | HIGH |
| `claude_ctx_py/analytics.py` | 430 | report generation time | HIGH |
| `claude_ctx_py/analytics.py` | 711 | cutoff_date calculation | HIGH |
| `claude_ctx_py/analytics.py` | 764 | report timestamp | HIGH |
| `claude_ctx_py/analytics.py` | 798 | report generation time | HIGH |
| `claude_ctx_py/core/base.py` | 641 | ISO timestamp generation | HIGH |
| `claude_ctx_py/core/profiles.py` | 510 | ISO timestamp | HIGH |
| `claude_ctx_py/core/profiles.py` | 1264 | report timestamp | HIGH |
| `tests/unit/test_analytics.py` | 47 | test data | MEDIUM |
| `tests/unit/test_metrics.py` | 101 | test timestamp | MEDIUM |

**Total**: 13 instances across 5 files

#### Recommended Fix

**Step 1**: Update imports
```python
# Add timezone to imports
from datetime import datetime, timezone, timedelta
```

**Step 2**: Replace all instances
```python
# BEFORE (deprecated)
timestamp = datetime.utcnow()
cutoff = datetime.utcnow() - timedelta(days=30)

# AFTER (recommended)
timestamp = datetime.now(timezone.utc)
cutoff = datetime.now(timezone.utc) - timedelta(days=30)
```

**Step 3**: Update ISO format strings
```python
# BEFORE
iso_timestamp = datetime.utcnow().isoformat() + "Z"

# AFTER (cleaner)
iso_timestamp = datetime.now(timezone.utc).isoformat()
# Or for explicit UTC marker:
iso_timestamp = datetime.now(timezone.utc).replace(tzinfo=timezone.utc).isoformat()
```

### Benefits of Migration

1. ✅ **Future-proof**: Compatible with Python 3.12+ and future versions
2. ✅ **Explicit timezone**: Makes UTC explicit, not implicit
3. ✅ **Type safety**: Better type checking with timezone-aware datetimes
4. ✅ **Bug prevention**: Avoids timezone comparison bugs
5. ✅ **No warnings**: Eliminates DeprecationWarnings

### Migration Priority

**Phase 1** (Immediate): Production code
- `analytics.py` (8 instances)
- `core/base.py` (1 instance)
- `core/profiles.py` (2 instances)

**Phase 2** (Short-term): Test code
- `test_analytics.py` (1 instance)
- `test_metrics.py` (1 instance)

## 3. Error Handling Pattern Analysis

### Current State

The codebase has **629 try/except/raise/finally blocks** across **38 Python files**, indicating extensive error handling coverage.

### Pattern Distribution

| Module Category | Try/Except Count | Assessment |
|----------------|------------------|------------|
| Core modules | 150+ | ✅ Good coverage |
| CLI commands | 80+ | ✅ Good coverage |
| TUI components | 120+ | ✅ Good coverage |
| Utilities | 60+ | ✅ Good coverage |
| Tests | 100+ | ⚠️ Some gaps |

### Strong Patterns Identified

#### 1. File Operations (`error_utils.py`)

**Excellent pattern** - Comprehensive error handling with recovery hints:

```python
def safe_read_file(filepath: Path, encoding: str = "utf-8") -> str:
    """Safely read a file with descriptive error handling."""
    if not filepath.exists():
        raise SkillNotFoundError(filepath.stem, search_paths=[str(filepath.parent)])

    try:
        return filepath.read_text(encoding=encoding)
    except PermissionError as exc:
        raise FileAccessError(str(filepath), "read") from exc
    except UnicodeDecodeError as exc:
        raise UnicodeDecodeError(
            exc.encoding, exc.object, exc.start, exc.end,
            f"Invalid {encoding} encoding in '{filepath}'. Try a different encoding.",
        ) from exc
```

**Why this is good**:
- ✅ Specific error types for different failure modes
- ✅ Preserves exception chain with `from exc`
- ✅ Actionable error messages
- ✅ Clear recovery hints

#### 2. Context Manager Pattern (`skill_rating.py`)

**Good pattern** - Automatic resource cleanup:

```python
with sqlite3.connect(self.db_path) as conn:
    conn.execute("INSERT INTO ...")
    conn.commit()
# Automatic cleanup, even on exception
```

#### 3. Operation Wrapper Pattern (`error_utils.py`)

**Flexible pattern** - Allows graceful degradation:

```python
def handle_file_operation(
    operation: Callable[[], T],
    filepath: Path,
    operation_name: str,
    default_on_error: Optional[T] = None,
) -> Tuple[bool, Optional[T], Optional[str]]:
    """Execute a file operation with consistent error handling."""
    try:
        result = operation()
        return True, result, None
    except FileNotFoundError:
        error = f"File not found: {filepath}"
        if default_on_error is not None:
            return False, default_on_error, error
        raise SkillNotFoundError(...)
    # ... more error handling
```

### Gaps Identified

#### 1. Inconsistent Database Error Handling

**Issue**: Some database operations lack proper error handling

**Example** (`skill_recommender.py` line 479):
```python
def learn_from_feedback(self, skill: str, was_helpful: bool, context_hash: str, comment: Optional[str] = None) -> None:
    conn = sqlite3.connect(self.db_path)
    # ... complex database operations ...
    conn.close()
    # ❌ No error handling for database errors
    # ❌ No transaction management
    # ❌ Connection leaks on error
```

**Recommendation**:
```python
def learn_from_feedback(self, skill: str, was_helpful: bool, context_hash: str, comment: Optional[str] = None) -> None:
    try:
        with sqlite3.connect(self.db_path) as conn:
            # ... complex database operations ...
            conn.commit()
    except sqlite3.Error as exc:
        raise MetricsFileError(
            str(self.db_path),
            "update feedback",
            f"Database error: {exc}"
        ) from exc
```

#### 2. Missing Timeout Handling

**Issue**: No timeout handling for potentially long operations

**Modules Affected**:
- Network operations
- File I/O on network filesystems
- Database queries

**Recommendation**: Add timeout parameters and handle `TimeoutError`

#### 3. Incomplete Exception Chain Preservation

**Issue**: Some error handlers don't preserve exception chain

**Example**:
```python
try:
    operation()
except Exception as exc:
    raise CustomError("Operation failed")  # ❌ Lost exception chain
```

**Recommendation**:
```python
try:
    operation()
except Exception as exc:
    raise CustomError("Operation failed") from exc  # ✅ Preserves chain
```

## 4. Proposed Error Handling Standards

### Standard 1: Resource Management

**Rule**: All resources MUST use context managers or try/finally

```python
# ✅ REQUIRED: Context manager
with open(file_path) as f:
    data = f.read()

# ✅ ACCEPTABLE: Try/finally for complex cleanup
resource = acquire_resource()
try:
    use_resource(resource)
finally:
    resource.cleanup()

# ❌ FORBIDDEN: Manual cleanup without try/finally
resource = acquire_resource()
use_resource(resource)
resource.cleanup()  # Won't run if exception occurs
```

### Standard 2: Database Operations

**Rule**: All database operations MUST use context managers

```python
# ✅ REQUIRED
with sqlite3.connect(db_path) as conn:
    conn.execute("INSERT ...")
    conn.commit()

# ❌ FORBIDDEN
conn = sqlite3.connect(db_path)
conn.execute("INSERT ...")
conn.commit()
conn.close()
```

### Standard 3: Exception Chain Preservation

**Rule**: All exception re-raises MUST preserve chain with `from exc`

```python
# ✅ REQUIRED
try:
    operation()
except ValueError as exc:
    raise CustomError("Failed") from exc

# ❌ FORBIDDEN
try:
    operation()
except ValueError as exc:
    raise CustomError("Failed")  # Lost context
```

### Standard 4: Error Messages

**Rule**: All error messages MUST include:
1. What went wrong
2. Why it matters
3. How to fix it (recovery hint)

```python
# ✅ GOOD
raise FileAccessError(
    filepath="/path/to/file",
    operation="read",
    # Message: "Permission denied: cannot read '/path/to/file'"
    # Hint: "Check file permissions with: ls -l /path/to/file"
)

# ❌ BAD
raise Exception("Error reading file")
```

## 5. Recommended Actions

### Immediate Actions (This Week)

1. **Fix SQLite Resource Leaks** (Priority: CRITICAL)
   - Convert 7 instances in `skill_recommender.py` to context managers
   - Add tests to verify resource cleanup
   - Estimated effort: 2-4 hours

2. **Replace datetime.utcnow()** (Priority: HIGH)
   - Update 11 production instances to `datetime.now(timezone.utc)`
   - Update 2 test instances
   - Run full test suite
   - Estimated effort: 1-2 hours

### Short-term Actions (Next 2 Weeks)

3. **Add Resource Cleanup Tests** (Priority: HIGH)
   - Verify no ResourceWarnings in test suite
   - Add negative tests for error paths
   - Estimated effort: 3-4 hours

4. **Standardize Database Error Handling** (Priority: MEDIUM)
   - Apply consistent error handling to all database operations
   - Add retry logic for transient failures
   - Estimated effort: 4-6 hours

### Medium-term Actions (Next Month)

5. **Error Handling Documentation** (Priority: MEDIUM)
   - Document error handling standards
   - Create code examples and anti-patterns guide
   - Add to developer onboarding
   - Estimated effort: 4-5 hours

6. **Automated Quality Checks** (Priority: MEDIUM)
   - Add pre-commit hooks for common patterns
   - Configure linters for error patterns
   - Add CI/CD quality gates
   - Estimated effort: 6-8 hours

## 6. Success Criteria

### Quantitative Metrics

- [ ] 0 SQLite ResourceWarnings in test runs
- [ ] 0 DeprecationWarnings for datetime usage
- [ ] 100% of database operations use context managers
- [ ] 100% of exceptions preserve chain with `from exc`
- [ ] Test suite passes with `-Werror` (warnings as errors)

### Qualitative Metrics

- [ ] Consistent error handling patterns across codebase
- [ ] Clear, actionable error messages
- [ ] Comprehensive error handling documentation
- [ ] Developer confidence in error handling approach

## 7. Appendix: Error Handling Best Practices

### Best Practice 1: Specific Error Types

Use the most specific error type available:

```python
# ✅ GOOD: Specific error type
if not file.exists():
    raise FileNotFoundError(f"Configuration file not found: {file}")

# ❌ BAD: Generic error
if not file.exists():
    raise Exception("File not found")
```

### Best Practice 2: Error Context

Provide context for debugging:

```python
# ✅ GOOD: Rich context
try:
    process_data(data)
except ValueError as exc:
    raise InvalidMetricsDataError(
        filepath=str(data_file),
        details=f"Invalid value at line {line_num}: {exc}"
    ) from exc

# ❌ BAD: No context
try:
    process_data(data)
except ValueError:
    raise ValueError("Invalid data")
```

### Best Practice 3: Recovery Hints

Always provide actionable recovery hints:

```python
# ✅ GOOD: Clear recovery path
raise FileAccessError(
    filepath="/protected/file",
    operation="write",
    # Hint: "Check file permissions with: ls -l /protected/file"
)

# ❌ BAD: No guidance
raise PermissionError("Cannot write file")
```

### Best Practice 4: Fail Fast

Validate inputs early:

```python
# ✅ GOOD: Validate early
def rate_skill(skill: str, stars: int) -> None:
    if not 1 <= stars <= 5:
        raise ValueError(f"Stars must be 1-5, got {stars}")
    # ... rest of function

# ❌ BAD: Validate late
def rate_skill(skill: str, stars: int) -> None:
    # ... complex operations ...
    if not 1 <= stars <= 5:
        raise ValueError(f"Invalid stars: {stars}")
```

## Conclusion

The claude-ctx-plugin project has a **strong error handling foundation** with well-designed infrastructure. The immediate priority is to address **resource management issues** (SQLite) and **deprecation warnings** (datetime), both of which are straightforward to fix and will significantly improve code quality.

The proposed standards and actions will ensure **consistent, maintainable error handling** across the entire codebase while preserving the existing strong patterns.
