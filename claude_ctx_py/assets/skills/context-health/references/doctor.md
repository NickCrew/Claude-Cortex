# Reference: doctor

# /analyze:doctor - System Diagnostics and Context Health Check

## Triggers
- Manual invocation to check system health.
- After significant changes to agents, modes, or rules.
- During troubleshooting to diagnose unexpected behavior.
- Regularly as part of maintenance to ensure an optimized `cortex` environment.

## Usage
```bash
cortex doctor [--fix]
```

## Arguments
- `--fix`: Optional. Attempt to automatically resolve identified issues, such as removing references to non-existent files from `.active-*` lists. (Note: Auto-fix capabilities are under active development).

## Behavioral Flow
1.  **Resolve Context:** Determines the active `cortex` directory.
2.  **Run Checks:** Executes a series of diagnostic checks across different categories:
    *   **Consistency Check:** Verifies that all active components (agents, modes, rules) have corresponding files on the filesystem.
    *   **Duplicate Check:** Identifies agent definition files with identical content (using hash comparison).
    *   **Redundancy Check:** (Future) Identifies unused agents, modes, or rules.
    *   **Optimization Check:** Flags large agent definition files that might impact performance or token usage.
3.  **Generate Report:** Compiles all findings into a human-readable report, categorizing issues by `ERROR`, `WARNING`, or `INFO`.
4.  **Apply Fixes (if `--fix`):** (Future) Attempts to automatically resolve minor issues.

## Key Behaviors
- Provides a comprehensive overview of the `cortex` environment's health.
- Offers actionable suggestions for resolving identified problems.
- Supports an optional auto-fix mode for basic issues.
- Designed to be extensible with new diagnostic checks.

## Personas (Thinking Modes)
- **system-analyst**: System health understanding, pattern recognition, diagnostic methodology
- **quality-engineer**: Quality standards, consistency validation, optimization recommendations

## Delegation Protocol

**This command does NOT delegate** - Doctor runs as direct Python analysis.

**Why no delegation**:
- ❌ Fast filesystem operations (<5 seconds)
- ❌ Simple consistency checks and hash comparisons
- ❌ Direct file system analysis via Python
- ❌ Report generation is straightforward

**All work done directly**:
- Python pathlib for file operations
- Hash comparison for duplicates
- Direct analysis of active component files
- Simple report generation

**Note**: This is a CLI command (`cortex doctor`) that runs Python code directly, not a slash command that would use Task tool. Personas guide the diagnostic logic and report formatting.

## Tool Coordination
- **Python pathlib**: File system operations (direct)
- **Python hashlib**: Content hashing (direct)
- **subprocess**: Future auto-fix (direct)
- **Direct analysis**: No Task tool needed

## Key Patterns
- **Health Monitoring**: Proactive identification of potential issues.
- **Problem Diagnosis**: Clear reporting of what is wrong and why.
- **Guided Resolution**: Provides concrete steps to improve system state.

## Examples

### Basic Health Check
```bash
cortex doctor
# Example Output:
# [PASS] Consistency check
# [WARN] Duplicate check
#   - Identical content found in agents: old-agent.md, new-agent.md
#     Suggestion: Delete duplicate files.
# [PASS] Redundancy check
# [WARN] Optimization check
#   - Agent definition is large (25.3KB) (verbose-agent.md)
#     Suggestion: Consider splitting this agent or removing verbose examples.
```

### Attempt Auto-Fix
```bash
cortex doctor --fix
# Example Output:
# [FAIL] Consistency check
#   - Active mode 'debugging' references missing file (modes/debugging.md)
#     Suggestion: Run 'cortex mode deactivate debugging'
# [PASS] Duplicate check
# [PASS] Redundancy check
# [PASS] Optimization check
# Auto-fix not fully implemented yet.
```

## Boundaries

**Will:**
- Perform comprehensive static code analysis across multiple domains
- Generate severity-rated findings with actionable recommendations
- Provide detailed reports with metrics and improvement guidance

**Will Not:**
- Execute dynamic analysis requiring code compilation or runtime
- Modify source code or apply fixes without explicit user consent
- Analyze external dependencies beyond import and usage patterns
