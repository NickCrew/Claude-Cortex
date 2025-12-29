# WS5 Quality & Error Handling - Action Plan

**Status**: Ready for Execution
**Priority**: HIGH
**Estimated Total Effort**: 15-25 hours

## Quick Start Checklist

### Phase 1: Critical Fixes (Week 1) - 3-6 hours

- [ ] **SQLite Resource Cleanup** (2-4 hours)
  - [ ] Fix `skill_recommender.py` line 101: `_init_database()`
  - [ ] Fix `skill_recommender.py` line 369: `_pattern_based_recommendations()`
  - [ ] Fix `skill_recommender.py` line 444: `_record_recommendations()`
  - [ ] Fix `skill_recommender.py` line 458: `record_activation()`
  - [ ] Fix `skill_recommender.py` line 479: `learn_from_feedback()` (CRITICAL)
  - [ ] Fix `skill_recommender.py` line 517: `get_recommendation_stats()`
  - [ ] Fix `skill_recommender.py` line 578: `record_feedback()` (CRITICAL)
  - [ ] Run tests to verify no ResourceWarnings
  - [ ] Verify test suite passes

- [ ] **datetime.utcnow() Migration** (1-2 hours)
  - [ ] Fix `analytics.py` (8 instances)
  - [ ] Fix `core/base.py` (1 instance)
  - [ ] Fix `core/profiles.py` (2 instances)
  - [ ] Fix `tests/unit/test_analytics.py` (1 instance)
  - [ ] Fix `tests/unit/test_metrics.py` (1 instance)
  - [ ] Run tests to verify no DeprecationWarnings
  - [ ] Verify test suite passes

### Phase 2: Validation & Testing (Week 2) - 4-6 hours

- [ ] **Resource Cleanup Tests** (2-3 hours)
  - [ ] Add test to verify no ResourceWarnings
  - [ ] Add test to verify database can be deleted after operations
  - [ ] Add test for transaction rollback on error
  - [ ] Add test for concurrent access safety

- [ ] **Error Handling Tests** (2-3 hours)
  - [ ] Add negative tests for database errors
  - [ ] Add tests for corrupted data handling
  - [ ] Add tests for timeout scenarios
  - [ ] Verify exception chain preservation

### Phase 3: Documentation & Standards (Week 3) - 4-6 hours

- [ ] **Development Guidelines** (2-3 hours)
  - [ ] Document error handling standards
  - [ ] Create code review checklist
  - [ ] Add examples and anti-patterns
  - [ ] Update CONTRIBUTING.md

- [ ] **Automation** (2-3 hours)
  - [ ] Add pre-commit hook for SQLite patterns
  - [ ] Configure pylint for error handling
  - [ ] Add CI check for DeprecationWarnings
  - [ ] Add CI check for ResourceWarnings

### Phase 4: Advanced Improvements (Week 4) - 4-7 hours

- [ ] **Error Recovery** (2-4 hours)
  - [ ] Add retry logic for transient database errors
  - [ ] Implement graceful degradation patterns
  - [ ] Add telemetry for error tracking

- [ ] **Performance** (2-3 hours)
  - [ ] Benchmark database operations
  - [ ] Consider connection pooling
  - [ ] Enable WAL mode for better concurrency

## Detailed Task Breakdown

### Task 1: Fix SQLite Resource Leaks

**File**: `claude_ctx_py/skill_recommender.py`

**Priority**: CRITICAL
**Estimated Time**: 2-4 hours
**Dependencies**: None

**Changes Required**:

1. **Line 101: `_init_database()`**
   ```python
   # BEFORE
   conn = sqlite3.connect(self.db_path)
   conn.execute("CREATE TABLE ...")
   conn.commit()
   conn.close()

   # AFTER
   with sqlite3.connect(self.db_path) as conn:
       conn.execute("CREATE TABLE ...")
       conn.commit()
   ```

2. **Line 369: `_pattern_based_recommendations()`**
   - Add context manager
   - Add error handling for database errors
   - Add error handling for JSON parsing

3. **Line 444: `_record_recommendations()`**
   - Add context manager
   - Add error handling for INSERT failures

4. **Line 458: `record_activation()`**
   - Add context manager
   - Add error handling for UPDATE failures

5. **Line 479: `learn_from_feedback()` (CRITICAL)**
   - Add context manager
   - Add comprehensive error handling (complex logic)
   - Add transaction management for multi-step operation

