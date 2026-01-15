#!/usr/bin/env bash
# Parallel Workflow & Quality Gate Hook
# Enforces strictly parallel execution, comprehensive quality gates, and structured documentation
#
# Triggers: After user prompt submission for planning, implementation, testing, documentation, or release
# Purpose: Mandate parallel workstreams, enforces coverage (85-95%), documentation quality (8/10), and P0-P2 remediation

set -euo pipefail

# Configuration
COVERAGE_MIN=85
COVERAGE_TARGET=95
DOCS_SCORE_MIN=8.0
CODE_REVIEW_REQUIRED=true

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() { echo -e "${BLUE}[Workflow Enforcer]${NC} $1" >&2; }
log_success() { echo -e "${GREEN}[Workflow Enforcer]${NC} $1" >&2; }
log_warning() { echo -e "${YELLOW}[Workflow Enforcer]${NC} $1" >&2; }
log_error() { echo -e "${RED}[Workflow Enforcer]${NC} $1" >&2; }

# Check if this is a relevant task
is_workflow_task() {
    local prompt="$1"
    local keywords=(
        "plan" "implement" "test" "document" "release"
        "roadmap" "architecture" "design" "build" "code"
        "feature" "diagram" "review" "refactor"
    )

    for keyword in "${keywords[@]}"; do
        if echo "$prompt" | grep -qi "$keyword"; then
            return 0
        fi
    done
    return 1
}

main() {
    local user_prompt="${CLAUDE_HOOK_PROMPT:-${CLAUDE_USER_PROMPT:-}}"

    if ! is_workflow_task "$user_prompt"; then
        log_info "No workflow triggers detected. Skipping."
        exit 0
    fi

    log_info "Workflow Trigger Detected - Enforcing Parallel Execution & Quality Gates"

    # 1. Activate Core & Specialist Agents
    # We try to activate all potentially needed agents. Failures are logged but non-fatal (|| true).
    
    log_info "Activating Workflow Agents..."
    
    # Core Engineering
    cortex agent activate test-automator quality-engineer code-reviewer >&2 || true
    
    # Documentation & Release
    cortex agent activate tutorial-engineer api-documenter technical-writer mermaid-expert docs-architect deployment-engineer >&2 || true
    
    # Run AI Auto-Activation for context-specific specialists (e.g. security, react, sql)
    log_info "Running AI analysis for specialized agents..."
    cortex ai auto-activate >&2 || true

    # 2. Inject The Workflow Directive
    cat <<INSTRUCTIONS

# 🚀 Parallel Workflow & Quality Gate Directive

**CRITICAL INSTRUCTION:** You must optimize for **PARALLEL EXECUTION** at all times. Serial execution is permitted ONLY when explicit blocking dependencies exist.

## 1. Global Concurrency Protocol
- **Planning Phase:** Identify independent subtasks immediately.
- **Execution Phase:** Run Implementation and Test Writing workstreams **IN PARALLEL**.
- **Review Phase:** All reviewers (Quality, Code, Security, etc.) must assess **SIMULTANEOUSLY**.
- **Remediation:** Fix independent issues (P0-P2) **IN PARALLEL**.

---

## 2. Workstream Definitions & Gates

### A. Planning Workstream
- **Entry:** Project scope / Feature request
- **Activities:** 
  - Break down tasks.
  - **Construct Dependency Graph:** Identify critical path.
  - **Populate Task Queue:** Assign workstreams.
- **Exit:** Validated Plan, Detailed Task Breakdown.
- **Metrics:** Plan completeness, Dependency accuracy.

### B. Implementation Workstream (Stream I)
- **Entry:** Validated Plan.
- **Activities:** Write/Refactor code.
- **Exit:** Feature complete code.
- **Metrics:** Adherence to spec, Code quality.

### C. Testing Workstream (Stream T) - RUNS PARALLEL TO STREAM I
- **Entry:** Validated Plan (start writing tests immediately).
- **Activities:** 
  - Write Unit/Integration tests.
  - Run tests against Implemented Code (Sync Point).
- **Exit:** Test suite passing.
- **Quality Gate:** **${COVERAGE_MIN}-${COVERAGE_TARGET}% Code Coverage**.
- **Metrics:** Test pass rate, Coverage %.

### D. Documentation Workstream (Final Phase)
- **Entry:** All previous workstreams complete (Implementation + Testing + Remediation).
- **Activities:**
  - **Tutorials:** (tutorial-engineer) for significant user changes.
  - **API Docs:** (api-documenter) for API changes.
  - **Release Notes:** (deployment-engineer/release-manager) if release detected.
  - **General Docs:** (technical-writer) for architecture/dev docs.
  - **Diagrams:** (mermaid-expert) ASCII Draft -> Mermaid -> PNG Embed.
- **Structure:** 
  - `docs/projects/{plans,activity}`
  - `docs/architecture`
- **Quality Gate:** **docs-architect Review Score ≥ 8/10**. (Loop until passed).
- **Exit:** Reviewed docs, diagrams, release notes.

---

## 3. Execution & Management Guidelines

1.  **Dependency Graph:** Always maintain a mental or written graph of task sequencing.
2.  **Status Reporting:** Provide updates on the status of each workstream (e.g., [Stream I: Active, Stream T: Active]).
3.  **Remediation Scope:**
    - **P0/Critical, P1/High, P2/Medium:** MANDATORY FIX.
    - **Low Severity:** Optional (fix if time permits).
    - **Deferred Tasks:** Must be documented in `docs/projects/plans/DEFERRED.md`.
4.  **Validation:** Post-execution validation is required for all fixes.

## 4. Anti-Pattern Prevention: The "Intent vs. Deliverable" Trap

**STOP AND READ:** A common failure mode is producing artifacts that document *intent* (plans, summaries, "I will do X") but failing to produce the *actual deliverables* (code files, test files).

**STRICT PROHIBITIONS:**
- ❌ **Do NOT** mark a task complete because you "planned" it.
- ❌ **Do NOT** say "I have implemented..." unless the files exist on disk.
- ❌ **Do NOT** output code blocks in conversation without writing them to files.

**MANDATORY VERIFICATION (Proof of Work):**
1.  **File Existence Check:** You must verify artifacts exist (e.g., `ls -l src/foo.py`) before proceeding to the next phase.
2.  **Test Execution:** You must RUN the tests and see the output, not just write them.
3.  **Final Report:** Your final status MUST list the specific files created/modified and the actual test execution logs.

**Rule of Thumb:** If `ls -l` cannot see it, it does not exist. If `pytest` has not run, it works in theory only. **DELIVERABLES MUST BE TANGIBLE.**

---

**You are now operating under the Parallel Workflow Protocol.**
**Analyze the request, build the Dependency Graph, and launch Parallel Workstreams.**

INSTRUCTIONS

    exit 0
}

main "$@"
