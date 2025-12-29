# WS5: Quality & Error Handling Workstream

**Status**: Active
**Owner**: Workstream Team
**Created**: 2025-11-27
**Last Updated**: 2025-11-27

## Overview

This workstream focuses on improving code quality, error handling patterns, and resource management across the claude-ctx-plugin codebase. The primary objectives are to eliminate technical debt, standardize error handling, and ensure proper resource cleanup.

## Key Objectives

1. **SQLite Resource Management**: Eliminate SQLite resource warnings through proper connection cleanup
2. **Datetime Deprecation**: Replace deprecated `datetime.utcnow()` with modern `datetime.now(timezone.utc)`
3. **Error Handling Standardization**: Establish consistent error handling patterns across all modules
4. **Resource Cleanup**: Implement proper try/finally patterns for all resource usage
5. **Test Quality**: Improve test reliability and eliminate flaky tests

## Current State Assessment

### Error Handling Infrastructure

**Strong Foundation**:
- Well-designed exception hierarchy in `claude_ctx_py/exceptions.py`
- Comprehensive error utilities in `claude_ctx_py/error_utils.py`
- 629 try/except/raise/finally blocks across 38 Python files
- Custom exception classes with recovery hints and actionable messages

**Exception Hierarchy**:
```
ClaudeCtxError (base)
├── FileOperationError
│   ├── SkillNotFoundError
│   ├── DirectoryNotFoundError
│   └── FileAccessError
├── ValidationError
│   ├── YAMLValidationError
│   ├── SkillValidationError
│   ├── VersionFormatError
│   └── DependencyError
│       ├── CircularDependencyError
│       └── MissingDependencyError
├── VersionError
│   ├── VersionCompatibilityError
│   └── NoCompatibleVersionError
├── CommunityError
│   ├── SkillInstallationError
│   └── RatingError
├── MetricsError
│   ├── MetricsFileError
│   ├── InvalidMetricsDataError
│   └── ExportError
└── CompositionError
    └── InvalidCompositionError
```

**Error Utilities Available**:
- `safe_read_file()` - File reading with error handling
- `safe_write_file()` - File writing with error handling
- `safe_load_yaml()` - YAML parsing with validation
- `safe_save_yaml()` - YAML serialization with validation
- `safe_load_json()` - JSON parsing with validation
- `safe_save_json()` - JSON serialization with validation
- `with_file_error_context()` - Decorator for file operations
- `ensure_directory()` - Directory creation with error handling
- `handle_file_operation()` - Generic operation wrapper
- `format_error_for_cli()` - CLI-friendly error formatting

### Issues Identified

#### 1. SQLite Resource Warnings (Priority: HIGH)

**Problem**: SQLite connections not properly closed, causing ResourceWarnings

**Affected Files**:
- `claude_ctx_py/skill_recommender.py` - 7 instances of `conn = sqlite3.connect()` without proper cleanup
- Tests using SQLite connections

**Impact**: Resource leaks, potential file handle exhaustion in long-running processes

**Root Cause**: Mixed usage patterns:
- ✅ GOOD: `skill_rating.py` uses context managers (`with sqlite3.connect()`)
- ❌ BAD: `skill_recommender.py` manually opens/closes connections, prone to resource leaks

#### 2. Deprecated datetime.utcnow() (Priority: MEDIUM)

**Problem**: Using deprecated `datetime.utcnow()` instead of timezone-aware alternatives

**Instances Found** (13 total):
1. `claude_ctx_py/analytics.py:193` - cutoff_date calculation
2. `claude_ctx_py/analytics.py:283` - cutoff calculation
3. `claude_ctx_py/analytics.py:346` - timestamp generation
4. `claude_ctx_py/analytics.py:367` - export timestamp
5. `claude_ctx_py/analytics.py:430` - report generation time
6. `claude_ctx_py/analytics.py:711` - cutoff_date calculation
7. `claude_ctx_py/analytics.py:764` - report timestamp
8. `claude_ctx_py/analytics.py:798` - report generation time
9. `claude_ctx_py/core/base.py:641` - ISO timestamp generation
10. `claude_ctx_py/core/profiles.py:510` - ISO timestamp
11. `claude_ctx_py/core/profiles.py:1264` - report timestamp
12. `tests/unit/test_analytics.py:47` - test data
13. `tests/unit/test_metrics.py:101` - test timestamp

**Impact**:
- DeprecationWarnings in Python 3.12+
- Potential timezone bugs when comparing with timezone-aware datetimes
- Code will break in future Python versions

**Recommended Fix**:
```python
# OLD (deprecated)
from datetime import datetime
timestamp = datetime.utcnow()

# NEW (recommended)
from datetime import datetime, timezone
timestamp = datetime.now(timezone.utc)
```

#### 3. Inconsistent Error Handling Patterns

**Gap Analysis**:
- Some modules use custom exceptions extensively
- Others rely on generic Python exceptions
- Mixed error handling strategies across similar operations

**Modules Needing Review**:
- Database operations (SQLite, metrics)
- File I/O operations
- External service calls
- CLI command execution

