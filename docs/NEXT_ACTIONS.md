# Next Actions - Week 1 Execution Plan

**Status**: 🟢 Ready to Execute
**Timeline**: Week 1 (Next 5 days)
**Goal**: Coverage 10.83% → 25-30%, Zero warnings, Core guides complete

---

## Immediate Actions (Today/Tomorrow)

### 🔴 Priority 1: Fix Blocking Issues (2-4 hours)

#### A. Complete datetime Migration (1 hour)
**Status**: 8/13 fixed, 5 remaining

**Remaining fixes**:
```bash
# Fix these files:
claude_ctx_py/core/base.py (line 641)
claude_ctx_py/core/profiles.py (lines 510, 1264)
tests/unit/test_analytics.py (line 47)
tests/unit/test_metrics.py (line 101)

# Pattern to replace:
datetime.utcnow() → datetime.now(timezone.utc)
```

**Commands**:
```bash
# 1. Make the fixes
# 2. Run tests to verify
source .venv/bin/activate && pytest -W error::DeprecationWarning
```

**Success**: Zero DeprecationWarnings

---

#### B. Fix SQLite Resource Leaks (2-3 hours)
**Status**: 7 instances identified in skill_recommender.py

**Files to fix**:
```python
# skill_recommender.py - Convert to context managers
# Lines: 101, 369, 444, 458, 479, 517, 578

# Pattern:
# BEFORE:
conn = sqlite3.connect(self.db_path)
cursor = conn.execute("SELECT ...")
conn.close()

# AFTER:
with sqlite3.connect(self.db_path) as conn:
    cursor = conn.execute("SELECT ...")
    # Auto-cleanup
```

**Commands**:
```bash
# 1. Fix the 7 instances
# 2. Verify zero warnings
pytest -W error::ResourceWarning
```

**Success**: Zero ResourceWarnings

---

### 🟡 Priority 2: Start Core Module Testing (4-8 hours)

#### Target: intelligence.py (First comprehensive test)

**Current**: 33.66% coverage
**Target**: 85%+ coverage
**File**: `claude_ctx_py/intelligence.py` (202 lines)

**Create**: `tests/unit/test_intelligence_comprehensive.py`

**Test checklist**:
- [ ] `IntelligentAgent` class
  - [ ] `__init__()` - initialization
  - [ ] `analyze_context()` - main workflow
  - [ ] `recommend_agents()` - recommendation logic
  - [ ] Error handling
- [ ] `ContextDetector` class
  - [ ] `detect_context()` - context building
  - [ ] Git diff parsing
  - [ ] File analysis
  - [ ] Edge cases
- [ ] `PatternLearner` class
  - [ ] `learn_patterns()` - pattern extraction
  - [ ] `match_patterns()` - pattern matching
  - [ ] Session history loading
  - [ ] Edge cases

**Commands**:
```bash
# 1. Create test file
# 2. Run with coverage
pytest tests/unit/test_intelligence_comprehensive.py --cov=claude_ctx_py/intelligence.py --cov-report=term-missing

# 3. Iterate until ≥85%
```

**Time estimate**: 4-6 hours
**Success**: ≥85% coverage, all tests passing

---

#### Parallel: agents.py testing

**Current**: 13.45% coverage
**Target**: 80%+ coverage
**File**: `claude_ctx_py/core/agents.py` (513 lines)

**Create**: `tests/unit/core/test_agents_comprehensive.py`

**Test checklist**:
- [ ] Agent CRUD operations (list, add, remove)
- [ ] Agent activation logic
- [ ] Dependency resolution
- [ ] CLAUDE.md file updates
- [ ] Error handling (missing files, invalid agents)
- [ ] Edge cases

**Time estimate**: 6-8 hours
**Success**: ≥80% coverage

---

### 🟢 Priority 3: Documentation (2-4 hours)

#### A. Contributor Getting Started Guide

**Create**: `docs/CONTRIBUTING.md`

**Sections**:
1. Development setup (venv, dependencies)
2. Running tests (`make test`, `make test-cov`)
3. Code style (`make lint`, `make type-check`)
4. Git workflow (branch, commit, PR)
5. Code review process
6. Testing conventions
7. Common tasks (adding tests, fixing bugs)

**Time estimate**: 2-3 hours

---

#### B. Testing Conventions Guide

**Create**: `docs/guides/testing-conventions.md`

**Sections**:
1. Test structure and organization
2. Naming conventions
3. Test markers (unit, integration, slow)
4. Mocking patterns
5. Coverage expectations (80% core, 70% TUI)
6. Examples of good tests

**Time estimate**: 1-2 hours

---

## Week 1 Schedule

### Day 1 (Today/Tomorrow)
**Focus**: Quick fixes + Setup first test

- [ ] **Morning (2-3h)**:
  - Fix remaining 5 datetime deprecations (1h)
  - Fix 3-4 SQLite resource leaks (2h)
  - Verify zero warnings

- [ ] **Afternoon (3-4h)**:
  - Set up `test_intelligence_comprehensive.py`
  - Write first 10-15 tests for IntelligentAgent
  - Measure coverage progress

**Goal**: Zero warnings, intelligence.py at 50%+

---

### Day 2
**Focus**: Complete intelligence.py, start agents.py

- [ ] **Morning (3-4h)**:
  - Complete intelligence.py tests (target 85%)
  - Fix edge cases
  - Run full test suite

- [ ] **Afternoon (3-4h)**:
  - Start agents.py comprehensive tests
  - Write first 15-20 tests
  - Measure coverage

