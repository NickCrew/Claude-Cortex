#!/usr/bin/env bash
#
# Create GitHub issues for test coverage
# Requires: GitHub CLI (gh)
#
# Usage: ./scripts/create_test_coverage_issues.sh

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI (gh) is not installed${NC}"
    echo "Install it with: brew install gh"
    echo "Then authenticate with: gh auth login"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${RED}Error: Not authenticated with GitHub CLI${NC}"
    echo "Run: gh auth login"
    exit 1
fi

echo -e "${GREEN}Creating test coverage issues...${NC}\n"

# Issue 1: core/base.py
echo -e "${YELLOW}Creating Issue #1: core/base.py${NC}"
gh issue create \
  --title "Test Coverage: core/base.py" \
  --label "testing,test-coverage,priority-high,core-module,good-first-issue" \
  --body "## Module Information
- **File:** \`claude_ctx_py/core/base.py\`
- **Current Coverage:** 0% (no tests)
- **Target Coverage:** 80%+
- **Priority:** 🔴 High (core functionality)

## Functions Needing Tests
- [ ] \`_resolve_claude_dir()\` - Claude directory resolution
- [ ] \`_iter_all_files()\` - File iteration logic
- [ ] \`_agent_basename()\` - Agent name extraction
- [ ] \`_is_disabled()\` - Disabled agent detection
- [ ] \`_extract_agent_name()\` - Name extraction from content
- [ ] \`_read_agent_front_matter_lines()\` - YAML front matter parsing
- [ ] \`_parse_dependencies_from_front()\` - Dependency extraction
- [ ] \`_tokenize_front_matter()\` - Front matter tokenization
- [ ] \`_extract_scalar_from_paths()\` - Scalar value extraction

## Test Areas
- ✅ Path resolution (macOS, Linux, Windows)
- ✅ File iteration with filters
- ✅ Agent naming conventions
- ✅ Front matter parsing (valid, invalid, edge cases)
- ✅ Dependency resolution
- ✅ Error handling

## Acceptance Criteria
- [ ] \`tests/unit/test_core_base.py\` created
- [ ] 80%+ coverage achieved
- [ ] All edge cases tested
- [ ] Tests pass in CI/CD

## Resources
- Reference: \`tests/unit/test_mcp.py\` for testing patterns
- [pytest documentation](https://docs.pytest.org/)"

# Issue 2: core/agents.py
echo -e "${YELLOW}Creating Issue #2: core/agents.py${NC}"
gh issue create \
  --title "Test Coverage: core/agents.py" \
  --label "testing,test-coverage,priority-high,core-module" \
  --body "## Module Information
- **File:** \`claude_ctx_py/core/agents.py\`
- **Current Coverage:** 0% (no tests)
- **Target Coverage:** 80%+
- **Priority:** 🔴 High (core functionality)

## Functions Needing Tests
- [ ] \`list_agents()\` - List all available agents
- [ ] \`agent_status()\` - Show agent activation status
- [ ] \`agent_activate()\` - Activate agents with dependency checking
- [ ] \`agent_deactivate()\` - Deactivate agents
- [ ] \`build_agent_graph()\` - Build dependency graph
- [ ] \`agent_deps()\` - Show agent dependencies
- [ ] \`agent_graph()\` - Generate dependency visualization
- [ ] \`validate_agent()\` - Validate agent metadata against schema

## Test Areas
- ✅ Agent listing (active, disabled, all)
- ✅ Activation/deactivation logic
- ✅ Dependency graph construction
- ✅ Circular dependency detection
- ✅ Validation against schema
- ✅ Error handling (missing files, invalid YAML)

## Acceptance Criteria
- [ ] \`tests/unit/test_core_agents.py\` created
- [ ] 80%+ coverage achieved
- [ ] Dependency graph tests comprehensive
- [ ] Circular dependency detection tested
- [ ] Tests pass in CI/CD"

# Issue 3: core/modes.py
echo -e "${YELLOW}Creating Issue #3: core/modes.py${NC}"
gh issue create \
  --title "Test Coverage: core/modes.py" \
  --label "testing,test-coverage,priority-high,core-module" \
  --body "## Module Information
- **File:** \`claude_ctx_py/core/modes.py\`
- **Current Coverage:** 0% (no tests)
- **Target Coverage:** 80%+
- **Priority:** 🔴 High (core functionality)

## Functions Needing Tests
- [ ] \`list_modes()\` - List available modes
- [ ] \`mode_status()\` - Show active modes
- [ ] \`mode_activate()\` - Activate modes
- [ ] \`mode_deactivate()\` - Deactivate modes

## Test Areas
- ✅ Mode listing (active vs inactive)
- ✅ Activation/deactivation (file moves)
- ✅ Error handling (invalid modes, missing files)
- ✅ Return value verification

## Acceptance Criteria
- [ ] \`tests/unit/test_core_modes.py\` created
- [ ] 80%+ coverage achieved
- [ ] Tests pass in CI/CD"

# Issue 4: core/rules.py
echo -e "${YELLOW}Creating Issue #4: core/rules.py${NC}"
gh issue create \
  --title "Test Coverage: core/rules.py" \
  --label "testing,test-coverage,priority-high,core-module" \
  --body "## Module Information
- **File:** \`claude_ctx_py/core/rules.py\`
- **Current Coverage:** 0% (no tests)
- **Target Coverage:** 80%+
- **Priority:** 🔴 High (core functionality)

## Functions Needing Tests
- [ ] \`list_rules()\` - List available rules
- [ ] \`rules_status()\` - Show active rules
- [ ] \`rules_activate()\` - Activate rules
- [ ] \`rules_deactivate()\` - Deactivate rules

## Acceptance Criteria
- [ ] \`tests/unit/test_core_rules.py\` created
- [ ] 80%+ coverage achieved
- [ ] Tests pass in CI/CD"

# Issue 5: cli.py
echo -e "${YELLOW}Creating Issue #5: cli.py${NC}"
gh issue create \
  --title "Test Coverage: cli.py (argument parsing & command routing)" \
  --label "testing,test-coverage,priority-high,cli" \
  --body "## Module Information
- **File:** \`claude_ctx_py/cli.py\`
- **Current Coverage:** Minimal (only basic tests exist)
- **Target Coverage:** 80%+
- **Priority:** 🔴 High (main entry point)

## Functions Needing Tests
- [ ] \`build_parser()\` - Argument parser construction for all subcommands
- [ ] \`main()\` - Main entry point with command routing
- [ ] All subcommand handlers
- [ ] Error handling and exit codes

## Test Areas
- ✅ Parser construction (all subcommands)
- ✅ Argument validation
- ✅ Command routing
- ✅ Exit codes
- ✅ Error messages

## Acceptance Criteria
- [ ] \`tests/integration/test_cli.py\` expanded
- [ ] All subcommands tested
- [ ] 80%+ coverage achieved
- [ ] Tests pass in CI/CD"

# Issue 6-10: Medium priority
echo -e "${YELLOW}Creating Issues #6-10: Medium priority modules${NC}"

gh issue create --title "Test Coverage: core/skills.py" \
  --label "testing,test-coverage,priority-medium,core-module" \
  --body "See CREATE_THESE_ISSUES.md for details"

gh issue create --title "Test Coverage: core/workflows.py" \
  --label "testing,test-coverage,priority-medium,core-module" \
  --body "See CREATE_THESE_ISSUES.md for details"

gh issue create --title "Test Coverage: core/context_export.py" \
  --label "testing,test-coverage,priority-medium,core-module" \
  --body "See CREATE_THESE_ISSUES.md for details"

gh issue create --title "Test Coverage: suggester.py" \
  --label "testing,test-coverage,priority-medium" \
  --body "See CREATE_THESE_ISSUES.md for details"

gh issue create --title "Test Coverage: cmd_ai.py" \
  --label "testing,test-coverage,priority-medium,ai" \
  --body "See CREATE_THESE_ISSUES.md for details"

# Meta tracking issue
echo -e "${YELLOW}Creating META tracking issue${NC}"
gh issue create \
  --title "[META] Test Coverage Tracker - 80% Target" \
  --label "testing,test-coverage,meta,tracking" \
  --body "## Overall Progress

**Current Coverage:** TBD (need baseline measurement)
**Target Coverage:** 80%
**Modules Tested:** 3/32 (mcp, analytics, composer have tests)

## 🔴 Priority High (Week 1-2)
- [ ] #1 core/base.py
- [ ] #2 core/agents.py
- [ ] #3 core/modes.py
- [ ] #4 core/rules.py
- [ ] #5 cli.py

## 🟡 Priority Medium (Week 3-4)
- [ ] #6 core/skills.py
- [ ] #7 core/workflows.py
- [ ] #8 core/context_export.py
- [ ] #9 suggester.py
- [ ] #10 cmd_ai.py

Track progress at: CREATE_THESE_ISSUES.md"

echo -e "\n${GREEN}✅ All issues created successfully!${NC}"
echo -e "View them at: $(gh repo view --web)"
