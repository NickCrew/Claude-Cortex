# Sequential Execution Plan for claude-ctx-plugin Improvements

**Status**: Ready to execute
**Context**: Day 1 complete (coverage 10.83% → 21.85%, all warnings eliminated)
**Goal**: Systematic path from current state (21.85%) to final target (75-80%)
**Duration**: 9 weeks remaining (Weeks 1-10)

---

## How to Use This Plan

This is a **sequential, step-by-step execution plan** designed to be followed by any developer or AI agent. Each task:
- ✅ Has clear inputs (what you need to start)
- ✅ Has clear outputs (what you produce)
- ✅ Has verification steps (how to confirm success)
- ✅ Has estimated time (for planning)
- ✅ Is self-contained (no ambiguity)

**Execution Model**: Complete each task in order. Verify success before moving to next task.

---

## Current State (Starting Point)

**Date**: 2025-11-27
**Coverage**: 21.85%
**Warnings**: 0
**Tests Passing**: 457/457
**Key Achievements**:
- intelligence.py: 91.09% coverage
- All datetime/SQLite issues fixed
- CONTRIBUTING.md created

**Next Phase**: Complete Week 1 core module testing

---

# Week 1: Core Module Testing (Days 2-5)

**Goal**: 21.85% → 30% coverage
**Focus**: Core business logic modules

---

## Task 1: Test agents.py Comprehensively

**Priority**: 🔴 CRITICAL
**Time Estimate**: 6-8 hours
**Module**: `claude_ctx_py/core/agents.py` (513 lines, 13.45% → 80%)

### Input Requirements
- ✅ File: `claude_ctx_py/core/agents.py`
- ✅ Reference: `tests/unit/test_intelligence_comprehensive.py` (pattern example)
- ✅ Coverage baseline: 13.45%

### Execution Steps

#### Step 1.1: Analyze Module Structure (30 min)
```bash
# Read the file
cat claude_ctx_py/core/agents.py

# Identify key functions/classes
grep -E "^(def|class)" claude_ctx_py/core/agents.py
```

**Output**: List of all public functions and classes to test

#### Step 1.2: Create Test File (15 min)
```bash
# Create test file
cat > tests/unit/core/test_agents_comprehensive.py << 'EOF'
"""Comprehensive tests for agents.py module."""
import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
from pathlib import Path

from claude_ctx_py.core.agents import (
    # Import all public functions/classes here
)

# Test classes will go here
EOF
```

#### Step 1.3: Write Tests for Agent CRUD (2 hours)
**Test scenarios**:
- [ ] List agents from directory
- [ ] List agents with filtering (active/inactive)
- [ ] List agents returns empty list when no agents exist
- [ ] Add new agent creates file correctly
- [ ] Add agent with frontmatter metadata
- [ ] Remove agent deletes file
- [ ] Remove non-existent agent handles error
- [ ] Update agent metadata

**Example test structure**:
```python
@pytest.mark.unit
@pytest.mark.core
class TestAgentListing:
    """Test agent listing functionality."""

    def test_list_agents_empty_directory(self, tmp_path):
        """Test listing agents from empty directory."""
        result = list_agents(tmp_path)
        assert result == []

    def test_list_agents_with_files(self, tmp_path):
        """Test listing agents with existing files."""
        # Create test agent files
        (tmp_path / "agent1.md").write_text("# Agent 1")
        (tmp_path / "agent2.md").write_text("# Agent 2")

        result = list_agents(tmp_path)

        assert len(result) == 2
        assert any(a.name == "agent1" for a in result)
        assert any(a.name == "agent2" for a in result)
```

#### Step 1.4: Write Tests for Agent Activation (2 hours)
**Test scenarios**:
- [ ] Activate agent updates CLAUDE.md
- [ ] Activate agent resolves dependencies
- [ ] Activate already-active agent (idempotent)
- [ ] Activate non-existent agent raises error
- [ ] Deactivate agent updates CLAUDE.md
- [ ] Deactivate agent handles dependencies
- [ ] Multiple activations maintain state

**Example test structure**:
```python
@pytest.mark.unit
@pytest.mark.core
class TestAgentActivation:
    """Test agent activation functionality."""

    def test_activate_agent_updates_claude_file(self, tmp_path):
        """Test activating agent updates CLAUDE.md."""
        agent_path = tmp_path / "agents" / "test-agent.md"
        claude_path = tmp_path / "CLAUDE.md"

        # Setup
        agent_path.parent.mkdir(parents=True)
        agent_path.write_text("# Test Agent")
        claude_path.write_text("# Existing content")

        # Execute
        activate_agent("test-agent", claude_path, tmp_path / "agents")

        # Verify
        content = claude_path.read_text()
        assert "@agents/test-agent.md" in content
```

#### Step 1.5: Write Tests for Dependency Resolution (1.5 hours)
**Test scenarios**:
- [ ] Resolve agent dependencies correctly
- [ ] Handle circular dependencies
- [ ] Handle missing dependencies
- [ ] Resolve transitive dependencies

