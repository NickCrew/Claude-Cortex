# WS1: Testing Workstream

## Overview
Systematic expansion of test coverage from baseline 10.83% to target 85%+ across three phases.

## Current Status
- **Phase**: Phase 1 - Core Module Testing (In Progress)
- **Baseline Coverage**: 10.83% (as of Nov 27, 2025)
- **Current Coverage**: 10.83%
- **Target Coverage**: 85%+
- **Tests Collected**: 425 tests (1 error to fix)

## Phase Breakdown

### Phase 1: Core Module Testing (Current)
**Timeline**: Week 1-2
**Target**: 40% coverage
**Focus**: Critical business logic and core modules

**Priority Modules**:
1. `core/agents.py` - Agent system backbone
2. `core/base.py` - Base classes and utilities
3. `intelligence.py` - AI intelligence layer
4. `metrics.py` - Metrics collection
5. `cli.py` - CLI command handlers
6. `analytics.py` - Analytics engine
7. `versioner.py` - Version management

**Status**: 🟡 In Progress
**Tracking**: See `phase1-core.md`

### Phase 2: Integration & TUI Testing
**Timeline**: Week 3-4
**Target**: 65% coverage
**Focus**: Component integration and TUI interactions

**Priority Areas**:
- TUI components (`tui/*.py`)
- Command integration (`cli.py` + `core/`)
- MCP server interactions
- Workflow orchestration
- File system operations

**Status**: 🔴 Not Started
**Tracking**: `phase2-integration.md` (TBD)

### Phase 3: Edge Cases & Polish
**Timeline**: Week 5-6
**Target**: 85%+ coverage
**Focus**: Edge cases, error handling, performance

**Priority Areas**:
- Error handling paths
- Edge case scenarios
- Performance stress tests
- Concurrent operations
- Integration error recovery

**Status**: 🔴 Not Started
**Tracking**: `phase3-polish.md` (TBD)

## Quality Gates

### Phase 1 Gates
- [ ] All core modules ≥60% coverage
- [ ] All critical paths tested
- [ ] No regression in existing tests
- [ ] Test collection error resolved
- [ ] All new tests passing

### Phase 2 Gates
- [ ] TUI components ≥70% coverage
- [ ] Integration tests ≥60% coverage
- [ ] MCP interactions validated
- [ ] Command workflows end-to-end tested
- [ ] Performance baselines established

### Phase 3 Gates
- [ ] Overall coverage ≥85%
- [ ] All error paths tested
- [ ] Edge cases documented and tested
- [ ] Performance targets met
- [ ] Code quality score ≥8/10

## Metrics & Tracking

### Coverage Progress
```
Baseline:    ████░░░░░░░░░░░░░░░░░░░░░░░░░░  10.83%
Phase 1:     ████████████░░░░░░░░░░░░░░░░░░  40%    (Target)
Phase 2:     ███████████████████░░░░░░░░░░░  65%    (Target)
Phase 3:     █████████████████████████░░░░░  85%+   (Target)
```

### Test Count
- **Current**: 425 tests
- **Phase 1 Target**: ~700 tests
- **Phase 2 Target**: ~1100 tests
- **Phase 3 Target**: ~1400 tests

## Next Actions

### Immediate (This Session)
1. ✅ Create WS1 structure
2. ✅ Create Phase 1 tracking doc
3. 🔲 Fix test collection error
4. 🔲 Create skeleton test files
5. 🔲 Begin core module testing

### Short-term (This Week)
1. Complete `test_agents_comprehensive.py`
2. Complete `test_base_comprehensive.py`
3. Expand `test_intelligence_comprehensive.py`
4. Add `test_metrics_comprehensive.py`
5. Begin `test_cli_comprehensive.py`

### Medium-term (Next Week)
1. Complete Phase 1 core modules
2. Validate Phase 1 quality gates
3. Begin Phase 2 planning
4. Establish performance baselines

## Resources

### Documentation
- Baseline Report: `docs/sprints/current/QA_Baseline.md`
- Parallel Plan: `docs/sprints/current/parallel-improvement-plan.md`
- Coverage Report: `htmlcov/index.html`

### Test Utilities
- Conftest: `tests/conftest.py`
- Fixtures: Available for all modules
- Mock helpers: Standard unittest.mock

### Commands
```bash
# Run all tests with coverage
pytest --cov=claude_ctx_py --cov-report=html --cov-report=term

# Run specific module tests
pytest tests/unit/test_agents_comprehensive.py -v

# Check coverage for specific file
pytest --cov=claude_ctx_py.core.agents --cov-report=term-missing

# Collect tests only (no execution)
pytest --collect-only tests/
```

## Workstream Coordination

### Dependencies
- **Blocks**: WS2 (Code Quality) partially - needs test infrastructure
- **Blocked by**: None
- **Parallel with**: WS2 (Code Quality), WS3 (Documentation)

### Communication
- **Daily Updates**: Coverage % and test count
- **Blockers**: Report immediately
- **Completion**: Notify when phase gates passed

## Success Criteria

### Phase 1 Success
- [ ] 40% overall coverage achieved
- [ ] All core modules ≥60% coverage
- [ ] All tests passing
- [ ] Quality gates met
- [ ] Performance acceptable (tests run <2min)

### Overall Success
- [ ] 85%+ overall coverage
- [ ] All modules ≥70% coverage
- [ ] 1400+ tests passing
- [ ] All quality gates met
- [ ] Regression suite stable
- [ ] CI/CD integration complete

---

**Status**: 🟡 Phase 1 In Progress
**Last Updated**: Nov 27, 2025
**Owner**: Testing Workstream (WS1)
