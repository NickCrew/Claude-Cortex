# CI/CD & Automation Flags

Flags optimized for continuous integration and automated pipelines.

**Estimated tokens: ~100**

---

**--ci-mode / --headless**
- Trigger: CI/CD pipelines, automation, scripts
- Behavior: Non-interactive, pipeline-friendly execution
- Auto-enables: --quiet, --auto-approve, JSON output, no prompts
- Disables: Interactive features, colored output, progress bars
- Exits: With proper exit codes (0 = success, non-zero = failure)
- Logs: Structured logs suitable for parsing

**--json-output**
- Trigger: Tool integration, parsing, automation
- Behavior: Machine-readable JSON output format
- Related: Structured logs, parseable results, integration-friendly
- Format: JSON lines for streaming, final JSON object for results
- Includes: Status codes, error details, metadata
- Compatible with: `jq`, log aggregators, monitoring tools

**--exit-on-error**
- Trigger: CI/CD pipelines, strict validation
- Behavior: Immediate exit on first error (fail fast)
- Opposite of: --resilient (continue on errors)
- Returns: Non-zero exit code immediately
- Logs: Error details before exiting
- Use when: Pipeline should stop on any failure