#### Step 1.6: Write Tests for Error Handling (1 hour)
**Test scenarios**:
- [ ] Invalid agent file format
- [ ] Missing required metadata
- [ ] File I/O errors
- [ ] Permission errors

#### Step 1.7: Measure Coverage (15 min)
```bash
# Run tests with coverage
pytest tests/unit/core/test_agents_comprehensive.py \
  --cov=claude_ctx_py/core/agents.py \
  --cov-report=term-missing \
  -v

# Target: ≥80% coverage
```

#### Step 1.8: Iterate Until Target Met (1-2 hours)
- Identify uncovered lines
- Add tests for missing scenarios
- Re-run coverage
- Repeat until ≥80%

### Output Deliverables
- ✅ File: `tests/unit/core/test_agents_comprehensive.py`
- ✅ Coverage: agents.py ≥80% (was 13.45%)
- ✅ All tests passing

### Verification
```bash
# 1. Run tests
pytest tests/unit/core/test_agents_comprehensive.py -v

# 2. Check coverage
pytest tests/unit/core/test_agents_comprehensive.py \
  --cov=claude_ctx_py/core/agents.py \
  --cov-report=term-missing

# 3. Verify ≥80% coverage
# 4. Verify all tests passing

# Success criteria:
# - Coverage ≥80%
# - All tests pass
# - No flaky tests
```

### Expected Impact
- Coverage: 21.85% → ~28%
- Core module security increased

---

## Task 2: Test base.py to 50%

**Priority**: 🔴 HIGH
**Time Estimate**: 4-6 hours
**Module**: `claude_ctx_py/core/base.py` (527 lines, 15.18% → 50%)

### Input Requirements
- ✅ Task 1 complete (agents.py at 80%)
- ✅ File: `claude_ctx_py/core/base.py`
- ✅ Coverage baseline: 15.18%

### Execution Steps

#### Step 2.1: Analyze Module (30 min)
```bash
# Read and understand base.py
cat claude_ctx_py/core/base.py | head -100

# Identify base classes and utilities
grep -E "^class" claude_ctx_py/core/base.py
```

#### Step 2.2: Prioritize High-Value Functions (15 min)
**Focus on**:
- Base classes used by other modules
- Utility functions with high call frequency
- Error handling and validation

**Strategy**: Test 50% of most critical functionality rather than random coverage

#### Step 2.3: Create Test File (15 min)
```bash
cat > tests/unit/core/test_base_comprehensive.py << 'EOF'
"""Comprehensive tests for base.py module."""
import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from claude_ctx_py.core.base import (
    # Import classes/functions to test
)

# Test classes
EOF
```

#### Step 2.4: Write Tests for Base Classes (2 hours)
**Test scenarios**:
- [ ] Base class initialization
- [ ] Common methods (to_dict, from_dict, validate)
- [ ] Property getters/setters
- [ ] Equality and comparison methods

#### Step 2.5: Write Tests for Utility Functions (1.5 hours)
**Test scenarios**:
- [ ] Path manipulation utilities
- [ ] String formatting utilities
- [ ] Validation functions
- [ ] Helper functions

#### Step 2.6: Write Tests for Error Handling (1 hour)
**Test scenarios**:
- [ ] Invalid inputs raise appropriate errors
- [ ] Edge cases handled gracefully
- [ ] Error messages are clear

#### Step 2.7: Measure and Iterate (30-60 min)
```bash
pytest tests/unit/core/test_base_comprehensive.py \
  --cov=claude_ctx_py/core/base.py \
  --cov-report=term-missing

# Iterate until ≥50%
```

### Output Deliverables
- ✅ File: `tests/unit/core/test_base_comprehensive.py`
- ✅ Coverage: base.py ≥50% (was 15.18%)
- ✅ All tests passing

### Verification
```bash
pytest tests/unit/core/test_base_comprehensive.py \
  --cov=claude_ctx_py/core/base.py \
  --cov-report=term-missing

# Success: ≥50% coverage, all tests pass
```

### Expected Impact
- Coverage: ~28% → ~32%

---

## Task 3: Test cmd_ai.py to 40%

**Priority**: 🟡 MEDIUM
**Time Estimate**: 3-4 hours
**Module**: `claude_ctx_py/cmd_ai.py` (131 lines, 0% → 40%)

### Input Requirements
- ✅ Task 2 complete (base.py at 50%)
- ✅ File: `claude_ctx_py/cmd_ai.py`
- ✅ Coverage baseline: 0%

### Execution Steps

#### Step 3.1: Analyze Module (20 min)
```bash
cat claude_ctx_py/cmd_ai.py
```

**Identify**:
- CLI command handlers
- AI integration points
- User interaction flows

#### Step 3.2: Create Test File (10 min)
```bash
cat > tests/unit/test_cmd_ai.py << 'EOF'
"""Tests for cmd_ai.py module."""
import pytest
from unittest.mock import Mock, patch
from click.testing import CliRunner

from claude_ctx_py.cmd_ai import (
    # Import functions/commands
)

EOF
```

