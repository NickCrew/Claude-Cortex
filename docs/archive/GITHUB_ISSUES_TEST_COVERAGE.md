# GitHub Issues for Test Coverage (80% Target)

Issues to create for reaching 80% test coverage across claude-ctx-plugin.

## Priority 1: Core Modules (No Tests)

### Issue 1: Test Coverage for core/base.py
```markdown
**Title:** Test Coverage: core/base.py

**Labels:** testing, test-coverage, priority-high, core-module

**Body:**
## Module Information
- **File:** `claude_ctx_py/core/base.py`
- **Current Coverage:** 0% (no tests)
- **Target Coverage:** 80%+
- **Priority:** High (core functionality)

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

## Acceptance Criteria
- [ ] `tests/unit/test_core_base.py` created
- [ ] 80%+ coverage achieved
- [ ] All edge cases tested
- [ ] Tests pass in CI/CD
```

---

### Issue 2: Test Coverage for core/agents.py
```markdown
**Title:** Test Coverage: core/agents.py

**Labels:** testing, test-coverage, priority-high, core-module

**Body:**
## Module Information
- **File:** `claude_ctx_py/core/agents.py`
- **Current Coverage:** 0% (no tests)
- **Target Coverage:** 80%+
- **Priority:** High (core functionality)

## Functions Needing Tests
- [ ] `list_agents()` - List all available agents
- [ ] `agent_status()` - Show agent activation status
- [ ] `agent_activate()` - Activate agents
- [ ] `agent_deactivate()` - Deactivate agents
- [ ] `build_agent_graph()` - Build dependency graph
- [ ] `agent_deps()` - Show agent dependencies
- [ ] `agent_graph()` - Generate dependency visualization
- [ ] `validate_agent()` - Validate agent metadata

## Test Areas
- ✅ Agent listing (active, disabled, all)
- ✅ Activation/deactivation logic
- ✅ Dependency graph construction
- ✅ Circular dependency detection
- ✅ Validation against schema
- ✅ Error handling (missing files, invalid YAML)

## Acceptance Criteria
- [ ] `tests/unit/test_core_agents.py` created
- [ ] 80%+ coverage achieved
- [ ] Dependency graph tests comprehensive
- [ ] Tests pass in CI/CD
```

---

### Issue 3: Test Coverage for core/modes.py
```markdown
**Title:** Test Coverage: core/modes.py

**Labels:** testing, test-coverage, priority-high, core-module

**Body:**
## Module Information
- **File:** `claude_ctx_py/core/modes.py`
- **Current Coverage:** 0% (no tests)
- **Target Coverage:** 80%+
- **Priority:** High (core functionality)

## Functions Needing Tests
- [ ] `list_modes()` - List available modes
- [ ] `mode_status()` - Show active modes
- [ ] `mode_activate()` - Activate modes
- [ ] `mode_deactivate()` - Deactivate modes

## Test Areas
- ✅ Mode listing (active vs inactive)
- ✅ Activation/deactivation
- ✅ File operations (move between directories)
- ✅ Error handling (invalid modes, missing files)

## Acceptance Criteria
- [ ] `tests/unit/test_core_modes.py` created
- [ ] 80%+ coverage achieved
- [ ] Tests pass in CI/CD
```

---

### Issue 4: Test Coverage for core/rules.py
```markdown
**Title:** Test Coverage: core/rules.py

**Labels:** testing, test-coverage, priority-high, core-module

**Body:**
## Module Information
- **File:** `claude_ctx_py/core/rules.py`
- **Current Coverage:** 0% (no tests)
- **Target Coverage:** 80%+
- **Priority:** High (core functionality)

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

### Issue 5: Test Coverage for core/skills.py
```markdown
**Title:** Test Coverage: core/skills.py

**Labels:** testing, test-coverage, priority-medium, core-module

**Body:**
## Module Information
- **File:** `claude_ctx_py/core/skills.py`
- **Current Coverage:** 0% (no tests)
- **Target Coverage:** 80%+
- **Priority:** Medium

