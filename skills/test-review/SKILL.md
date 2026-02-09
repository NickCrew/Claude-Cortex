---
name: test-review
description: Review test quality and audit test coverage for any module. This skill should be used when reviewing existing tests, auditing test gaps, writing new tests, or when asked to assess test health. It pipelines testing standards into the audit workflow to produce a prioritized gap report. The output is a report, not code — do not write test implementations until the report is reviewed.
---

# Test Review

Review test quality and audit coverage gaps by loading the project testing standards
first, then executing the audit workflow. The pipeline produces a prioritized gap
report — not test code.

## When to Use

- "Review the tests for module X"
- "Audit test coverage for this component"
- "Are these tests any good?"
- "What tests are missing?"
- Before writing new tests (audit first, then write)
- After a significant refactor (verify tests still cover the contract)
- When preparing a module for production

## Pipeline

This skill is a two-phase pipeline. Execute the phases in order. Do not skip
Phase 1 — the standards must be loaded before reviewing any test code.

### Phase 1: Load the Standards

Read the project testing standards to calibrate what "good" looks like:

```
cat skills/test-review/references/testing-standards.md
```

This file defines:
- Anti-patterns to flag (mirror testing, happy-path-only, over-mocking, trivial assertions)
- Required test categories (contract, boundary, failure mode, state transition, integration)
- The self-check checklist for individual tests
- Language-specific standards (Rust, TypeScript/React)
- Coverage expectations by component type
- Naming conventions

**Internalize these before reading any test code.** Every finding in the audit
must reference a specific standard from this file. Do not invent standards — use
the ones defined here.

### Phase 2: Execute the Audit

Read the audit workflow and follow it step by step:

```
cat skills/test-review/references/audit-workflow.md
```

This file defines the four-step audit process:
1. **Map the public contract** — list every behavior the module promises
2. **Map existing test coverage** — mark each behavior as covered, shallow, or missing
3. **Adversarial analysis** — probe input boundaries, error handling, state, integration seams
4. **Produce the gap report** — prioritized findings in the format defined in the file

Follow the process exactly as written. The output format (gap report with P0/P1/P2
priority tiers) is defined in TEST-AUDIT.md. Use it.

## Operating Rules

1. **Standards first, always.** Read testing-standards.md before opening any test file. If
   context has been compressed and the standards are no longer loaded, read them again.

2. **Report, do not fix.** The output is a gap report. Do not write test code unless
   explicitly asked to implement specific gaps from an approved report.

3. **Cite the standard.** Every finding must name which testing-standards.md rule it
   violates or which audit-workflow.md criterion it fails. Findings without citations
   are opinions, not audit results.

4. **Read the source, not just the tests.** The audit requires reading the module
   source to map the public contract (Step 1 of audit-workflow.md). Do not audit tests
   in isolation — the whole point is to find gaps between what the code does and what
   the tests verify.

5. **Do not manufacture gaps.** If a module is well-tested, say so. The gap report
   has a "Well-Tested" section for exactly this purpose.

## Modes

### Full Audit (default)

Execute both phases completely. Produces the full gap report.

Use when: "audit tests for module X", "review test coverage", preparing for production.

### Quick Review

Load testing-standards.md, then review specific test files against the anti-patterns and
self-check checklist only. Skip the full contract-mapping and adversarial analysis.

Use when: reviewing a PR's test changes, spot-checking a single test file,
"are these tests ok?"

### Write Mode

Execute a full audit first, present the gap report, then — only after approval —
write test implementations for approved gaps following the standards in testing-standards.md.

Use when: "audit and fix tests for module X", "write missing tests".

## Common Mistakes

- **Skipping testing-standards.md** — Reviewing tests without loading the standards
  produces generic feedback. The standards are project-specific and opinionated.
- **Writing tests before the report** — The audit produces findings. The user decides
  which to implement. Do not jump ahead.
- **Auditing tests without reading source** — Cannot identify missing coverage without
  knowing what the code does.
- **Citing severity without justification** — P0/P1/P2 assignments have specific
  criteria defined in audit-workflow.md. Use those criteria, not gut feeling.