#### Step 3.3: Write Tests for CLI Commands (2 hours)
**Test scenarios**:
- [ ] Command invocation succeeds
- [ ] Command with arguments
- [ ] Command with flags/options
- [ ] Command error handling
- [ ] Command output format

**Use CliRunner for testing**:
```python
from click.testing import CliRunner

def test_ai_recommend_command():
    """Test ai recommend command."""
    runner = CliRunner()
    result = runner.invoke(ai_recommend_cmd, [])

    assert result.exit_code == 0
    assert "recommendations" in result.output.lower()
```

#### Step 3.4: Write Tests for AI Integration (1 hour)
**Test scenarios** (with mocks):
- [ ] AI service called correctly
- [ ] AI response processed
- [ ] AI errors handled

#### Step 3.5: Measure and Iterate (30-60 min)
```bash
pytest tests/unit/test_cmd_ai.py \
  --cov=claude_ctx_py/cmd_ai.py \
  --cov-report=term-missing

# Iterate until ≥40%
```

### Output Deliverables
- ✅ File: `tests/unit/test_cmd_ai.py`
- ✅ Coverage: cmd_ai.py ≥40% (was 0%)
- ✅ All tests passing

### Verification
```bash
pytest tests/unit/test_cmd_ai.py --cov=claude_ctx_py/cmd_ai.py -v

# Success: ≥40% coverage, all tests pass
```

### Expected Impact
- Coverage: ~32% → ~34%

---

## Task 4: Write Testing Conventions Guide

**Priority**: 🟡 MEDIUM
**Time Estimate**: 2-3 hours
**Purpose**: Complete documentation referenced in CONTRIBUTING.md

### Input Requirements
- ✅ CONTRIBUTING.md exists (references this doc)
- ✅ Multiple test files created (patterns established)

### Execution Steps

#### Step 4.1: Review Existing Tests (30 min)
```bash
# Analyze patterns in existing tests
ls -la tests/unit/
cat tests/unit/test_intelligence_comprehensive.py | head -50
cat tests/unit/test_metrics.py | head -50
```

**Extract patterns**:
- Test structure
- Naming conventions
- Mock usage
- Fixtures

#### Step 4.2: Create Documentation File (2 hours)
```bash
cat > docs/guides/testing-conventions.md << 'EOF'
# Testing Conventions

## Overview
This guide documents testing patterns and conventions for claude-ctx-plugin.

## Test Organization
[Structure and file organization]

## Naming Conventions
[How to name tests, files, fixtures]

## Test Markers
[When to use each marker]

## Mocking Patterns
[Common mock patterns with examples]

## Coverage Expectations
[Requirements by module type]

## Examples
[Real examples from the codebase]
EOF
```

**Sections to include**:
1. Test Organization (unit vs integration)
2. Naming Conventions (files, classes, methods)
3. Test Markers (when to use each)
4. Fixture Patterns (common fixtures)
5. Mocking Strategies (filesystem, network, etc.)
6. Coverage Expectations (80% core, 70% TUI)
7. Examples (from actual tests)
8. Common Pitfalls (what to avoid)
9. TUI Testing (Textual-specific patterns)
10. CI Integration (how tests run in CI)

#### Step 4.3: Add Examples (30 min)
Copy relevant examples from actual test files

#### Step 4.4: Review and Refine (30 min)
- Check for clarity
- Verify accuracy
- Add cross-references

### Output Deliverables
- ✅ File: `docs/guides/testing-conventions.md`
- ✅ Linked from CONTRIBUTING.md
- ✅ Contains practical examples

### Verification
```bash
# 1. File exists
ls -la docs/guides/testing-conventions.md

# 2. Contains all sections
grep "^##" docs/guides/testing-conventions.md

# 3. Referenced in CONTRIBUTING.md
grep "testing-conventions" CONTRIBUTING.md

# Success: All checks pass
```

---

## Task 5: Update Week 1 Status Tracking

**Priority**: 🟢 LOW
**Time Estimate**: 30-60 min
**Purpose**: Maintain visibility and progress tracking

### Execution Steps

#### Step 5.1: Update Coverage Metrics (10 min)
```bash
# Run full coverage
pytest --cov=claude_ctx_py --cov-report=term > /tmp/coverage.txt

# Extract key metrics
grep "TOTAL" /tmp/coverage.txt
```

#### Step 5.2: Update Status Document (20 min)
```bash
# Update docs/workstreams/ws1-testing/status.md
```

**Update sections**:
- Current coverage %
- Modules tested today
- Tests added
- Issues encountered
- Next actions

#### Step 5.3: Update Day Tracker (10 min)
Create/update `docs/WEEK1_PROGRESS.md` with:
- Day-by-day metrics
- Modules completed
- Coverage trajectory
- On-track assessment

### Output Deliverables
- ✅ File: `docs/workstreams/ws1-testing/status.md` (updated)
- ✅ File: `docs/WEEK1_PROGRESS.md` (created/updated)

### Verification
```bash
# Files updated
ls -la docs/workstreams/ws1-testing/status.md
ls -la docs/WEEK1_PROGRESS.md

# Contains current date
grep "2025-11-" docs/WEEK1_PROGRESS.md
```

---