## Functions Needing Tests
- [ ] `list_skills()` - List available skills
- [ ] `skill_validate()` - Validate skill structure
- [ ] `skill_metrics()` - Get skill metrics
- [ ] `skill_community()` - Community skill operations

## Test Areas
- ✅ Skill discovery
- ✅ Validation logic
- ✅ Metrics calculation
- ✅ Error handling

## Acceptance Criteria
- [ ] `tests/unit/test_core_skills.py` created
- [ ] 80%+ coverage achieved
- [ ] Tests pass in CI/CD
```

---

### Issue 6: Test Coverage for core/workflows.py
```markdown
**Title:** Test Coverage: core/workflows.py

**Labels:** testing, test-coverage, priority-medium, core-module

**Body:**
## Module Information
- **File:** `claude_ctx_py/core/workflows.py`
- **Current Coverage:** 0% (no tests)
- **Target Coverage:** 80%+
- **Priority:** Medium

## Functions Needing Tests
- [ ] `workflow_list()` - List workflows
- [ ] `workflow_status()` - Show workflow status
- [ ] `workflow_run()` - Execute workflow
- [ ] `workflow_resume()` - Resume workflow

## Test Areas
- ✅ Workflow discovery
- ✅ Execution logic
- ✅ State management
- ✅ Error handling

## Acceptance Criteria
- [ ] `tests/unit/test_core_workflows.py` created
- [ ] 80%+ coverage achieved
- [ ] Tests pass in CI/CD
```

---

### Issue 7: Test Coverage for core/context_export.py
```markdown
**Title:** Test Coverage: core/context_export.py

**Labels:** testing, test-coverage, priority-medium, core-module

**Body:**
## Module Information
- **File:** `claude_ctx_py/core/context_export.py`
- **Current Coverage:** 0% (no tests)
- **Target Coverage:** 80%+
- **Priority:** Medium

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

## Priority 2: TUI Modules (Partial/No Tests)

### Issue 8: Test Coverage for TUI modules
```markdown
**Title:** Test Coverage: TUI Components (tui_*.py)

**Labels:** testing, test-coverage, priority-medium, tui

**Body:**
## Module Information
Multiple TUI modules need test coverage:
- `tui_command_palette.py`
- `tui_commands.py`
- `tui_dashboard.py`
- `tui_dialogs.py`
- `tui_extensions.py`
- `tui_format.py`
- `tui_graphs.py`
- `tui_icons.py`
- `tui_notifications.py`
- `tui_overview_enhanced.py`
- `tui_performance.py`
- `tui_progress.py`
- `tui_supersaiyan.py`
- `tui_textual.py`
- `tui_workflow_viz.py`
- `tui_workflows_orchest.py`
- `tui.py`

**Current Coverage:** Minimal/None
**Target Coverage:** 80%+
**Priority:** Medium

## Test Strategy
TUI components can be challenging to test. Focus on:
- ✅ **Logic testing**: Test data transformation, formatting, state management
- ✅ **Component testing**: Test Rich/Textual component generation
- ✅ **Mock rendering**: Mock Console/Live for render tests
- ✅ **Keyboard handling**: Test key press logic

## Suggested Approach
1. Start with pure logic functions (formatters, converters)
2. Test component generation (verify Panel, Table, Text objects)
3. Mock Rich Console for rendering tests
4. Test keyboard handlers with mock events

## Acceptance Criteria
- [ ] Tests created for high-value TUI logic
- [ ] Formatting functions tested
- [ ] Component generation tested
- [ ] Tests pass in CI/CD
- [ ] Focus on testable logic, not visual rendering
```

---

## Priority 3: Utility Modules (No Tests)

