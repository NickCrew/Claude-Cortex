# Test Coverage Plan - Reach 80% Coverage

Complete plan for achieving 80% test coverage across claude-ctx-plugin.

## Executive Summary

**Current State:**
- Test coverage: ~15% (estimated, 3 modules with tests out of 32)
- Modules with tests: `mcp.py`, `analytics.py`, `composer.py`, `versioner.py`, `watch.py`, `intelligence.py`, `metrics.py`
- Modules without tests: 25+ files

**Target State:**
- Test coverage: 80%+
- All core modules tested
- Critical paths covered
- CI/CD integration with coverage reporting

**Timeline:** 4-6 weeks
**Effort:** 11 GitHub issues created, prioritized by impact

## Files Created

1. **`.github/ISSUE_TEMPLATE/test_coverage.md`** - Template for test coverage issues
2. **`GITHUB_ISSUES_TEST_COVERAGE.md`** - Detailed analysis of all needed tests
3. **`CREATE_THESE_ISSUES.md`** - Copy-paste ready GitHub issue content
4. **`scripts/create_test_coverage_issues.sh`** - Automation script for issue creation
5. **`TEST_COVERAGE_PLAN.md`** - This document

## Priority Breakdown

### 🔴 Priority High (Week 1-2) - Core Modules

**Target:** 5 modules, ~2000 lines of test code

| Module | Current | Target | Complexity | Issue # |
|--------|---------|--------|------------|---------|
| `core/base.py` | 0% | 80% | Medium | #1 |
| `core/agents.py` | 0% | 80% | High | #2 |
| `core/modes.py` | 0% | 80% | Low | #3 |
| `core/rules.py` | 0% | 80% | Low | #4 |
| `cli.py` | 10% | 80% | Medium | #5 |

**Why Priority High:**
- Core functionality used by all features
- Entry points (cli.py)
- Dependency graph critical (agents.py)
- File operations need validation (base.py, modes.py, rules.py)

### 🟡 Priority Medium (Week 3-4) - Extended Core

**Target:** 5 modules, ~1500 lines of test code

| Module | Current | Target | Complexity | Issue # |
|--------|---------|--------|------------|---------|
| `core/skills.py` | 0% | 80% | Medium | #6 |
| `core/workflows.py` | 0% | 80% | Medium | #7 |
| `core/context_export.py` | 0% | 80% | Low | #8 |
| `suggester.py` | 0% | 80% | Medium | #9 |
| `cmd_ai.py` | 0% | 80% | High | #10 |

**Why Priority Medium:**
- Important but not critical path
- Less frequently used features
- Can leverage patterns from high-priority tests

### 🟢 Priority Low (Week 5-6) - Utilities & TUI

**Target:** Select high-value components, ~1000 lines of test code

| Module | Current | Target | Complexity | Notes |
|--------|---------|--------|------------|-------|
| `error_utils.py` | 0% | 80% | Low | Utility functions |
| TUI modules | 0-50% | 60% | High | Focus on logic, not rendering |

**Why Priority Low:**
- Utilities with simple logic
- TUI components hard to test (visual)
- Lower ROI for test effort

## Issue Creation

### Manual Creation
Use `CREATE_THESE_ISSUES.md` - copy and paste each issue into GitHub.

### Automated Creation
Use the script:
```bash
./scripts/create_test_coverage_issues.sh
```

**Prerequisites:**
```bash
# Install GitHub CLI
brew install gh

# Authenticate
gh auth login

# Run script
./scripts/create_test_coverage_issues.sh
```

## Testing Strategy

### Test Structure

**File naming:**
- Implementation: `claude_ctx_py/core/agents.py`
- Tests: `tests/unit/test_core_agents.py`

**Test organization:**
```python
"""Tests for claude_ctx_py.core.agents"""

import pytest
from claude_ctx_py.core.agents import list_agents, agent_activate

class TestListAgents:
    """Tests for list_agents function"""

    def test_lists_all_agents(self):
        """Should list all agents"""
        result = list_agents()
        assert len(result) > 0

    def test_filters_disabled(self):
        """Should filter disabled agents"""
        # Test implementation

class TestAgentActivate:
    """Tests for agent_activate function"""

    def test_activates_agent(self):
        """Should activate valid agent"""
        # Test implementation

    def test_handles_dependencies(self):
        """Should activate dependencies"""
        # Test implementation

    def test_error_on_missing_agent(self):
        """Should raise error for missing agent"""
        with pytest.raises(Exception):
            agent_activate("nonexistent")
```

### Coverage Measurement

**Local:**
```bash
# Install coverage tools
pip install pytest pytest-cov

# Run tests with coverage
pytest --cov=claude_ctx_py --cov-report=term-missing

# Generate HTML report
pytest --cov=claude_ctx_py --cov-report=html
open htmlcov/index.html
```

