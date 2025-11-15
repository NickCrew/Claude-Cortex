# GitHub Issues to Create for Test Coverage

Copy and paste these into GitHub Issues to reach 80% test coverage.

---

## Issue #1: Test Coverage for core/base.py

**Title:**
```
Test Coverage: core/base.py
```

**Labels:**
```
testing, test-coverage, priority-high, core-module, good-first-issue
```

**Body:**
```markdown
## Module Information
- **File:** `claude_ctx_py/core/base.py`
- **Current Coverage:** 0% (no tests)
- **Target Coverage:** 80%+
- **Priority:** 🔴 High (core functionality)

## Functions Needing Tests
- [ ] `_resolve_claude_dir()` - Claude directory resolution
- [ ] `_iter_all_files()` - File iteration logic
- [ ] `_agent_basename()` - Agent name extraction
- [ ] `_is_disabled()` - Disabled agent detection
- [ ] `_extract_agent_name()` - Name extraction from content
- [ ] `_read_agent_front_matter_lines()` - YAML front matter parsing
- [ ] `_parse_dependencies_from_front()` - Dependency extraction
- [ ] `_tokenize_front_matter()` - Front matter tokenization
- [ ] `_extract_scalar_from_paths()` - Scalar value extraction

## Test Areas
- ✅ Path resolution (macOS, Linux, Windows)
- ✅ File iteration with filters
- ✅ Agent naming conventions
- ✅ Front matter parsing (valid, invalid, edge cases)
- ✅ Dependency resolution
- ✅ Error handling

## Example Test
```python
def test_resolve_claude_dir():
    """Test Claude directory resolution"""
    from claude_ctx_py.core.base import _resolve_claude_dir

    # Test with default
    result = _resolve_claude_dir()
    assert result.exists()
    assert result.name == '.claude'

    # Test with custom path
    result = _resolve_claude_dir(Path('/custom/path'))
    assert result == Path('/custom/path')
```

## Acceptance Criteria
- [ ] `tests/unit/test_core_base.py` created
- [ ] 80%+ coverage achieved
- [ ] All edge cases tested
- [ ] Tests pass in CI/CD

## Resources
- Reference: `tests/unit/test_mcp.py` for testing patterns
- [pytest documentation](https://docs.pytest.org/)
```

---

## Issue #2: Test Coverage for core/agents.py

**Title:**
```
Test Coverage: core/agents.py
```

**Labels:**
```
testing, test-coverage, priority-high, core-module
```

**Body:**
```markdown
## Module Information
- **File:** `claude_ctx_py/core/agents.py`
- **Current Coverage:** 0% (no tests)
- **Target Coverage:** 80%+
- **Priority:** 🔴 High (core functionality)

## Functions Needing Tests
- [ ] `list_agents()` - List all available agents
- [ ] `agent_status()` - Show agent activation status
- [ ] `agent_activate()` - Activate agents with dependency checking
- [ ] `agent_deactivate()` - Deactivate agents
- [ ] `build_agent_graph()` - Build dependency graph
- [ ] `agent_deps()` - Show agent dependencies
- [ ] `agent_graph()` - Generate dependency visualization
- [ ] `validate_agent()` - Validate agent metadata against schema

## Test Areas
- ✅ Agent listing (active, disabled, all)
- ✅ Activation/deactivation logic
- ✅ Dependency graph construction
- ✅ Circular dependency detection
- ✅ Validation against schema
- ✅ Error handling (missing files, invalid YAML)

## Example Test
```python
def test_build_agent_graph():
    """Test dependency graph construction"""
    from claude_ctx_py.core.agents import build_agent_graph

    graph = build_agent_graph()
    assert isinstance(graph, dict)
    assert len(graph) > 0

    # Check for valid structure
    for name, node in graph.items():
        assert hasattr(node, 'name')
        assert hasattr(node, 'dependencies')
```

## Acceptance Criteria
- [ ] `tests/unit/test_core_agents.py` created
- [ ] 80%+ coverage achieved
- [ ] Dependency graph tests comprehensive
- [ ] Circular dependency detection tested
- [ ] Tests pass in CI/CD
```

---

## Issue #3: Test Coverage for core/modes.py

**Title:**
```
Test Coverage: core/modes.py
```

**Labels:**
```
testing, test-coverage, priority-high, core-module
```