## End of Week 1 Checkpoint

**Target State**:
- Coverage: ≥30% (currently 21.85%)
- Core modules: intelligence ≥90%, agents ≥80%, base ≥50%
- Warnings: 0 (maintained)
- Tests: 500+
- Documentation: CONTRIBUTING.md + testing-conventions.md complete

**Verification**:
```bash
# Run full test suite
pytest --cov=claude_ctx_py --cov-report=term-missing

# Check metrics
# - Overall coverage ≥30%
# - All tests passing
# - Zero warnings

# Generate report
pytest --cov=claude_ctx_py --cov-report=html
open htmlcov/index.html
```

**If targets not met**:
- Identify coverage gaps
- Add targeted tests
- Iterate until goals achieved

---

# Week 2: Integration Tests & TUI Setup

**Goal**: 30% → 40% coverage
**Focus**: Integration testing + TUI framework

---

## Task 6: Create Integration Test Framework

**Priority**: 🔴 HIGH
**Time Estimate**: 3-4 hours

### Execution Steps

#### Step 6.1: Design Integration Test Strategy (1 hour)
**Identify key integration points**:
- CLI → Core → File system
- TUI → Core → File system
- AI → Context detection → Recommendations

**Define test scenarios**:
- End-to-end user workflows
- Cross-module interactions
- External dependency integration

#### Step 6.2: Create Test Infrastructure (1 hour)
```bash
# Create integration test structure
mkdir -p tests/integration/{cli,tui,ai}

# Create shared fixtures
cat > tests/integration/conftest.py << 'EOF'
"""Shared fixtures for integration tests."""
import pytest
from pathlib import Path
import tempfile
import shutil

@pytest.fixture
def test_project(tmp_path):
    """Create a test project with .claude directory."""
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()

    claude_dir = project_dir / ".claude"
    claude_dir.mkdir()

    # Create structure
    (claude_dir / "agents").mkdir()
    (claude_dir / "modes").mkdir()
    (claude_dir / "CLAUDE.md").touch()

    return project_dir

@pytest.fixture
def sample_agents(test_project):
    """Create sample agent files."""
    agents_dir = test_project / ".claude" / "agents"

    (agents_dir / "test-agent-1.md").write_text("""---
name: Test Agent 1
active: true
---
# Test Agent 1
Test content
""")

    (agents_dir / "test-agent-2.md").write_text("""---
name: Test Agent 2
active: false
---
# Test Agent 2
Test content
""")

    return test_project
EOF
```

#### Step 6.3: Write First Integration Test (1 hour)
```bash
cat > tests/integration/cli/test_agent_workflow.py << 'EOF'
"""Integration test for agent management workflow."""
import pytest
from click.testing import CliRunner

from claude_ctx_py.cli import main

@pytest.mark.integration
@pytest.mark.slow
def test_agent_list_activate_deactivate_workflow(test_project, sample_agents):
    """Test complete agent management workflow."""
    runner = CliRunner()

    # Change to test project directory
    with runner.isolated_filesystem(temp_dir=test_project):
        # List agents
        result = runner.invoke(main, ['agent', 'list'])
        assert result.exit_code == 0
        assert 'Test Agent 1' in result.output
        assert 'Test Agent 2' in result.output

        # Activate agent
        result = runner.invoke(main, ['agent', 'activate', 'test-agent-2'])
        assert result.exit_code == 0

        # Verify activation
        result = runner.invoke(main, ['agent', 'list', '--active'])
        assert result.exit_code == 0
        assert 'Test Agent 2' in result.output

        # Deactivate agent
        result = runner.invoke(main, ['agent', 'deactivate', 'test-agent-2'])
        assert result.exit_code == 0
EOF
```

#### Step 6.4: Verify Integration Tests Run (15 min)
```bash
# Run integration tests
pytest tests/integration/ -v -m integration

# Verify they pass
```

### Output Deliverables
- ✅ Directory: `tests/integration/` structure
- ✅ File: `tests/integration/conftest.py` (shared fixtures)
- ✅ File: `tests/integration/cli/test_agent_workflow.py`
- ✅ Integration tests passing

### Verification
```bash
pytest tests/integration/ -v -m integration

# Success: Tests pass, infrastructure works
```

---

## Task 7: Write 3 More Integration Tests

**Priority**: 🟡 MEDIUM
**Time Estimate**: 3-4 hours (1-1.5h each)

### Test Scenarios

#### Integration Test 2: AI Recommendation Flow
**File**: `tests/integration/ai/test_recommendation_flow.py`
**Scenario**: Context detection → Pattern learning → Recommendations

#### Integration Test 3: TUI Navigation Flow
**File**: `tests/integration/tui/test_navigation_flow.py`
**Scenario**: Launch TUI → Navigate views → Edit agent → Save

#### Integration Test 4: File Sync Flow
**File**: `tests/integration/cli/test_file_sync.py`
**Scenario**: Create agent → Sync to CLAUDE.md → Verify content

### Execution Steps (per test)

1. **Design test scenario** (15 min)
2. **Write test code** (45 min)
3. **Debug and fix** (15-30 min)
4. **Verify passing** (5 min)

