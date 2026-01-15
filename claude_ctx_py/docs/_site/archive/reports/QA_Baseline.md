# QA Baseline Report

**Generated**: 2025-11-27
**Project**: claude-ctx-plugin
**Branch**: main
**Commit**: b8d4e59 (HEAD -> main)

---

## Executive Summary

This baseline establishes the starting point for the comprehensive improvement plan. The project currently has **10.83% code coverage** with **458 total tests** (42 unit tests passing in the fast suite). The majority of the codebase lacks test coverage, particularly in the `core/` modules and TUI components.

### Key Findings

- ✅ **Tests Passing**: 42/42 unit tests (100% pass rate)
- ❌ **Coverage**: 10.83% overall (target: 75-80%)
- ⚠️ **Pytest Markers**: Not properly registered (34 warnings)
- ⚠️ **Resource Warnings**: SQLite connections not being closed
- ⚠️ **Deprecation**: `datetime.utcnow()` deprecated in Python 3.13

---

## Test Coverage Baseline

### Overall Metrics

| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| **Overall Coverage** | 10.83% | 75-80% | -64-69% |
| **Core Modules** | ~15% | 80% | -65% |
| **TUI Modules** | ~0% | 70% | -70% |
| **Tests Passing** | 42/42 | All | ✅ |
| **Total Test Count** | 458 | 600+ | Need ~142+ |

### Coverage by Module Category

#### Excellent Coverage (≥80%)
- `claude_ctx_py/metrics.py`: **82.07%** ✅
- `claude_ctx_py/skill_rating_prompts.py`: **83.14%** ✅
- `claude_ctx_py/__init__.py`: **100%** ✅
- `claude_ctx_py/core/__init__.py`: **100%** ✅

#### Good Coverage (60-79%)
- `claude_ctx_py/analytics.py`: **59.09%** (close)
- `claude_ctx_py/core/rules.py`: **60.00%**
- `claude_ctx_py/core/modes.py`: **55.56%**
- `claude_ctx_py/skill_rating.py`: **58.86%**

#### Poor Coverage (20-59%)
- `claude_ctx_py/exceptions.py`: **39.05%**
- `claude_ctx_py/intelligence.py`: **33.66%**
- `claude_ctx_py/slash_commands.py`: **30.38%**
- `claude_ctx_py/error_utils.py`: **27.82%**

#### Critical Gaps (0-20%)
- `claude_ctx_py/tui/main.py`: **0.00%** ❌ (2,914 lines)
- `claude_ctx_py/cli.py`: **5.60%** ❌ (696 lines)
- `claude_ctx_py/core/skills.py`: **5.36%** ❌ (746 lines)
- `claude_ctx_py/core/agents.py`: **13.45%** ❌ (513 lines)
- `claude_ctx_py/core/base.py`: **15.18%** ❌ (527 lines)
- `claude_ctx_py/core/profiles.py`: **7.67%** ❌ (613 lines)
- `claude_ctx_py/core/mcp.py`: **12.06%** ❌ (431 lines)
- `claude_ctx_py/cmd_ai.py`: **0.00%** ❌ (131 lines)
- All `tui_*.py` modules: **0-10%** ❌

### Coverage by Workstream Priority

#### WS1: Testing Workstream Focus

**Phase 1: Core Modules (Weeks 1-4)**
- High Priority (0-20% coverage):
  - `intelligence.py`: 33.66% → 85%+ (gap: -51%)
  - `core/agents.py`: 13.45% → 80%+ (gap: -67%)
  - `core/base.py`: 15.18% → 80%+ (gap: -65%)
  - `core/skills.py`: 5.36% → 80%+ (gap: -75%)
  - `core/profiles.py`: 7.67% → 80%+ (gap: -72%)
  - `core/mcp.py`: 12.06% → 80%+ (gap: -68%)

**Phase 2: TUI Testing (Weeks 3-6)**
- Critical Priority (0% coverage):
  - `tui/main.py`: 0% → 70%+ (2,914 lines!)
  - `tui_textual.py`: Would be part of main.py
  - All other `tui_*.py` modules: 0-10% → 70%+