### Issue 9: Test Coverage for CLI module
```markdown
**Title:** Test Coverage: cli.py

**Labels:** testing, test-coverage, priority-high, cli

**Body:**
## Module Information
- **File:** `claude_ctx_py/cli.py`
- **Current Coverage:** 0% (no tests)
- **Target Coverage:** 80%+
- **Priority:** High (entry point)

## Functions Needing Tests
- [ ] `build_parser()` - Argument parser construction
- [ ] `main()` - Main entry point with routing
- [ ] All subcommand handlers
- [ ] Error handling and exit codes

## Test Areas
- ✅ Parser construction (all subcommands)
- ✅ Argument validation
- ✅ Command routing
- ✅ Exit codes
- ✅ Error messages

## Test Strategy
Use `argparse` testing patterns:
```python
parser = build_parser()
args = parser.parse_args(['mcp', 'list'])
assert args.command == 'mcp'
assert args.mcp_command == 'list'
```

## Acceptance Criteria
- [ ] `tests/unit/test_cli.py` expanded
- [ ] All subcommands tested
- [ ] 80%+ coverage achieved
- [ ] Tests pass in CI/CD
```

---

### Issue 10: Test Coverage for suggester.py
```markdown
**Title:** Test Coverage: suggester.py

**Labels:** testing, test-coverage, priority-medium

**Body:**
## Module Information
- **File:** `claude_ctx_py/suggester.py`
- **Current Coverage:** 0% (no tests)
- **Target Coverage:** 80%+
- **Priority:** Medium

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

### Issue 11: Test Coverage for error_utils.py
```markdown
**Title:** Test Coverage: error_utils.py

**Labels:** testing, test-coverage, priority-low

**Body:**
## Module Information
- **File:** `claude_ctx_py/error_utils.py`
- **Current Coverage:** 0% (no tests)
- **Target Coverage:** 80%+
- **Priority:** Low

## Functions Needing Tests
All error handling utilities

## Test Areas
- ✅ Error formatting
- ✅ Error recovery
- ✅ Error messages

## Acceptance Criteria
- [ ] `tests/unit/test_error_utils.py` created
- [ ] 80%+ coverage achieved
- [ ] Tests pass in CI/CD
```

---

### Issue 12: Test Coverage for cmd_ai.py
```markdown
**Title:** Test Coverage: cmd_ai.py

**Labels:** testing, test-coverage, priority-medium, ai

**Body:**
## Module Information
- **File:** `claude_ctx_py/cmd_ai.py`
- **Current Coverage:** 0% (no tests)
- **Target Coverage:** 80%+
- **Priority:** Medium

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

## Implementation Plan

### Phase 1: Core Modules (Priority High)
**Target:** Week 1-2
1. Issue 1: `core/base.py`
2. Issue 2: `core/agents.py`
3. Issue 3: `core/modes.py`
4. Issue 4: `core/rules.py`
5. Issue 9: `cli.py`

### Phase 2: Extended Core (Priority Medium)
**Target:** Week 3-4
6. Issue 5: `core/skills.py`
7. Issue 6: `core/workflows.py`
8. Issue 7: `core/context_export.py`
9. Issue 10: `suggester.py`
10. Issue 12: `cmd_ai.py`

### Phase 3: TUI & Utilities (Priority Low-Medium)
**Target:** Week 5-6
11. Issue 8: TUI modules (select high-value components)
12. Issue 11: `error_utils.py`

## Coverage Tracking

Create a tracking issue to monitor progress:

```markdown
**Title:** [META] Test Coverage Tracker - 80% Target

**Body:**
## Overall Progress

**Current Coverage:** TBD
**Target Coverage:** 80%
**Modules Covered:** 0/32

## Core Modules
- [ ] #1 core/base.py
- [ ] #2 core/agents.py
- [ ] #3 core/modes.py
- [ ] #4 core/rules.py
- [ ] #5 core/skills.py
- [ ] #6 core/workflows.py
- [ ] #7 core/context_export.py

## Entry Points
- [ ] #9 cli.py

## AI/Intelligence
- [ ] #10 suggester.py
- [ ] #12 cmd_ai.py

## TUI Components
- [ ] #8 TUI modules

## Utilities
- [ ] #11 error_utils.py

## Coverage Reports
Updated weekly with CI coverage reports.
```

---

## Resources

- **Existing Tests:** Reference `tests/unit/test_mcp.py` for patterns
- **pytest Docs:** https://docs.pytest.org/
- **Coverage Tool:** pytest-cov
- **CI Integration:** GitHub Actions with coverage reporting