**CI/CD:**
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -e .[dev]
      - run: pytest --cov=claude_ctx_py --cov-report=xml
      - uses: codecov/codecov-action@v2
        with:
          files: ./coverage.xml
```

## Test Patterns

### Pattern 1: File Operations
```python
def test_file_operation(tmp_path):
    """Test file creation/modification"""
    test_file = tmp_path / "test.md"
    test_file.write_text("content")

    result = your_function(test_file)
    assert result == expected
```

### Pattern 2: Mocking External Calls
```python
from unittest.mock import Mock, patch

def test_with_mock():
    """Test with mocked dependency"""
    with patch('claude_ctx_py.core.module.external_call') as mock:
        mock.return_value = "mocked value"
        result = your_function()
        assert mock.called
```

### Pattern 3: Fixtures
```python
# conftest.py
@pytest.fixture
def sample_agent():
    """Provide sample agent data"""
    return {
        "name": "test-agent",
        "dependencies": ["dep1", "dep2"]
    }

# test file
def test_with_fixture(sample_agent):
    """Test using fixture"""
    assert sample_agent["name"] == "test-agent"
```

### Pattern 4: Parametrized Tests
```python
@pytest.mark.parametrize("input,expected", [
    ("value1", "result1"),
    ("value2", "result2"),
    ("value3", "result3"),
])
def test_multiple_inputs(input, expected):
    """Test with multiple inputs"""
    assert your_function(input) == expected
```

## Success Metrics

### Coverage Targets
- **Core modules:** 85%+ coverage
- **CLI:** 80%+ coverage
- **Utilities:** 75%+ coverage
- **TUI:** 60%+ coverage (focus on logic)
- **Overall:** 80%+ coverage

### Quality Metrics
- All tests pass on main branch
- No flaky tests (>95% pass rate)
- Tests run in <2 minutes
- Coverage reported in PR checks
- Badge in README showing coverage

### Process Metrics
- Issues completed per week: 2-3
- Code review for all test additions
- Documentation updated with testing guide

## Timeline & Milestones

### Week 1-2: Foundation (Priority High)
- [ ] Issue #1: core/base.py tested
- [ ] Issue #2: core/agents.py tested
- [ ] Issue #3: core/modes.py tested
- [ ] Issue #4: core/rules.py tested
- [ ] Issue #5: cli.py expanded tests
- **Milestone:** 50% coverage achieved

### Week 3-4: Extension (Priority Medium)
- [ ] Issue #6: core/skills.py tested
- [ ] Issue #7: core/workflows.py tested
- [ ] Issue #8: core/context_export.py tested
- [ ] Issue #9: suggester.py tested
- [ ] Issue #10: cmd_ai.py tested
- **Milestone:** 70% coverage achieved

### Week 5-6: Polish (Priority Low)
- [ ] error_utils.py tested
- [ ] Select TUI components tested
- [ ] CI/CD integration complete
- [ ] Coverage badge added
- **Milestone:** 80% coverage achieved

## Resources

### Documentation
- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov plugin](https://pytest-cov.readthedocs.io/)
- [Testing best practices](https://docs.pytest.org/en/stable/goodpractices.html)

### Reference Tests
- `tests/unit/test_mcp.py` - Comprehensive module testing
- `tests/unit/test_analytics.py` - Class-based testing
- `tests/unit/test_composer.py` - Integration testing

### Tools
- **pytest** - Test framework
- **pytest-cov** - Coverage measurement
- **pytest-xdist** - Parallel test execution
- **pytest-mock** - Mocking utilities
- **codecov** - Coverage reporting service

## Next Steps

1. **Create Issues:**
   ```bash
   ./scripts/create_test_coverage_issues.sh
   ```

2. **Set Up CI/CD:**
   - Add GitHub Actions workflow for tests
   - Configure codecov integration
   - Add coverage badge to README

3. **Start Testing (Week 1):**
   - Pick Issue #1 (core/base.py)
   - Create `tests/unit/test_core_base.py`
   - Write tests for all functions
   - Submit PR with tests

4. **Iterate:**
   - Complete 2-3 issues per week
   - Review and merge test PRs
   - Update coverage metrics
   - Celebrate milestones! 🎉

## Questions?

- **How do I run tests?** `pytest` or `pytest tests/unit/test_file.py`
- **How do I check coverage?** `pytest --cov=claude_ctx_py`
- **Where are the issues?** See `CREATE_THESE_ISSUES.md`
- **Can I contribute?** Yes! Pick an issue labeled `good-first-issue`

---

**Status:** Plan ready, issues ready to create
**Last Updated:** 2025-11-05