**Phase 3: Integration (Weeks 4-8)**
- Current: Minimal integration tests in `tests/integration/test_cli.py`
- Target: 5+ major flow tests with ≥60% integration coverage

---

## Test Execution Baseline

### Current Test Suite Structure

```
tests/
├── integration/
│   └── test_cli.py                   # Only integration test file
└── unit/
    ├── test_activator.py             # Some coverage
    ├── test_analytics.py             # Good coverage ✅
    ├── test_community.py             # Minimal
    ├── test_completions.py           # (not run in fast suite)
    ├── test_intelligence.py          # (not run in fast suite)
    ├── test_metrics.py               # Excellent coverage ✅
    ├── test_skill_rating_prompts.py  # Excellent coverage ✅
    └── test_tui_mcp.py               # Minimal coverage
```

### Test Execution Metrics

| Metric | Value |
|--------|-------|
| **Total Tests** | 458 tests |
| **Fast Unit Tests** | 42 tests |
| **Tests Run** | 42 selected, 416 deselected |
| **Execution Time** | 4.99 seconds |
| **Pass Rate** | 100% (42/42) |
| **Warnings** | 34 (pytest markers) |
| **Resource Warnings** | 14 (SQLite connections) |

### Test Markers Status

**Current Issues:**
- ❌ Pytest markers not registered in `pytest.ini`
- ⚠️ Markers used: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`
- ⚠️ Unknown marker warnings causing noise

**Required Action (WS6):**
Register markers in `pytest.ini`:
```ini
[pytest]
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (slower, cross-component)
    slow: Slow tests (skip by default)
    fast: Fast tests (include in pre-commit)
    tui: TUI-specific tests
    cli: CLI-specific tests
    core: Core module tests
    intelligence: AI/Intelligence tests
    smoke: Smoke tests for basic functionality
    regression: Regression tests for bug fixes
```

---

## Issue Analysis

### 1. SQLite Resource Warnings (14 instances)

**Issue**: Unclosed database connections in SQLite tests
```
ResourceWarning: unclosed database in <sqlite3.Connection object at 0x...>
```

**Impact**: Potential resource leaks, test pollution
**Priority**: Medium
**Workstream**: WS5 (Quality)
**Action**: Add proper connection cleanup in test teardown

### 2. Deprecated `datetime.utcnow()` (5 instances)

**Files affected:**
- `claude_ctx_py/analytics.py` (lines 193, 283, 764, 798)
- Test files using it indirectly

**Issue**: `datetime.utcnow()` deprecated in Python 3.13
```python
# Current (deprecated):
datetime.utcnow()

