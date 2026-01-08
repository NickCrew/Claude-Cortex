#!/usr/bin/env bash
# Implementation Quality Gate Hook
# Enforces test coverage, documentation, and code review requirements after implementations
#
# Triggers: After user prompt submission
# Purpose: Ensure all implementations have tests (>=85% coverage), documentation (>=7.5/10), and code review (high/medium issues resolved)

set -euo pipefail

# Configuration
COVERAGE_THRESHOLD=85
MIN_COVERAGE_FOR_AUTO_PROCEED=85
DOCS_REVIEW_THRESHOLD=7.5
CODE_REVIEW_REQUIRED=true

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[Quality Gate]${NC} $1" >&2
}

log_success() {
    echo -e "${GREEN}[Quality Gate]${NC} $1" >&2
}

log_warning() {
    echo -e "${YELLOW}[Quality Gate]${NC} $1" >&2
}

log_error() {
    echo -e "${RED}[Quality Gate]${NC} $1" >&2
}

# Check if this is an implementation task
is_implementation_task() {
    local prompt="$1"

    # Keywords that indicate implementation work
    local impl_keywords=(
        "implement"
        "add feature"
        "create function"
        "build"
        "write code"
        "add method"
        "create class"
        "develop"
        "code"
    )

    for keyword in "${impl_keywords[@]}"; do
        if echo "$prompt" | grep -qi "$keyword"; then
            return 0
        fi
    done

    return 1
}

# Check if test files were modified/created
has_test_changes() {
    # Check git diff for test files
    if git rev-parse --git-dir > /dev/null 2>&1; then
        local test_changes=$(git diff --name-only --cached 2>/dev/null | grep -E "(test_|_test\.py|\.test\.|spec\.)" || true)
        [[ -n "$test_changes" ]]
    else
        # Not a git repo, assume tests might be needed
        return 0
    fi
}

# Detect change type for documentation routing
detect_change_type() {
    local prompt="$1"

    # User-facing keywords
    local user_facing_keywords=(
        "user interface"
        "UI"
        "frontend"
        "user experience"
        "UX"
        "user feature"
        "end user"
        "tutorial"
        "guide"
        "workflow"
    )

    # API/Library keywords
    local api_keywords=(
        "API"
        "endpoint"
        "library"
        "SDK"
        "public method"
        "interface"
        "module"
        "package"
        "function"
        "class"
    )

    # Check for user-facing changes
    for keyword in "${user_facing_keywords[@]}"; do
        if echo "$prompt" | grep -qi "$keyword"; then
            echo "user-facing"
            return 0
        fi
    done

    # Check for API/library changes
    for keyword in "${api_keywords[@]}"; do
        if echo "$prompt" | grep -qi "$keyword"; then
            echo "api"
            return 0
        fi
    done

    # Default to API documentation for code implementations
    echo "api"
}

# Detect test framework and run tests
detect_and_run_tests() {
    local project_dir="${1:-.}"

    # Python projects (pytest, unittest)
    if [[ -f "pyproject.toml" ]] || [[ -f "pytest.ini" ]] || [[ -f "setup.py" ]]; then
        if command -v pytest &> /dev/null; then
            log_info "Running pytest..."
            if pytest --cov --cov-report=term-missing --cov-report=json 2>&1; then
                return 0
            else
                return 1
            fi
        elif command -v python &> /dev/null; then
            log_info "Running unittest..."
            if python -m unittest discover 2>&1; then
                return 0
            else
                return 1
            fi
        fi
    fi

    # Node/TypeScript projects (jest, vitest)
    if [[ -f "package.json" ]]; then
        if grep -q "\"test\":" package.json; then
            log_info "Running npm test..."
            if npm test 2>&1; then
                return 0
            else
                return 1
            fi
        fi
    fi

    # Go projects
    if [[ -f "go.mod" ]]; then
        log_info "Running go test..."
        if go test -cover ./... 2>&1; then
            return 0
        else
            return 1
        fi
    fi

    # Rust projects
    if [[ -f "Cargo.toml" ]]; then
        log_info "Running cargo test..."
        if cargo test 2>&1; then
            return 0
        else
            return 1
        fi
    fi

    log_warning "No test framework detected"
    return 2  # Unknown/no test framework
}

# Extract coverage percentage from common formats
extract_coverage() {
    local coverage_file="${1:-coverage.json}"

    # Try pytest-cov JSON format
    if [[ -f "coverage.json" ]]; then
        local total_coverage=$(python3 -c "import json; data=json.load(open('coverage.json')); print(data.get('totals', {}).get('percent_covered', 0))" 2>/dev/null || echo "0")
        echo "$total_coverage"
        return 0
    fi

    # Try to parse from test output (last resort)
    # This is fragile and framework-specific
    echo "0"
}