**Body:**
```markdown
## Module Information
- **File:** `claude_ctx_py/core/modes.py`
- **Current Coverage:** 0% (no tests)
- **Target Coverage:** 80%+
- **Priority:** 🔴 High (core functionality)

## Functions Needing Tests
- [ ] `list_modes()` - List available modes
- [ ] `mode_status()` - Show active modes
- [ ] `mode_activate()` - Activate modes
- [ ] `mode_deactivate()` - Deactivate modes

## Test Areas
- ✅ Mode listing (active vs inactive)
- ✅ Activation/deactivation (file moves)
- ✅ Error handling (invalid modes, missing files)
- ✅ Return value verification

## Acceptance Criteria
- [ ] `tests/unit/test_core_modes.py` created
- [ ] 80%+ coverage achieved
- [ ] Tests pass in CI/CD
```

---

## Issue #4: Test Coverage for core/rules.py

**Title:**
```
Test Coverage: core/rules.py
```

**Labels:**
```
testing, test-coverage, priority-high, core-module
```

**Body:**
```markdown
## Module Information
- **File:** `claude_ctx_py/core/rules.py`
- **Current Coverage:** 0% (no tests)
- **Target Coverage:** 80%+
- **Priority:** 🔴 High (core functionality)

## Functions Needing Tests
- [ ] `list_rules()` - List available rules
- [ ] `rules_status()` - Show active rules
- [ ] `rules_activate()` - Activate rules
- [ ] `rules_deactivate()` - Deactivate rules

## Test Areas
- ✅ Rule listing
- ✅ Activation/deactivation
- ✅ File operations
- ✅ Error handling

## Acceptance Criteria
- [ ] `tests/unit/test_core_rules.py` created
- [ ] 80%+ coverage achieved
- [ ] Tests pass in CI/CD
```

---

## Issue #5: Test Coverage for cli.py

**Title:**
```
Test Coverage: cli.py (argument parsing & command routing)
```

**Labels:**
```
testing, test-coverage, priority-high, cli
```

**Body:**
```markdown
## Module Information
- **File:** `claude_ctx_py/cli.py`
- **Current Coverage:** Minimal (only basic tests exist)
- **Target Coverage:** 80%+
- **Priority:** 🔴 High (main entry point)

## Functions Needing Tests
- [ ] `build_parser()` - Argument parser construction for all subcommands
- [ ] `main()` - Main entry point with command routing
- [ ] All subcommand handlers (mode, agent, rules, skills, mcp, etc.)
- [ ] Error handling and exit codes

## Test Areas
- ✅ Parser construction (all subcommands: mode, agent, rules, skills, workflows, mcp, export, ai)
- ✅ Argument validation
- ✅ Command routing
- ✅ Exit codes (0 for success, non-zero for errors)
- ✅ Error messages
- ✅ Help text generation

## Example Test
```python
def test_build_parser_mcp_commands():
    """Test MCP subcommand parsing"""
    from claude_ctx_py.cli import build_parser

    parser = build_parser()

    # Test mcp list
    args = parser.parse_args(['mcp', 'list'])
    assert args.command == 'mcp'
    assert args.mcp_command == 'list'

    # Test mcp show with server name
    args = parser.parse_args(['mcp', 'show', 'context7'])
    assert args.command == 'mcp'
    assert args.mcp_command == 'show'
    assert args.server == 'context7'
```

## Acceptance Criteria
- [ ] `tests/integration/test_cli.py` expanded with comprehensive tests
- [ ] All subcommands tested
- [ ] Argument validation tested
- [ ] 80%+ coverage achieved
- [ ] Tests pass in CI/CD
```

---

## Issue #6: Test Coverage for core/skills.py

**Title:**
```
Test Coverage: core/skills.py
```

**Labels:**
```
testing, test-coverage, priority-medium, core-module
```

**Body:**
```markdown
## Module Information
- **File:** `claude_ctx_py/core/skills.py`
- **Current Coverage:** 0% (no tests)
- **Target Coverage:** 80%+
- **Priority:** 🟡 Medium

## Functions Needing Tests
- [ ] `list_skills()` - List available skills
- [ ] `skill_validate()` - Validate skill structure
- [ ] `skill_metrics()` - Get skill metrics
- [ ] `skill_community()` - Community skill operations

## Acceptance Criteria
- [ ] `tests/unit/test_core_skills.py` created
- [ ] 80%+ coverage achieved
- [ ] Tests pass in CI/CD
```

---

## Issue #7: Test Coverage for core/workflows.py

**Title:**
```
Test Coverage: core/workflows.py
```

**Labels:**
```
testing, test-coverage, priority-medium, core-module
```

**Body:**
```markdown
## Module Information
- **File:** `claude_ctx_py/core/workflows.py`
- **Current Coverage:** 0% (no tests)
- **Target Coverage:** 80%+
- **Priority:** 🟡 Medium

## Functions Needing Tests
- [ ] `workflow_list()` - List workflows
- [ ] `workflow_status()` - Show workflow status
- [ ] `workflow_run()` - Execute workflow
- [ ] `workflow_resume()` - Resume workflow

## Acceptance Criteria
- [ ] `tests/unit/test_core_workflows.py` created
- [ ] 80%+ coverage achieved
- [ ] Tests pass in CI/CD
```