# Should be:
datetime.now(datetime.UTC)
```

**Impact**: Future Python version incompatibility
**Priority**: Medium
**Workstream**: WS5 (Quality)
**Action**: Replace all instances with timezone-aware `datetime.now(datetime.UTC)`

### 3. Pytest Unknown Markers (34 warnings)

**Issue**: Test markers not registered causing warnings noise

**Priority**: High
**Workstream**: WS6 (CI/CD)
**Action**: Register all markers in `pytest.ini` (Week 2)

### 4. Coverage Failure Gate

**Issue**: Coverage gate set to 80%, currently at 10.83%
```
ERROR: Coverage failure: total of 10.83 is less than fail-under=80.00
```

**Priority**: Critical
**Workstream**: WS6 (CI/CD)
**Action**:
- Temporarily lower gate to 15% (current reality + buffer)
- Incrementally increase as coverage improves
- Target progression: 15% → 30% → 50% → 65% → 80%

---

## Module-Level Coverage Detail

### Modules with 0% Coverage (Critical Priority)

| Module | Lines | Priority | Workstream |
|--------|-------|----------|------------|
| `tui/main.py` | 2,914 | CRITICAL | WS1 Phase 2 |
| `cmd_ai.py` | 131 | HIGH | WS1 Phase 1 |
| `completions.py` | 25 | MEDIUM | WS1 Phase 3 |
| `init_cmds.py` | 192 | MEDIUM | WS1 Phase 3 |
| `shell_integration.py` | 140 | LOW | WS1 Phase 4 |
| `skill_recommender.py` | 190 | HIGH | WS1 Phase 2 |
| `suggester.py` | 130 | MEDIUM | WS1 Phase 3 |
| `core/mode_metadata.py` | 98 | MEDIUM | WS1 Phase 2 |
| All `tui_*.py` modules | ~3,500 | CRITICAL | WS1 Phase 2 |

### High-Value Testing Targets (Week 1-2)

Priority modules for immediate test development:

1. **`intelligence.py`** (202 lines, 33.66%)
   - Core AI functionality
   - `IntelligentAgent`, `ContextDetector`, `PatternLearner`
   - High business value
   - Target: 85%+

2. **`core/agents.py`** (513 lines, 13.45%)
   - Agent activation and management
   - Critical for core functionality
   - Target: 80%+

3. **`core/context.py`** (part of base.py, 527 lines, 15.18%)
   - Context detection and analysis
   - Used by intelligence system
   - Target: 85%+

4. **`cmd_ai.py`** (131 lines, 0%)
   - AI command interface
   - User-facing functionality
   - Target: 75%+

---

## Performance Baseline

### Test Execution Performance

| Metric | Value | Target |
|--------|-------|--------|
| **Fast Unit Suite** | 4.99s | <5s ✅ |
| **Full Test Suite** | Not measured | <30s |
| **Coverage Generation** | ~5s | <10s ✅ |

**Note**: Performance baselines for application runtime not captured. Should be added in WS3 (Performance Monitoring).

---

## CI/CD Configuration Audit

### Current CI Setup

**File**: `.github/workflows/` (to be analyzed in WS6)

### Current Makefile Targets

```makefile
test          # Run full test suite
test-cov      # Run with coverage reports
lint          # black --check
lint-fix      # black formatting
type-check    # mypy on Phase 4 modules only
type-check-all # mypy on all modules (informational)
clean         # Remove build artifacts
```

### Issues Identified

1. **No CI coverage gate** (currently fails locally)
2. **Test markers not organized** (unit vs integration vs slow)
3. **No performance regression testing**
4. **Limited mypy coverage** (only "Phase 4" modules)
5. **No automated quality gates** beyond basic tests

### Recommended Additions (WS6)

- [ ] Coverage gate (progressive: 15% → 30% → 50% → 65% → 80%)
- [ ] Test marker-based execution (`pytest -m "unit and fast"`)
- [ ] Performance benchmarking
- [ ] Security scanning (bandit)
- [ ] Dependency vulnerability scanning
- [ ] Pre-commit hooks
- [ ] Branch protection rules

---

## Technical Debt Baseline

### Code Quality Issues

1. **Massive TUI file** (`tui/main.py`): 2,914 lines
   - Should be <500 lines per file
   - Needs refactoring (WS2)

2. **Large core modules**:
   - `core/skills.py`: 746 lines
   - `core/cli.py`: 696 lines
   - `core/profiles.py`: 613 lines
   - `core/base.py`: 527 lines
   - `core/agents.py`: 513 lines

3. **Low test coverage**: 10.83% overall

4. **No TUI testing**: 0% coverage on UI components

5. **Deprecation warnings**: Python 3.13 compatibility issues

### Estimated Test Gap

**Current**: 458 tests, ~42 running in fast suite
**Needed**:
- Core modules: ~150-200 tests
- TUI components: ~100-150 tests
- Integration: ~20-30 tests
- **Total needed**: ~600-700 tests (~142-242 additional tests)

---

## Workstream Readiness Assessment

### WS1: Testing (READY ✅)
- Baseline captured ✅
- Coverage reports generated ✅
- High-priority targets identified ✅
- Test framework working ✅

### WS2: Refactoring (READY ✅)
- Large files identified ✅
- Refactoring candidates prioritized ✅
- Can proceed after Phase 1 testing ✅

### WS3: Features (BLOCKED ⏸️)
- Depends on WS2 refactoring
- Should start Week 5 ⏸️

### WS4: Documentation (READY ✅)
- Current state documented ✅
- Architecture can be mapped ✅
- Can proceed in parallel ✅

### WS5: Quality (READY ✅)
- Issues identified ✅
- Error handling gaps known ✅
- Can start error audit ✅

### WS6: CI/CD (READY ✅)
- Current config audited ✅
- Improvements identified ✅
- Can start immediately ✅

---

## Next Actions (Week 0 Remaining)

### Immediate (Days 2-3)
- [ ] Set up GitHub project board (WS tracking)
- [ ] Create workstream documentation directories
- [ ] Register pytest markers in `pytest.ini`
- [ ] Lower coverage gate to 15% (realistic baseline)
- [ ] Create initial test skeleton files for core modules

### Week 1 Priorities
- [ ] **WS1**: Start core module testing (intelligence.py, agents.py)
- [ ] **WS5**: Fix SQLite resource warnings
- [ ] **WS5**: Replace deprecated `datetime.utcnow()`
- [ ] **WS6**: Implement coverage gates and test markers
- [ ] **WS4**: Begin architecture documentation

---

## Success Metrics

### Phase 1 Targets (Weeks 1-4)

| Metric | Baseline | Phase 1 Target | Phase 1 Goal |
|--------|----------|----------------|--------------|
| **Overall Coverage** | 10.83% | 30%+ | ✅ Good progress |
| **Core Coverage** | ~15% | 50%+ | ✅ Major improvement |
| **Tests Passing** | 42/42 | 150+/150+ | ✅ 3x growth |
| **CI Gates** | Failing | Passing | ✅ Unblocked |

### End Goal Targets (Week 10)

| Metric | Baseline | Final Target |
|--------|----------|--------------|
| **Overall Coverage** | 10.83% | 75-80% |
| **Core Coverage** | ~15% | 80%+ |
| **TUI Coverage** | 0% | 70%+ |
| **Integration Coverage** | Minimal | 60%+ |
| **Total Tests** | 458 | 600-700 |
| **All CI Gates** | Failing | Passing |

---

## Appendix: Raw Test Output Summary

### Coverage Summary (Top 20 Worst)

```
Name                                Stmts   Miss   Cover   Gap
tui/main.py                         2914   2914    0.00%  -2914
cli.py                               696    657    5.60%  -657
core/skills.py                       746    706    5.36%  -706
core/profiles.py                     613    566    7.67%  -566
core/base.py                         527    447   15.18%  -447
core/agents.py                       513    444   13.45%  -444
core/mcp.py                          431    379   12.06%  -379
core/scenarios.py                    353    305   13.60%  -305
analytics.py (partial)               374    153   59.09%  -153
cmd_ai.py                            131    131    0.00%  -131
watch.py                             177    149   15.82%  -149
versioner.py                         141    125   11.35%  -125
intelligence.py                      202    134   33.66%  -134
error_utils.py                       133     96   27.82%  -96
exceptions.py                        169    103   39.05%  -103
(+ many more TUI modules at 0%)
```

### Test Execution Summary

```
42 passed, 416 deselected, 34 warnings in 4.99s
- 42 unit tests passed (fast suite)
- 416 tests deselected (integration, slow, other)
- 34 warnings (pytest markers)
- 14 ResourceWarnings (SQLite)
- 5 DeprecationWarnings (datetime.utcnow)
```

---

## Conclusion

This baseline establishes a clear starting point for the comprehensive improvement plan. The project has a solid foundation with **458 tests** and a **100% pass rate** for the fast unit suite. However, **coverage is critically low at 10.83%**, with massive gaps in core modules (intelligence, agents, base) and complete absence of TUI testing.

The improvement plan is feasible with the proposed 6-workstream approach, but will require sustained effort across 10 weeks to reach the 75-80% coverage target. Priority should be given to core business logic testing (WS1 Phase 1) and CI/CD improvements (WS6) to enable the other workstreams to proceed efficiently.

**Status**: ✅ **Ready to launch parallel workstreams**

**Next**: Set up GitHub tracking and begin Week 1 execution.