# Main hook logic
main() {
    local user_prompt="${CLAUDE_USER_PROMPT:-}"

    # Skip if not an implementation task
    if ! is_implementation_task "$user_prompt"; then
        log_info "Not an implementation task, skipping quality gate"
        exit 0
    fi

    log_info "Implementation detected - enforcing quality gate"

    # Detect change type for documentation routing
    local change_type=$(detect_change_type "$user_prompt")
    log_info "Change type detected: $change_type"

    # Check if test-automator agent is active
    if ! cortex agent status | grep -q "test-automator (active)"; then
        log_warning "test-automator agent not active, activating..."
        cortex agent activate test-automator >&2 || true
    fi

    # Check if documentation agents are active
    local doc_agents=()
    if [[ "$change_type" == "user-facing" ]]; then
        doc_agents=("tutorial-engineer" "technical-writer")
    else
        doc_agents=("api-documenter")
    fi

    for agent in "${doc_agents[@]}"; do
        if ! cortex agent status | grep -q "$agent (active)"; then
            log_warning "$agent agent not active, activating..."
            cortex agent activate "$agent" >&2 || true
        fi
    done

    # Always check docs-architect
    if ! cortex agent status | grep -q "docs-architect (active)"; then
        log_warning "docs-architect agent not active, activating..."
        cortex agent activate docs-architect >&2 || true
    fi

    # Run AI Auto-Activation to bring in specialized reviewers (Multi-Reviewer Activation)
    log_info "Running AI analysis to detect specialized reviewers..."
    cortex ai auto-activate >&2 || true

    # Check if code review agents are active
    if [[ "$CODE_REVIEW_REQUIRED" == "true" ]]; then
        if ! cortex agent status | grep -q "quality-engineer (active)"; then
            log_warning "quality-engineer agent not active, activating..."
            cortex agent activate quality-engineer >&2 || true
        fi
        if ! cortex agent status | grep -q "code-reviewer (active)"; then
            log_warning "code-reviewer agent not active, activating..."
            cortex agent activate code-reviewer >&2 || true
        fi
    fi

    # Inject quality gate instructions into the conversation
    cat <<INSTRUCTIONS

# 🔒 Implementation Quality Gate Active

**MANDATORY WORKFLOW:**

## Phase 1: Testing (test-automator agent)

1. **Write Tests**
   - Use test-automator agent for test generation
   - Coverage requirement: ≥85%
   - If coverage <85%, you MUST ask user permission to proceed

2. **Run Test Suite**
   - Execute all tests (new + pre-existing)
   - All tests must pass

3. **Handle Test Failures**
   - Pre-existing test failures: Fix source code (DO NOT modify tests)
   - To skip or modify pre-existing tests: ASK USER PERMISSION FIRST
   - Never silently comment out or disable failing tests

## Phase 2: Documentation

**Change Type Detected:** $change_type

INSTRUCTIONS

    if [[ "$change_type" == "user-facing" ]]; then
        cat <<'INSTRUCTIONS'

**User-Facing Changes - Use tutorial-engineer + technical-writer:**

4. **Create/Update User Documentation**
   - tutorial-engineer: Create tutorials, guides, walkthroughs
   - technical-writer: Write clear, user-friendly documentation
   - Include: Installation, usage examples, screenshots/diagrams
   - Format: Markdown with proper headings, code blocks, examples

INSTRUCTIONS
    else
        cat <<'INSTRUCTIONS'

**API/Library Changes - Use api-documenter:**

4. **Create/Update Developer Documentation**
   - api-documenter: Document APIs, functions, classes, modules
   - Include: Function signatures, parameters, return types, examples
   - Format: Docstrings/JSDoc + external API reference
   - Coverage: All public interfaces

INSTRUCTIONS
    fi

    cat <<INSTRUCTIONS

5. **Documentation Review (docs-architect)**
   - docs-architect reviews all documentation
   - Minimum score required: ≥7.5/10
   - If score <7.5, you MUST revise documentation
   - Criteria: Clarity, completeness, accuracy, examples, formatting

## Phase 3: Code Review

6. **Request Code Review (quality-engineer AND code-reviewer)**
   - quality-engineer: Assess code quality, maintainability, best practices
   - code-reviewer: Review for bugs, edge cases, performance, security
   - Both agents provide feedback with priority levels

7. **Resolve Issues by Priority**
   - **HIGH priority:** MUST fix immediately (blocking issues)
   - **MEDIUM priority:** MUST fix (quality/maintainability issues)
   - **LOW priority:** Nice to have (user may decline)
   - To skip HIGH/MEDIUM issues: ASK USER PERMISSION FIRST

8. **Re-review if Needed**
   - After fixing HIGH/MEDIUM issues, request re-review
   - Ensure all critical feedback addressed
   - LOW priority items: ask user if they want to address

## Validation Checklist

- [ ] Tests written using test-automator agent
- [ ] Coverage ≥85% OR user permission granted
- [ ] All pre-existing tests still pass
- [ ] New tests pass
- [ ] Documentation created/updated using appropriate agents
- [ ] docs-architect review score ≥7.5/10
- [ ] Code review completed (quality-engineer + code-reviewer)
- [ ] All HIGH priority issues resolved
- [ ] All MEDIUM priority issues resolved OR user permission granted
- [ ] No tests skipped/modified without permission

## Exit Criteria

✅ All tests pass + coverage ≥85% + docs review ≥7.5 + HIGH/MEDIUM issues resolved → Implementation complete
⚠️  Coverage <85% → Request user approval to proceed
⚠️  Docs review <7.5 → Revise documentation until passing
⚠️  HIGH/MEDIUM issues found → Fix immediately OR request user permission
🚫 Pre-existing tests fail → Fix code, do not modify tests without permission

## Agent Orchestration

**Active for this task:**
- test-automator (testing)
INSTRUCTIONS

    if [[ "$change_type" == "user-facing" ]]; then
        echo "- tutorial-engineer (user guides)"
        echo "- technical-writer (user documentation)"
    else
        echo "- api-documenter (API/library documentation)"
    fi

    echo "- docs-architect (documentation review)"

    if [[ "$CODE_REVIEW_REQUIRED" == "true" ]]; then
        echo "- quality-engineer (code quality review)"
        echo "- code-reviewer (code review for bugs/security)"
    fi

    echo "- Plus any specialized reviewers activated by AI (e.g., security-auditor, react-specialist)"
    echo ""

    exit 0
}

# Execute main function
main "$@"