## Action Plan

### Phase 1: Critical Fixes (Immediate)

**1.1 SQLite Resource Cleanup** (Estimated: 2-4 hours)
- [ ] Convert all `conn = sqlite3.connect()` to context managers in `skill_recommender.py`
- [ ] Audit tests for proper SQLite cleanup
- [ ] Add linting rule to prevent future violations
- [ ] Document pattern in development guidelines

**Files to Fix**:
- `claude_ctx_py/skill_recommender.py`:
  - Line 101: `_init_database()` - Already has `.close()`, convert to context manager
  - Line 369: `_pattern_based_recommendations()` - Missing error handling
  - Line 444: `_record_recommendations()` - Basic close, needs try/finally
  - Line 458: `record_activation()` - Basic close, needs try/finally
  - Line 479: `learn_from_feedback()` - Basic close, needs try/finally
  - Line 517: `get_recommendation_stats()` - Basic close, needs try/finally
  - Line 578: `record_feedback()` - Basic close, needs try/finally

**Pattern to Apply**:
```python
# BEFORE (unsafe)
conn = sqlite3.connect(self.db_path)
cursor = conn.execute("SELECT ...")
# ... operations ...
conn.close()

# AFTER (safe)
with sqlite3.connect(self.db_path) as conn:
    cursor = conn.execute("SELECT ...")
    # ... operations ...
    # Automatic commit on success, rollback on exception
```

**1.2 Datetime Migration** (Estimated: 1-2 hours)
- [ ] Replace all 13 instances of `datetime.utcnow()` with `datetime.now(timezone.utc)`
- [ ] Update imports to include `timezone`
- [ ] Verify test compatibility
- [ ] Run full test suite

**Priority Order**:
1. Production code (analytics.py, base.py, profiles.py)
2. Test fixtures (test_analytics.py, test_metrics.py)

### Phase 2: Standardization (Short-term)

**2.1 Error Handling Audit** (Estimated: 3-5 hours)
- [ ] Document current error handling patterns
- [ ] Identify modules missing proper error handling
- [ ] Create error handling guidelines
- [ ] Propose standardization for common operations

**2.2 Resource Management Audit** (Estimated: 2-3 hours)
- [ ] Audit all file operations for proper cleanup
- [ ] Check network/socket operations
- [ ] Review temporary file usage
- [ ] Document resource lifecycle patterns

### Phase 3: Enhancement (Medium-term)

**3.1 Error Recovery Mechanisms** (Estimated: 5-8 hours)
- [ ] Implement retry logic for transient failures
- [ ] Add circuit breaker patterns for external services
- [ ] Create graceful degradation strategies
- [ ] Add error telemetry/logging

**3.2 Test Quality Improvements** (Estimated: 4-6 hours)
- [ ] Eliminate flaky tests
- [ ] Add resource cleanup verification
- [ ] Implement test isolation
- [ ] Add negative test cases

### Phase 4: Documentation & Guidelines (Ongoing)

**4.1 Developer Guidelines** (Estimated: 2-3 hours)
- [ ] Document error handling best practices
- [ ] Create resource management checklist
- [ ] Add code review guidelines
- [ ] Provide examples and anti-patterns

**4.2 Code Quality Automation** (Estimated: 3-4 hours)
- [ ] Add pre-commit hooks for common issues
- [ ] Configure linters for error patterns
- [ ] Set up resource leak detection
- [ ] Integrate with CI/CD pipeline

## Success Metrics

### Quantitative Metrics
- **Resource Warnings**: 0 SQLite ResourceWarnings in test runs
- **Deprecation Warnings**: 0 datetime.utcnow() DeprecationWarnings
- **Error Coverage**: 100% of public APIs have proper error handling
- **Test Reliability**: <1% flaky test rate

### Qualitative Metrics
- Consistent error handling patterns across codebase
- Clear recovery hints in all error messages
- Comprehensive error handling documentation
- Developer confidence in error handling approach

## Dependencies

- Access to test suite
- CI/CD pipeline for validation
- Linting tools (pylint, mypy, ruff)
- Code review process

## Risks & Mitigation

### Risk 1: Breaking Changes
**Mitigation**:
- Comprehensive test coverage before changes
- Incremental rollout
- Feature flags for major changes

### Risk 2: Performance Impact
**Mitigation**:
- Benchmark critical paths
- Profile before/after changes
- Monitor production metrics

### Risk 3: Incomplete Migration
**Mitigation**:
- Automated checks in CI/CD
- Code review checklist
- Regular audits

## Related Documents

- [Error Handling Audit](./error-audit.md) - Detailed analysis and action items
- [SQLite Patterns](./sqlite-patterns.md) - Resource management patterns
- [Testing Guidelines](./testing-guidelines.md) - Test quality standards

## Change Log

### 2025-11-27
- Initial workstream setup
- Completed error handling infrastructure audit
- Identified 7 SQLite resource leak locations
- Documented 13 datetime.utcnow() deprecation instances
- Created phased action plan