### Output Deliverables
- ✅ 3 new integration test files
- ✅ All tests passing
- ✅ Integration coverage ≥60%

---

## Task 8: Set Up TUI Testing Framework

**Priority**: 🔴 HIGH
**Time Estimate**: 4-6 hours

### Execution Steps

#### Step 8.1: Research Textual Testing (1 hour)
```bash
# Read Textual docs on testing
# https://textual.textualize.io/guide/testing/

# Study examples from Textual repo
# Look for headless testing patterns
```

#### Step 8.2: Create TUI Test Infrastructure (1 hour)
```bash
mkdir -p tests/unit/tui

cat > tests/unit/tui/conftest.py << 'EOF'
"""Fixtures for TUI testing."""
import pytest
from textual.pilot import Pilot

@pytest.fixture
async def app_pilot():
    """Create a Pilot for testing TUI app."""
    from claude_ctx_py.tui.app import ClaudeCtxApp

    app = ClaudeCtxApp()
    async with app.run_test() as pilot:
        yield pilot
EOF
```

#### Step 8.3: Write First TUI Test (1 hour)
```bash
cat > tests/unit/tui/test_app_basic.py << 'EOF'
"""Basic TUI application tests."""
import pytest
from textual.pilot import Pilot

from claude_ctx_py.tui.app import ClaudeCtxApp

@pytest.mark.asyncio
@pytest.mark.tui
async def test_app_launches():
    """Test TUI app launches successfully."""
    app = ClaudeCtxApp()
    async with app.run_test() as pilot:
        assert app.is_running
        assert pilot.app.screen is not None

@pytest.mark.asyncio
@pytest.mark.tui
async def test_app_navigation():
    """Test basic navigation in TUI."""
    app = ClaudeCtxApp()
    async with app.run_test() as pilot:
        # Test navigation between views
        await pilot.press("tab")  # Navigate
        # Add assertions based on app structure
EOF
```

#### Step 8.4: Write Widget Tests (1-2 hours)
Create tests for key widgets:
- Agent browser widget
- Editor widget
- Status bar
- Command palette

#### Step 8.5: Document TUI Testing Patterns (30 min)
Add section to `docs/guides/testing-conventions.md`:
```markdown
## TUI Testing with Textual

### Running Headless Tests
[How to use run_test()]

### Testing User Interactions
[How to test keypresses, mouse events]

### Testing Rendering
[How to verify UI state]

### Common Patterns
[Examples from test files]
```

### Output Deliverables
- ✅ TUI test infrastructure in `tests/unit/tui/`
- ✅ First TUI tests passing
- ✅ TUI testing documented

### Verification
```bash
pytest tests/unit/tui/ -v -m tui

# Success: Tests pass, framework works
```

---

## End of Week 2 Checkpoint

**Target State**:
- Coverage: ≥40% (was 30%)
- Integration tests: 4+ flows tested
- TUI testing: Framework operational
- Documentation: Integration + TUI testing guides

**Verification**:
```bash
pytest --cov=claude_ctx_py --cov-report=term-missing

# Check:
# - Overall ≥40%
# - Integration tests passing
# - TUI tests passing
```

---

# Week 3-4: TUI Testing & More Core Coverage

**Goal**: 40% → 55% coverage
**Focus**: Complete TUI component testing, finish remaining core modules

---

## Task 9: Test Remaining Core Modules

**Priority**: 🔴 HIGH
**Time Estimate**: 12-16 hours (distributed)

### Modules to Complete

| Module | Current | Target | Priority | Effort |
|--------|---------|--------|----------|--------|
| **base.py** | 50% | 80% | HIGH | 4-5h |
| **skills.py** | 5.36% | 60% | HIGH | 5-6h |
| **profiles.py** | 7.67% | 50% | MED | 4-5h |
| **workflows.py** | 15.27% | 60% | MED | 3-4h |

### Execution (Per Module)

Follow same pattern as Task 1 (agents.py):
1. Analyze module structure
2. Create comprehensive test file
3. Write tests (CRUD, business logic, errors)
4. Measure coverage, iterate until target met
5. Verify all tests passing

### Output Deliverables
- ✅ 4 comprehensive test files
- ✅ All modules at target coverage
- ✅ All tests passing

---

## Task 10: Complete TUI Component Testing

**Priority**: 🔴 HIGH
**Time Estimate**: 16-20 hours

### Components to Test

1. **Main App** (`tui/main.py`)
   - App lifecycle
   - View management
   - State management
   - Target: 40% (partial, due to size)

2. **Agent Browser** (within main.py)
   - Agent listing
   - Filtering
   - Selection
   - Target: 70%

3. **Editor View** (within main.py)
   - File editing
   - Saving
   - Validation
   - Target: 70%

4. **Other Widgets**
   - Command palette
   - Status bar
   - Dialogs
   - Target: 60%

### Execution Steps (Per Component)

#### Step 10.1: Identify Component Boundaries (30 min)
- Read tui/main.py
- Identify discrete components
- Plan test strategy

