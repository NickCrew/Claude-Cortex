# Refactoring & Safety Flags

Flags for safe code transformation and behavior preservation.

**Estimated tokens: ~140**

---

**--refactor-safe**
- Trigger: Large refactorings, legacy code changes
- Behavior: Maximum safety checks, behavior preservation validation
- Auto-enables: Comprehensive tests before/after, diff analysis, rollback plan
- Validates: Output equivalence, performance parity, no regressions
- Generates: Safety report with risk assessment
- Requires: Explicit confirmation before applying changes

**--preserve-behavior**
- Trigger: Critical refactorings, production code
- Behavior: Strict behavior preservation with automated verification
- Related: Generates characterization tests, validates output equivalence
- Tests: Input/output pairs, edge cases, performance benchmarks
- Fails: If any behavior change detected
- Documents: Proof of equivalence with test results

**--modernize [python|typescript|react|etc]**
- Trigger: Legacy code updates, framework upgrades
- Behavior: Update to latest language/framework patterns and standards
- Example: `--modernize python` → Python 3.13+ features, type hints, async
- Includes: Dependency updates, API migrations, pattern replacements
- Preserves: Functionality while improving code quality
- Reports: List of modernizations applied with rationale