6. **Line 517: `get_recommendation_stats()`**
   - Add context manager
   - Add error handling for query failures

7. **Line 578: `record_feedback()` (CRITICAL)**
   - Add context manager
   - Add comprehensive error handling (complex logic)
   - Add transaction management

**Testing**:
```bash
# Run with warnings enabled
python -W error::ResourceWarning -m pytest tests/

# Should show 0 ResourceWarnings
```

### Task 2: Replace datetime.utcnow()

**Files**: 5 files, 13 instances total

**Priority**: HIGH
**Estimated Time**: 1-2 hours
**Dependencies**: None

**Changes Required**:

1. **Update imports** (all affected files):
   ```python
   # Add timezone to imports
   from datetime import datetime, timezone, timedelta
   ```

2. **Replace all instances**:
   ```python
   # BEFORE
   timestamp = datetime.utcnow()
   cutoff = datetime.utcnow() - timedelta(days=30)
   iso_str = datetime.utcnow().isoformat() + "Z"

   # AFTER
   timestamp = datetime.now(timezone.utc)
   cutoff = datetime.now(timezone.utc) - timedelta(days=30)
   iso_str = datetime.now(timezone.utc).isoformat()
   ```

**File-by-file breakdown**:
- `analytics.py`: 8 instances (lines 193, 283, 346, 367, 430, 711, 764, 798)
- `core/base.py`: 1 instance (line 641)
- `core/profiles.py`: 2 instances (lines 510, 1264)
- `tests/unit/test_analytics.py`: 1 instance (line 47)
- `tests/unit/test_metrics.py`: 1 instance (line 101)

**Testing**:
```bash
# Run with deprecation warnings as errors
python -W error::DeprecationWarning -m pytest tests/

# Should show 0 DeprecationWarnings
```

### Task 3: Add Resource Cleanup Tests

**Priority**: HIGH
**Estimated Time**: 2-3 hours
**Dependencies**: Task 1 complete

**Test Cases to Add**:

1. **Test no ResourceWarnings**:
   ```python
   def test_no_resource_warnings_after_operations():
       """Verify no ResourceWarnings after database operations."""
       import warnings
       with warnings.catch_warnings(record=True) as w:
           warnings.simplefilter("always", ResourceWarning)
           # Perform operations
           recommender = SkillRecommender()
           recommender.get_recommendation_stats()
           # Check warnings
           resource_warnings = [warning for warning in w if issubclass(warning.category, ResourceWarning)]
           assert len(resource_warnings) == 0, f"Found ResourceWarnings: {resource_warnings}"
   ```

2. **Test database can be deleted**:
   ```python
   def test_database_can_be_deleted_after_use(tmp_path):
       """Verify database file can be deleted (no locks)."""
       db_path = tmp_path / "test.db"
       recommender = SkillRecommender(home=tmp_path)
       recommender.get_recommendation_stats()

       import gc
       gc.collect()  # Force cleanup

       # Should not raise "file in use" error
       db_path.unlink()
   ```

3. **Test transaction rollback**:
   ```python
   def test_automatic_rollback_on_error(tmp_path):
       """Verify automatic rollback on exceptions."""
       recommender = SkillRecommender(home=tmp_path)

       # Get initial count
       initial_count = get_rating_count(recommender.db_path)

       # Attempt operation that fails
       with pytest.raises(ValueError):
           recommender.record_invalid_rating()

       # Verify rollback
       final_count = get_rating_count(recommender.db_path)
       assert final_count == initial_count, "Transaction should have rolled back"
   ```

### Task 4: Add Error Handling Documentation

**Priority**: MEDIUM
**Estimated Time**: 2-3 hours
**Dependencies**: None

**Documents to Create**:

1. **Developer Guidelines** (`docs/development/error-handling.md`):
   - Error handling standards
   - Resource management patterns
   - Exception chain preservation
   - Error message guidelines

2. **Code Review Checklist** (`docs/development/code-review.md`):
   - Resource cleanup verification
   - Error handling verification
   - Exception chain verification
   - Error message quality check

3. **Examples Repository** (`docs/examples/error-handling/`):
   - Good patterns
   - Anti-patterns
   - Common pitfalls
   - Migration examples

### Task 5: Add Automation

**Priority**: MEDIUM
**Estimated Time**: 2-3 hours
**Dependencies**: Tasks 1-2 complete