#### Step 10.2: Write Component Tests (3-4 hours per component)
- Test rendering
- Test user interactions (keyboard, mouse)
- Test state changes
- Test error handling

#### Step 10.3: Measure and Iterate (30-60 min per component)
```bash
pytest tests/unit/tui/test_<component>.py \
  --cov=claude_ctx_py/tui/main.py \
  --cov-report=term-missing
```

### Output Deliverables
- ✅ TUI component tests for 5+ components
- ✅ TUI coverage ≥40% (was 0%)
- ✅ All tests passing

---

## End of Week 4 Checkpoint

**Target State**:
- Coverage: ≥55% (was 40%)
- Core modules: All critical modules ≥60%
- TUI coverage: ≥40%
- Integration tests: 5+ flows

**Verification**:
```bash
pytest --cov=claude_ctx_py --cov-report=html
open htmlcov/index.html

# Check all modules meet targets
```

---

# Week 5-7: Refactoring & Advanced Features

**Goal**: 55% → 70% coverage
**Focus**: TUI refactoring, Intelligence refactoring, Feature development

---

## Task 11: Refactor TUI into Modular Components

**Priority**: 🔴 CRITICAL
**Time Estimate**: 20-24 hours
**Purpose**: Break down tui/main.py (2,914 lines) into manageable modules

### Execution Steps

#### Step 11.1: Plan Component Extraction (2 hours)
**Analyze**: Read tui/main.py, identify natural boundaries
**Plan**: Design new module structure
**Document**: Create refactoring plan document

#### Step 11.2: Create New Module Structure (1 hour)
```bash
mkdir -p claude_ctx_py/tui/{views,widgets,controllers}

# Create module files
touch claude_ctx_py/tui/views/__init__.py
touch claude_ctx_py/tui/widgets/__init__.py
touch claude_ctx_py/tui/controllers/__init__.py
```

#### Step 11.3: Extract Components (15-18 hours)
**Strategy**: Extract one component at a time, test after each

**Component extraction order**:
1. Agent Browser View (4-5 hours)
2. Editor View (4-5 hours)
3. Navigation Controller (2-3 hours)
4. Data Manager (3-4 hours)
5. Remaining widgets (2-3 hours)

**Per component**:
1. Create new file
2. Move code from main.py
3. Update imports
4. Run tests (should still pass)
5. Measure coverage (should maintain or improve)
6. Commit

#### Step 11.4: Update Tests (2 hours)
Update test imports to point to new modules

#### Step 11.5: Verify Refactoring (1 hour)
```bash
# All tests still pass
pytest

# Coverage maintained or improved
pytest --cov=claude_ctx_py/tui

# TUI still works
python -m claude_ctx_py.tui.app
```

### Output Deliverables
- ✅ Modular TUI structure (6+ modules, each <500 lines)
- ✅ All tests passing
- ✅ Coverage maintained or improved
- ✅ TUI functionality unchanged

### Verification
```bash
# Check file sizes
wc -l claude_ctx_py/tui/**/*.py

# All files <500 lines
# All tests pass
pytest -v

# TUI runs correctly
python -m claude_ctx_py.tui.app
```

---

## Task 12: Refactor Intelligence Module

**Priority**: 🔴 HIGH
**Time Estimate**: 12-16 hours
**Purpose**: Make learning strategies pluggable

### Execution Steps

#### Step 12.1: Design Architecture (2 hours)
**Create**: `docs/architecture/intelligence-refactoring.md`

**Design**:
- `ILearningStrategy` interface
- `PatternLearner` uses strategy
- Multiple strategy implementations

#### Step 12.2: Create Interfaces (2 hours)
```python
# claude_ctx_py/intelligence/interfaces.py
from abc import ABC, abstractmethod
from typing import List, Dict

class ILearningStrategy(ABC):
    """Interface for learning strategies."""

    @abstractmethod
    def learn_patterns(self, history: List[Dict]) -> Dict:
        """Learn patterns from history."""
        pass

    @abstractmethod
    def match_patterns(self, context: Dict) -> List[Dict]:
        """Match patterns against context."""
        pass
```

#### Step 12.3: Implement Strategies (4-6 hours)
1. **RulesBasedStrategy** (migrate current logic)
2. **SimpleStrategy** (basic pattern matching)
3. **StatisticalStrategy** (frequency-based)

#### Step 12.4: Refactor PatternLearner (2-3 hours)
Update to use strategy pattern

#### Step 12.5: Update Tests (2-3 hours)
Test each strategy independently

#### Step 12.6: Verify (1 hour)
```bash
pytest tests/unit/intelligence/
pytest tests/integration/ai/

# All tests pass
# Coverage maintained
```

### Output Deliverables
- ✅ Pluggable learning strategy architecture
- ✅ 3+ strategy implementations
- ✅ All tests passing
- ✅ Coverage ≥85% maintained

---

## Task 13: Implement Embedding-Based Recommender

**Priority**: 🟡 MEDIUM
**Time Estimate**: 16-20 hours
**Purpose**: Advanced AI feature using embeddings

### Execution Steps

