# Design: Doctor Command (`/ctx:doctor`)

## Objective
Implement a `doctor` command (`claude-ctx doctor`) to diagnose, validate, and optimize the `claude-ctx` environment. This tool acts as a system health check, ensuring the integrity of Claude's context.

## Core Responsibilities

1.  **Consistency Verification (Real vs. Expected Context)**
    *   **Goal:** Ensure `claude-ctx`'s internal state matches the actual file system.
    *   **Checks:**
        *   Verify all entries in `.active-modes`, `.active-rules`, etc., point to existing files.
        *   Verify that all required "Base" agents/modes for the active profile are actually present.
        *   Detect "Zombie" states: Config files pointing to deleted resources.

2.  **Duplicate Detection**
    *   **Goal:** Prevent context pollution from duplicate definitions.
    *   **Checks:**
        *   Identify agents/modes with identical names (case-insensitive).
        *   Identify agents/modes with identical content (hash comparison).

3.  **Redundancy Analysis**
    *   **Goal:** Identify unused resources.
    *   **Checks:**
        *   Agents not used in any Mode or Workflow.
        *   Modes that activate no agents/rules.

4.  **Optimization Recommendations**
    *   **Goal:** Improve performance and reduce token usage.
    *   **Checks:**
        *   Warn about excessively large context files (>10KB).
        *   Warn about too many active agents (>5).

## Architecture

### 1. Core Module: `claude_ctx_py/core/doctor.py`
A new module containing the diagnostic logic.

**Data Structures:**
```python
@dataclass
class Diagnosis:
    category: str  # e.g., "Consistency", "Optimization"
    level: str     # "ERROR", "WARNING", "INFO"
    message: str
    resource: Optional[str]
    suggestion: Optional[str]
```

**Key Functions:**
*   `doctor_run(fix: bool = False) -> Tuple[int, str]`: Main entry point.
*   `check_consistency(claude_dir: Path) -> List[Diagnosis]`
*   `check_duplicates(claude_dir: Path) -> List[Diagnosis]`
*   `check_redundancy(claude_dir: Path) -> List[Diagnosis]`
*   `check_optimizations(claude_dir: Path) -> List[Diagnosis]`

### 2. CLI Integration: `claude_ctx_py/cli.py`
*   Add `_build_doctor_parser` to register the `doctor` subcommand.
*   Add `_handle_doctor_command` to execute `core.doctor_run`.

## Usage
```bash
claude-ctx doctor
# Output:
# [ERROR] Consistency: Active mode 'debugging' references missing file 'modes/debugging.md'.
# [WARN]  Optimization: Agent 'verbose-logger' is 25KB. Consider splitting.
# [INFO]  Redundancy: Agent 'old-test' is never used.
```

```bash
claude-ctx doctor --fix
# Attempts to auto-resolve issues (e.g., removing missing entries from .active-* files).
```
