---
name: test-review-request
description: Request a test coverage audit from the Claude CLI. This skill is for non-Claude agents (Codex, Gemini, etc.) that need to audit test quality and coverage gaps for a module. The calling agent MUST shell out to the Claude CLI via the bundled script and read the result file. It must NOT attempt to perform the audit itself. Claude agents are excluded — Claude has native access to the test-review skill.
---

# Test Review Request

Delegate a test coverage audit to the Claude CLI. This skill is for **non-Claude
agents** (Codex, Gemini, and similar) that lack access to the skills ecosystem.
Claude agents do not need this skill — they can audit tests directly using the
`test-review` skill.

## IMPORTANT: Do Not Audit the Tests Yourself

**If you are Codex, Gemini, or any non-Claude agent: your ONLY job is to run the
script and read the output file. Do NOT read source code to map behaviors. Do NOT
classify test coverage. Do NOT produce a gap report. Shell out and read the result.**

The audit requires Claude's skills ecosystem — specifically the `test-review` skill
which pipelines testing standards into a structured audit workflow with Haiku-driven
discovery. Non-Claude agents do not have access to these skills or the project-specific
testing standards. Attempting the audit yourself produces generic, uncalibrated results.
The script invokes a Claude CLI instance with full access.

## How to Invoke

### Step 1: Run the script

```bash
# Full audit of a module (default)
agents/skills/test-review-request/scripts/test-review-request.sh /path/to/module

# Full audit with specific test directory
agents/skills/test-review-request/scripts/test-review-request.sh /path/to/module --tests /path/to/tests

# Quick review of specific test files only
agents/skills/test-review-request/scripts/test-review-request.sh --quick /path/to/test_file.py

# Custom output directory
agents/skills/test-review-request/scripts/test-review-request.sh /path/to/module --output ./my-reports
```

### Step 2: Read the result

The script prints the output file path to stdout on success. Read that file.

```bash
REPORT_FILE=$(agents/skills/test-review-request/scripts/test-review-request.sh src/parser)
cat "$REPORT_FILE"
```

The report contains: behavior inventory (public contract mapping), coverage status
for each behavior (Covered/Shallow/Missing), adversarial analysis findings,
prioritized gap report (P0/P1/P2), and shallow test details with fix recommendations.

### Step 3: Act on findings

- **P0 (Security/Correctness Critical)**: Fix before merge. These are gaps that
  could allow security vulnerabilities or silent incorrect behavior.
- **P1 (Reliability/Edge Cases)**: Fix in current sprint. Missing error handling,
  boundary conditions, concurrency tests.
- **P2 (Completeness/Confidence)**: Backlog. Nice-to-have coverage improvements.

## Anti-Patterns

- **Performing the audit yourself** — You do not have the testing standards or
  audit workflow. Shell out to the script. This is the most common failure mode.
- **Pre-reading source before shelling out** — Unnecessary. The script passes the
  module path to Claude who reads it directly. Do not pre-process it.
- **Ignoring the output file** — The gap report is written to a file. Read it and
  act on the findings. Do not assume it passed.
- **Using sub-agents for the audit** — The script invokes a single Claude CLI
  process. Do not spawn sub-agents.