#### Step 13.1: Design Feature (2 hours)
**Document**: Feature requirements and architecture
**Research**: Sentence transformers, embeddings

#### Step 13.2: Add Dependencies (30 min)
```bash
# Add to pyproject.toml
sentence-transformers = "^2.0.0"

# Install
pip install sentence-transformers
```

#### Step 13.3: Implement Embedding Strategy (6-8 hours)
```python
# claude_ctx_py/intelligence/strategies/embedding.py
from sentence_transformers import SentenceTransformer

class EmbeddingStrategy(ILearningStrategy):
    """Embedding-based learning strategy."""

    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.pattern_embeddings = {}

    def learn_patterns(self, history):
        # Create embeddings from history
        pass

    def match_patterns(self, context):
        # Use cosine similarity
        pass
```

#### Step 13.4: Add Feature Flag (1 hour)
```python
# Enable with flag
USE_EMBEDDINGS = os.getenv("CLAUDE_CTX_USE_EMBEDDINGS", "false").lower() == "true"
```

#### Step 13.5: Write Tests (4-6 hours)
Test embedding strategy in isolation

#### Step 13.6: Benchmark vs Rules-Based (2 hours)
Compare accuracy and performance

#### Step 13.7: Document (1 hour)
Add usage guide and configuration docs

### Output Deliverables
- ✅ Embedding-based recommender (behind feature flag)
- ✅ Tests with ≥80% coverage
- ✅ Benchmark comparison
- ✅ Documentation

---

## End of Week 7 Checkpoint

**Target State**:
- Coverage: ≥70% (was 55%)
- TUI: Modular architecture (<500 lines per file)
- Intelligence: Pluggable strategies
- Features: Embedding recommender operational

**Verification**:
```bash
pytest --cov=claude_ctx_py --cov-report=term-missing

# Overall ≥70%
# All refactored modules tested
# New features tested
```

---

# Week 8-10: Final Push to 75-80%

**Goal**: 70% → 75-80% coverage
**Focus**: Polish, edge cases, integration, documentation

---

## Task 14: Complete Remaining Coverage Gaps

**Priority**: 🔴 HIGH
**Time Estimate**: 12-16 hours

### Execution Steps

#### Step 14.1: Identify Gaps (1 hour)
```bash
# Generate HTML coverage report
pytest --cov=claude_ctx_py --cov-report=html
open htmlcov/index.html

# List modules <80%
# Prioritize by importance
```

#### Step 14.2: Target Low-Hanging Fruit (4-6 hours)
Focus on modules close to target:
- 70-79% → 80%+
- 60-69% → 75%+

#### Step 14.3: Add Edge Case Tests (4-6 hours)
Test scenarios often missed:
- Error handling paths
- Boundary conditions
- Unusual inputs
- Race conditions

#### Step 14.4: Add Integration Tests (3-4 hours)
Ensure component integration tested

### Output Deliverables
- ✅ All core modules ≥80%
- ✅ All TUI components ≥70%
- ✅ Overall ≥75%

---

## Task 15: Performance Testing & Optimization

**Priority**: 🟡 MEDIUM
**Time Estimate**: 8-10 hours

### Execution Steps

#### Step 15.1: Set Up Performance Benchmarks (2 hours)
```python
# tests/performance/test_benchmarks.py
import pytest

@pytest.mark.performance
def test_agent_listing_performance(benchmark):
    """Benchmark agent listing."""
    result = benchmark(list_agents, test_dir)
    assert result  # Performance regression check
```

#### Step 15.2: Profile Key Operations (2-3 hours)
```bash
# Profile critical paths
python -m cProfile -o profile.stats app.py
python -m pstats profile.stats

# Identify bottlenecks
```

#### Step 15.3: Optimize (3-4 hours)
Focus on:
- File I/O operations
- Pattern matching algorithms
- TUI rendering

#### Step 15.4: Add Performance Tests to CI (1 hour)
Ensure performance regressions caught

### Output Deliverables
- ✅ Performance benchmarks
- ✅ Optimization improvements
- ✅ CI performance tests

---

## Task 16: Complete Documentation

**Priority**: 🟡 MEDIUM
**Time Estimate**: 12-16 hours

### Documentation Checklist

#### API Documentation (4-6 hours)
- [ ] Generate API docs with Sphinx
- [ ] Document all public APIs
- [ ] Add usage examples

#### User Guides (4-6 hours)
- [ ] Getting started tutorial
- [ ] Common workflows
- [ ] Troubleshooting guide
- [ ] FAQ

#### Developer Guides (2-3 hours)
- [ ] Architecture deep dive
- [ ] Extending the system
- [ ] Plugin development

#### Examples (2-3 hours)
- [ ] Example agents
- [ ] Example workflows
- [ ] Integration examples

### Output Deliverables
- ✅ Complete API documentation
- ✅ User guides
- ✅ Developer guides
- ✅ Examples

---

## Task 17: Final Quality Pass

**Priority**: 🔴 CRITICAL
**Time Estimate**: 8-12 hours

### Execution Steps