**Automation to Add**:

1. **Pre-commit Hook** (`.pre-commit-config.yaml`):
   ```yaml
   - repo: local
     hooks:
       - id: check-sqlite-context-manager
         name: Check SQLite uses context managers
         entry: bash -c 'if grep -r "= sqlite3.connect" --include="*.py" claude_ctx_py/; then exit 1; fi'
         language: system
         pass_filenames: false

       - id: check-datetime-utcnow
         name: Check no datetime.utcnow()
         entry: bash -c 'if grep -r "datetime.utcnow()" --include="*.py" claude_ctx_py/; then exit 1; fi'
         language: system
         pass_filenames: false
   ```

2. **Pylint Configuration** (`pyproject.toml`):
   ```toml
   [tool.pylint.messages_control]
   enable = [
       "consider-using-with",
       "unidiomatic-typecheck",
   ]
   ```

3. **CI Check** (`.github/workflows/quality.yml`):
   ```yaml
   - name: Check for warnings
     run: |
       python -W error::ResourceWarning -W error::DeprecationWarning -m pytest tests/
   ```

## Progress Tracking

### Week 1 Goals
- [ ] All SQLite resource leaks fixed
- [ ] All datetime.utcnow() instances migrated
- [ ] Test suite passes with no warnings

### Week 2 Goals
- [ ] Resource cleanup tests added
- [ ] Error handling tests added
- [ ] Test coverage >85%

### Week 3 Goals
- [ ] Documentation complete
- [ ] Code review checklist in place
- [ ] Pre-commit hooks configured

### Week 4 Goals
- [ ] Advanced error recovery implemented
- [ ] Performance benchmarks complete
- [ ] CI/CD quality gates active

## Success Criteria

### Must Have (Critical)
- ✅ 0 SQLite ResourceWarnings
- ✅ 0 datetime DeprecationWarnings
- ✅ All tests passing
- ✅ 100% of database ops use context managers

### Should Have (Important)
- ✅ Resource cleanup tests in place
- ✅ Error handling documentation complete
- ✅ Pre-commit hooks configured
- ✅ CI checks enforcing standards

### Nice to Have (Optional)
- ✅ Connection pooling implemented
- ✅ WAL mode enabled
- ✅ Performance benchmarks documented
- ✅ Error telemetry in place

## Risk Management

### Risk: Breaking Existing Functionality
**Probability**: Low
**Impact**: High
**Mitigation**:
- Comprehensive testing before merge
- Code review with domain expert
- Incremental rollout if possible

### Risk: Test Suite Failures
**Probability**: Medium
**Impact**: Medium
**Mitigation**:
- Fix tests alongside code changes
- Verify tests with warnings enabled
- Add regression tests

### Risk: Performance Degradation
**Probability**: Low
**Impact**: Medium
**Mitigation**:
- Benchmark before/after changes
- Profile critical paths
- Monitor production metrics

## Resources

### Documentation
- [SQLite Patterns Guide](./sqlite-patterns.md)
- [Error Audit Report](./error-audit.md)
- [Python datetime docs](https://docs.python.org/3/library/datetime.html)
- [Python sqlite3 docs](https://docs.python.org/3/library/sqlite3.html)

### Tools
- pytest with warnings enabled
- pylint for pattern detection
- pre-commit for automation
- coverage.py for test coverage

### Support
- Python 3.12+ for testing deprecation warnings
- SQLite 3.x for database operations
- pytest 7.x for testing framework

## Next Steps

1. **Immediate**: Start with Task 1 (SQLite fixes)
2. **Short-term**: Complete Task 2 (datetime migration)
3. **Medium-term**: Add tests and documentation
4. **Long-term**: Implement automation and advanced features

## Questions & Decisions

### Q: Should we migrate all at once or incrementally?
**Decision**: Migrate incrementally, starting with critical paths
**Rationale**: Lower risk, easier to test and validate

### Q: Should we add connection pooling now?
**Decision**: No, defer to Phase 4
**Rationale**: Fix critical issues first, optimize later

### Q: Should we enable WAL mode globally?
**Decision**: Yes, but test thoroughly first
**Rationale**: Better concurrency with minimal risk

## Sign-off

- [ ] Technical Lead Review
- [ ] QA Validation
- [ ] Documentation Complete
- [ ] CI/CD Updated
- [ ] Ready for Merge