**Goal**: intelligence.py ≥85%, agents.py at 40%+

---

### Day 3
**Focus**: Complete agents.py, start base.py

- [ ] **Morning (3-4h)**:
  - Complete agents.py tests (target 80%)
  - Verify all edge cases covered

- [ ] **Afternoon (3-4h)**:
  - Start base.py tests
  - Write CONTRIBUTING.md
  - Write testing-conventions.md

**Goal**: agents.py ≥80%, documentation started

---

### Day 4
**Focus**: Continue core module testing

- [ ] **Morning (3-4h)**:
  - Continue base.py testing
  - Target 50%+ coverage

- [ ] **Afternoon (3-4h)**:
  - Start cmd_ai.py tests (currently 0%)
  - Review and refine existing tests

**Goal**: base.py at 50%+, cmd_ai.py started

---

### Day 5
**Focus**: Integration, review, planning

- [ ] **Morning (2-3h)**:
  - Write first integration test
  - Run full test suite
  - Measure week's progress

- [ ] **Afternoon (2-3h)**:
  - Week 1 retrospective
  - Plan Week 2
  - Document learnings

**Goal**: Week 1 goals met, Week 2 planned

---

## Week 1 Success Criteria

### Must Have ✅
- [ ] Zero pytest warnings ✅ (DONE)
- [ ] Zero resource warnings ❌ (TODO)
- [ ] Zero deprecation warnings ❌ (TODO: 5 remaining)
- [ ] intelligence.py ≥85% coverage
- [ ] agents.py ≥80% coverage
- [ ] Overall coverage ≥25%

### Should Have 📋
- [ ] base.py ≥50% coverage
- [ ] cmd_ai.py ≥40% coverage
- [ ] CONTRIBUTING.md complete
- [ ] testing-conventions.md complete
- [ ] 50+ new tests written

### Nice to Have ✨
- [ ] First integration test
- [ ] TUI testing framework prototype
- [ ] Additional module tests (metrics, analytics)

---

## Commands Reference

### Run Tests
```bash
# Fast unit tests only
source .venv/bin/activate && pytest -m "unit and fast"

# All tests with coverage
pytest --cov=claude_ctx_py --cov-report=term-missing --cov-report=html

# Specific module with coverage
pytest tests/unit/test_intelligence_comprehensive.py \
  --cov=claude_ctx_py/intelligence.py \
  --cov-report=term-missing

# Check for warnings
pytest -W error::DeprecationWarning
pytest -W error::ResourceWarning
```

### Check Code Quality
```bash
# Format code
make lint-fix

# Type checking
make type-check

# Full quality check
make lint && make type-check && make test-cov
```

### Coverage Reports
```bash
# Generate HTML report
pytest --cov=claude_ctx_py --cov-report=html
open htmlcov/index.html

# Check coverage gate
pytest --cov=claude_ctx_py --cov-fail-under=25
```

---

## Tracking Progress

### Daily Updates
Update `docs/workstreams/ws1-testing/status.md` daily:
- Coverage % (overall and per-module)
- Tests added
- Tests passing
- Issues encountered
- Next day plan

### Metrics to Track

| Day | Overall % | intelligence.py | agents.py | base.py | Tests | Warnings |
|-----|-----------|-----------------|-----------|---------|-------|----------|
| Day 0 | 10.83% | 33.66% | 13.45% | 15.18% | 458 | 34+14 |
| Day 1 | ? | ? | ? | ? | ? | 0 (goal) |
| Day 2 | ? | 85% (goal) | ? | ? | ? | 0 |
| Day 3 | ? | ≥85% | 80% (goal) | ? | ? | 0 |
| Day 4 | ? | ≥85% | ≥80% | 50% (goal) | ? | 0 |
| Day 5 | 25%+ (goal) | ≥85% | ≥80% | ≥50% | 500+ | 0 |

---

## Getting Help

### Resources
- **Plan**: `docs/plans/parallel-improvement-plan.md`
- **Baseline**: `docs/reports/QA_Baseline.md`
- **WS1 Status**: `docs/workstreams/ws1-testing/status.md`
- **Architecture**: `docs/architecture/README.md`

### Questions?
- Check documentation first
- Review existing test patterns (`tests/unit/test_metrics.py` is excellent)
- Ask in team channel
- Create GitHub issue if blocked

---

## Parallel Work (Other Workstreams)

While WS1 focuses on core testing, these continue in parallel:

**WS4: Documentation** (Continuous)
- Complete contributor guides
- Refine architecture docs
- Add examples

**WS5: Quality** (Continuous)
- Monitor code reviews
- Track technical debt
- Fix issues as found

**WS6: CI/CD** (Phase 1 complete)
- Monitor CI performance
- Adjust coverage gates as we progress
- Add pre-commit hooks

---

## Week 1 End Goal

By Friday:
- ✅ 25-30% overall coverage (was 10.83%)
- ✅ 3-4 core modules well-tested (≥80%)
- ✅ Zero warnings of any kind
- ✅ 500+ tests (was 458)
- ✅ Core contributor docs complete
- ✅ Strong foundation for Week 2

---

## Let's Go! 🚀

**Start with**: Fix the 5 remaining datetime deprecations (1 hour)
**Then**: Fix SQLite resource leaks (2 hours)
**Then**: Start intelligence.py comprehensive tests (4 hours)

**Total Day 1**: 6-8 hours of focused work
**Impact**: MAJOR (warnings → 0, first module → 85%)

**Ready?** Let's build something great! 💪