#### Step 17.1: Run All Quality Checks (1 hour)
```bash
# Tests
pytest --cov=claude_ctx_py --cov-report=term-missing

# Formatting
make lint

# Type checking
make type-check

# Security scan
bandit -r claude_ctx_py/
```

#### Step 17.2: Fix Any Issues (4-6 hours)
Address:
- Test failures
- Type errors
- Security issues
- Code quality issues

#### Step 17.3: Update All Documentation (2-3 hours)
Ensure docs reflect final state

#### Step 17.4: Create Release Checklist (1 hour)
Document what was achieved

#### Step 17.5: Final Verification (1-2 hours)
```bash
# Full test suite
pytest -v

# Coverage check
pytest --cov=claude_ctx_py --cov-report=html

# Manual TUI testing
python -m claude_ctx_py.tui.app

# CLI testing
claude-ctx --help
claude-ctx agent list
```

### Output Deliverables
- ✅ All quality gates passing
- ✅ Coverage ≥75%
- ✅ Documentation complete
- ✅ Release ready

---

## End of Week 10 Checkpoint (FINAL)

**Target State**:
- Coverage: ≥75-80%
- All quality gates: Passing
- Documentation: Complete
- Features: Delivered and tested

**Final Verification**:
```bash
# 1. Run full test suite
pytest --cov=claude_ctx_py --cov-report=html -v

# 2. Check coverage
# Overall: ≥75%
# Core modules: ≥80%
# TUI components: ≥70%

# 3. Verify quality gates
make verify

# 4. Manual testing
python -m claude_ctx_py.tui.app
claude-ctx agent list

# 5. Generate final report
pytest --cov=claude_ctx_py --cov-report=html
open htmlcov/index.html
```

**Success Criteria**:
- [ ] Coverage ≥75%
- [ ] All tests passing (≥600 tests)
- [ ] Zero warnings
- [ ] All documentation complete
- [ ] TUI fully functional
- [ ] CLI fully functional
- [ ] Performance acceptable
- [ ] Security scan clean

---

# Quick Reference: Task Dependencies

```
Week 1:
  Task 1 (agents.py) → Task 2 (base.py) → Task 3 (cmd_ai.py)
  Task 4 (testing guide) - can run parallel
  Task 5 (status update) - run at end

Week 2:
  Task 6 (integration framework) → Task 7 (more integration tests)
  Task 8 (TUI framework) - can run parallel

Week 3-4:
  Task 9 (remaining core) - can parallelize by module
  Task 10 (TUI components) - depends on Task 8

Week 5-7:
  Task 11 (TUI refactor) → requires Task 10 complete
  Task 12 (intelligence refactor) - can run parallel with Task 11
  Task 13 (embeddings) → depends on Task 12

Week 8-10:
  Task 14 (coverage gaps) - all previous complete
  Task 15 (performance) - can run parallel
  Task 16 (documentation) - can run parallel
  Task 17 (final quality) → all previous complete
```

---

# Execution Tips

## For Humans

1. **Follow tasks sequentially** - Each builds on previous
2. **Verify after each task** - Don't skip verification steps
3. **Update tracking frequently** - Maintain visibility
4. **Ask for help when stuck** - Reference docs and examples
5. **Take breaks** - This is a marathon, not a sprint

## For AI Agents (like Codex)

1. **Execute one task at a time** - Complete fully before moving to next
2. **Run verification steps** - Don't assume success
3. **Update status docs** - Keep humans informed
4. **Ask for clarification** - If inputs unclear
5. **Report issues immediately** - Don't continue if blocked

## Success Patterns

**DO**:
- ✅ Follow the sequence
- ✅ Complete verification steps
- ✅ Update documentation
- ✅ Ask questions early
- ✅ Measure coverage after each task

**DON'T**:
- ❌ Skip verification
- ❌ Jump ahead in sequence
- ❌ Assume tests pass
- ❌ Leave documentation outdated
- ❌ Continue when blocked

---

# Tracking Progress

## Daily Updates

Create `docs/DAILY_LOG.md`:
```markdown
# Daily Progress Log

## 2025-11-28
- Task completed: Task 1 (agents.py)
- Coverage: 21.85% → 28%
- Tests added: 45
- Issues: None
- Next: Task 2 (base.py)

## 2025-11-29
- Task completed: Task 2 (base.py)
- Coverage: 28% → 32%
- Tests added: 38
- Issues: Found edge case in base class
- Next: Task 3 (cmd_ai.py)
```

## Weekly Reviews

Every Friday, create:
- Coverage progress chart
- Modules completed
- Blockers encountered
- Next week plan

---

# Completion Criteria

**The plan is COMPLETE when**:
- [ ] All 17 tasks completed
- [ ] Coverage ≥75%
- [ ] All quality gates passing
- [ ] Documentation complete
- [ ] Final verification passed

**At that point**:
1. Generate final report
2. Create summary document
3. Celebrate! 🎉

---

**Prepared for**: Sequential execution by any developer or AI agent
**Total estimated time**: 9 weeks (160-200 hours)
**Expected outcome**: Professional-grade tested codebase with 75-80% coverage

**Ready to execute!** Start with Task 1 when ready. 🚀