---

## Issue #8: Test Coverage for core/context_export.py

**Title:**
```
Test Coverage: core/context_export.py
```

**Labels:**
```
testing, test-coverage, priority-medium, core-module
```

**Body:**
```markdown
## Module Information
- **File:** `claude_ctx_py/core/context_export.py`
- **Current Coverage:** 0% (no tests)
- **Target Coverage:** 80%+
- **Priority:** 🟡 Medium

## Functions Needing Tests
- [ ] `export_context()` - Export context to file
- [ ] Category filtering logic
- [ ] File exclusion logic
- [ ] Format generation (Claude-specific, agent-generic)

## Test Areas
- ✅ Export with various filters
- ✅ Format generation
- ✅ File writing
- ✅ Error handling

## Acceptance Criteria
- [ ] `tests/unit/test_core_context_export.py` created
- [ ] 80%+ coverage achieved
- [ ] Tests pass in CI/CD
```

---

## Issue #9: Test Coverage for suggester.py

**Title:**
```
Test Coverage: suggester.py
```

**Labels:**
```
testing, test-coverage, priority-medium
```

**Body:**
```markdown
## Module Information
- **File:** `claude_ctx_py/suggester.py`
- **Current Coverage:** 0% (no tests)
- **Target Coverage:** 80%+
- **Priority:** 🟡 Medium

## Functions Needing Tests
All suggestion logic and recommendation algorithms

## Test Areas
- ✅ Suggestion generation
- ✅ Recommendation scoring
- ✅ Context analysis
- ✅ Error handling

## Acceptance Criteria
- [ ] `tests/unit/test_suggester.py` created
- [ ] 80%+ coverage achieved
- [ ] Tests pass in CI/CD
```

---

## Issue #10: Test Coverage for cmd_ai.py

**Title:**
```
Test Coverage: cmd_ai.py
```

**Labels:**
```
testing, test-coverage, priority-medium, ai
```

**Body:**
```markdown
## Module Information
- **File:** `claude_ctx_py/cmd_ai.py`
- **Current Coverage:** 0% (no tests)
- **Target Coverage:** 80%+
- **Priority:** 🟡 Medium

## Functions Needing Tests
All AI command functionality

## Test Areas
- ✅ AI recommendations
- ✅ Context analysis
- ✅ Prediction logic
- ✅ Error handling

## Acceptance Criteria
- [ ] `tests/unit/test_cmd_ai.py` created
- [ ] 80%+ coverage achieved
- [ ] Tests pass in CI/CD
```

---

## Issue #11: [META] Test Coverage Tracker - 80% Target

**Title:**
```
[META] Test Coverage Tracker - 80% Target
```

**Labels:**
```
testing, test-coverage, meta, tracking
```

**Body:**
```markdown
## Overall Progress

**Current Coverage:** TBD (need baseline measurement)
**Target Coverage:** 80%
**Modules Tested:** 3/32 (mcp, analytics, composer have tests)

## 🔴 Priority High (Week 1-2)

Core modules and entry points:
- [ ] #1 core/base.py
- [ ] #2 core/agents.py
- [ ] #3 core/modes.py
- [ ] #4 core/rules.py
- [ ] #5 cli.py

## 🟡 Priority Medium (Week 3-4)

Extended core functionality:
- [ ] #6 core/skills.py
- [ ] #7 core/workflows.py
- [ ] #8 core/context_export.py
- [ ] #9 suggester.py
- [ ] #10 cmd_ai.py

## 🟢 Priority Low (Week 5+)

Utilities and TUI components:
- [ ] error_utils.py
- [ ] TUI modules (select high-value components)

## Coverage Reports

Update weekly with CI coverage reports:
- Week 1: TBD
- Week 2: TBD
- Week 3: TBD
- Week 4: TBD

## Resources
- CI Integration: GitHub Actions with pytest-cov
- Coverage Badge: Add to README once 80% reached
- Testing Guide: See CONTRIBUTING.md (to be created)
```

---

## Quick Start: Creating Issues

1. Go to: https://github.com/yourusername/claude-ctx-plugin/issues/new
2. Copy the Title, Labels, and Body from each issue above
3. Create the issues in priority order (#1-#5 first)
4. Create the META tracking issue (#11) last
5. Link all test issues to the META tracking issue

## Automation Option

Use GitHub CLI to create all issues at once:

```bash
# Install GitHub CLI if not already installed
brew install gh

# Create issues programmatically (coming soon)
# Script to automate issue creation from this file
```
