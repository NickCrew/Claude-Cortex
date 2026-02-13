# Agent Workflow Loops

This document defines the operational loops that Codex and Gemini agents follow when making code changes and writing tests. Each loop has explicit entry criteria, exit criteria, and escalation rules. If you are an agent, follow these loops exactly.

**You do not review your own work.** All reviews are performed by Claude via dedicated skills. You never grade your own homework.

**Related documents:**
- `TESTING.md` — Test quality standards (how to write tests)
- `TEST-AUDIT.md` — Test gap discovery (how to find what's missing)

---

## Architecture: Who Does What

| Role | Agent | How |
|------|-------|-----|
| **Implementer** | Codex or Gemini | Writes code changes and test code |
| **Code Reviewer** | Claude | Invoked via `specialist-review` skill |
| **Test Reviewer** | Claude | Invoked via `test-review-request` skill |
| **Test Auditor** | Claude | Uses `test-review` skill internally |
| **Remediator** | Codex or Gemini | Fixes findings from Claude's reviews |

**Critical rule:** Codex and Gemini NEVER self-review. Every review step means invoking a skill to send work to Claude. If you cannot invoke the review skill, STOP and escalate — do not substitute your own review.

---

## Skill Invocation Reference

### `specialist-review` — Request Code Review from Claude

**When:** After completing implementation, after each remediation cycle.
**What to send:** The changed files (full content or diff), the task spec, and the iteration number.
**What you get back:** Findings with severity levels (P0-P3) and a verdict (BLOCKED / PASS WITH ISSUES / CLEAN).

### `test-review-request` — Request Test Review from Claude

**When:** After writing tests, after each test remediation cycle.
**What to send:** The test files, the source files they test, and the gap report (if from audit loop).
**What you get back:** Findings on test quality per `TESTING.md` standards, with severity and specific remediation guidance.

---

## Overview

There are two primary loops. They run sequentially — the code loop completes before the test loop begins.

```
┌─────────────────────────────────────────────────────────────────┐
│                        CODE CHANGE LOOP                         │
│  Implement → specialist-review → Remediate → specialist-review  │
│  Exit: all P0/P1 findings resolved                              │
│  Output: clean code + issues filed for P2+                      │
├─────────────────────────────────────────────────────────────────┤
│                        TEST WRITING LOOP                        │
│  Audit → Write Tests → test-review-request → Remediate → ...   │
│  Exit: all P0/P1 gaps covered                                   │
│  Output: tests passing + issues filed for P2+                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Loop 1: Code Change Loop

### Severity Levels

| Severity | Meaning | Loop Behavior |
|----------|---------|---------------|
| 🔴 **P0** | Security flaw, incorrect behavior, data loss, crashes | MUST fix before exit |
| 🟠 **P1** | Error handling gaps, resource leaks, missing validation, concurrency issues | MUST fix before exit |
| 🟡 **P2** | Code quality, naming, documentation, minor edge cases | File issue, do not block |
| ⚪ **P3** | Style preferences, optional improvements, future optimization | File issue, do not block |

### The Loop

```
ENTRY: Task spec or ticket describing the required change.

┌──────────────────┐
│  IMPLEMENT       │ ← You (Codex/Gemini): write the code change per spec
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ specialist-review│ ← Invoke skill: send changed files + spec to Claude
└──────┬───────────┘   Claude returns findings with severities
       │
       ├── Findings? ──► Yes ──► Any P0 or P1? ──► Yes ──┐
       │                                                   │
       │                        No ──► File P2/P3 issues   │
       │                               Exit loop ✅        │
       │                                                   │
       │   No findings ──► Exit loop ✅                    │
       │                                                   │
       ▼                                                   ▼
                                          ┌──────────────────┐
                                          │  REMEDIATE       │ ← You: fix ONLY P0/P1
                                          └──────┬───────────┘   findings cited by Claude
                                                 │
                                                 ▼
                                          ┌──────────────────┐
                                          │ specialist-review│ ← Invoke skill again
                                          └──────┬───────────┘   Send ONLY the remediated
                                                 │               files + prior findings
                                                 └── Loop back to findings check
```

### Circuit Breaker

**Maximum iterations: 3 `specialist-review` cycles.**

If P0/P1 findings remain after 3 cycles:
1. Stop. Do not attempt a 4th remediation.
2. Produce a summary of unresolved findings with context on why they persist.
3. Escalate to human reviewer with the summary and Claude's last review output.

This prevents infinite loops when you keep introducing new issues while fixing old ones, or when a finding requires a design-level change you can't make in remediation scope.

### Code Review Checklist (Claude's Criteria)

Claude evaluates against these criteria via `specialist-review`. You need to understand these so you can anticipate and prevent issues before review, and correctly interpret findings during remediation.

**Correctness:**
- [ ] Does the code do what the spec says? Not more, not less.
- [ ] Are all error cases handled? No unwrap() on fallible operations in non-test code (Rust). No unhandled promise rejections (TS).
- [ ] Are numeric operations safe from overflow/underflow?
- [ ] Are string operations safe with unicode input?
- [ ] Does the code handle empty/zero/None inputs?

**Security (when applicable):**
- [ ] Is untrusted input validated before use?
- [ ] Are auth checks present on protected paths?
- [ ] Is sensitive data (keys, tokens) excluded from logs and error messages?
- [ ] Are timing-safe comparisons used for secrets?

**Patterns and conventions:**
- [ ] Does the code follow existing patterns in the codebase? (highest precedence)
- [ ] Are new types/functions placed in the right modules?
- [ ] Do public APIs have doc comments?
- [ ] Are error types specific and actionable?

**Resource management:**
- [ ] Are connections, file handles, and locks properly released?
- [ ] Are timeouts set on all I/O operations?
- [ ] Do caches/pools have bounded capacity?
- [ ] Is cleanup handled on error paths, not just success paths?

**Concurrency (when applicable):**
- [ ] Is shared state accessed through appropriate synchronization?
- [ ] Are lock scopes minimized?
- [ ] Could this deadlock? (nested locks, await while holding lock)

### Review Output Format (What Claude Returns)

Claude's `specialist-review` response will follow this format. Parse it to determine your next action.

```markdown
## Code Review: [change description]

**Files reviewed:** [list]
**Iteration:** N of 3

### Findings

#### 🔴 P0-001: [title]
**File:** `src/tunnel.rs:45-52`
**Issue:** [what's wrong]
**Impact:** [what happens if not fixed]
**Suggested fix:** [specific guidance, not just "fix this"]

#### 🟠 P1-001: [title]
**File:** `src/auth.rs:23`
**Issue:** [what's wrong]
**Impact:** [what happens if not fixed]
**Suggested fix:** [specific guidance]

#### 🟡 P2-001: [title]
**File:** `src/config.rs:100`
**Issue:** [what's wrong]
**Recommendation:** [what to improve]

### Summary
- P0: N findings (MUST fix)
- P1: N findings (MUST fix)
- P2: N findings (file issues)
- P3: N findings (file issues)
- **Verdict:** BLOCKED / PASS WITH ISSUES / CLEAN
```

### Remediation Rules

When fixing findings from Claude's review:
- Fix ONLY the cited findings. Do not refactor adjacent code.
- Do not introduce new functionality while remediating.
- If a fix requires changing the approach significantly, note this in the remediation and let Claude evaluate the full new approach on the next `specialist-review` cycle.
- Each remediated finding should be annotated: `Fixed P0-001: [what was changed]`
- If you disagree with a finding, see "Disagreeing with Claude's Findings" below — do not silently skip it.

---

## Loop 2: Test Writing Loop

This loop runs after the code change loop exits cleanly. It ensures the new (and existing) code has adequate test coverage.

### Roles

| Role | Agent | Skill |
|------|-------|-------|
| **Auditor** | Claude | `test-review` (internal) — discovers gaps per `TEST-AUDIT.md` |
| **Test Writer** | Codex or Gemini | Writes tests per `TESTING.md` standards |
| **Test Reviewer** | Claude | `test-review-request` — reviews test quality |

### The Loop

```
ENTRY: Code change loop has exited cleanly.

┌──────────────────────┐
│   AUDIT              │ ← Claude runs TEST-AUDIT.md process
└──────┬───────────────┘   via test-review skill against changed modules
       │                   Output: prioritized gap report
       ▼
┌──────────────────────┐
│  SCOPE APPROVAL      │ ← Human reviews gap report
└──────┬───────────────┘   P0/P1 auto-approved. P2+ at human discretion.
       │                   Approved gaps become your work list.
       ▼
┌──────────────────────┐
│  WRITE TESTS         │ ← You (Codex/Gemini): write tests for P0 first,
└──────┬───────────────┘   then P1. Follow TESTING.md standards.
       │
       ▼
┌──────────────────────┐
│  VERIFY TESTS        │ ← You: run the tests locally. They must:
└──────┬───────────────┘   1. Compile / pass lint
       │                   2. All pass (no test is born failing)
       │                   3. Actually exercise the code (not no-ops)
       ▼
┌──────────────────────┐
│ test-review-request  │ ← Invoke skill: send test files + source files
└──────┬───────────────┘   + gap report to Claude for review
       │
       ├── Findings? ──► Yes ──► Any P0 or P1? ──► Yes ──┐
       │                                                   │
       │                        No ──► File P2/P3 issues   │
       │                               Proceed ▼           │
       │                                                   │
       │   No findings ──► Proceed ▼                       │
       │                                                   │
       │                                                   ▼
       │                                   ┌──────────────────┐
       │                                   │  REMEDIATE       │ ← You: fix cited findings
       │                                   └──────┬───────────┘
       │                                          │
       │                                          ▼
       │                                   ┌──────────────────┐
       │                                   │ test-review-     │ ← Invoke skill again
       │                                   │ request          │
       │                                   └──────┬───────────┘
       │                                          │
       │                                          └── Loop back
       ▼
┌──────────────────────┐
│  GAP CHECK           │ ← Claude re-runs audit on the same modules
└──────┬───────────────┘   Compare against original gap report
       │
       ├── All P0/P1 gaps covered? ──► Yes ──► Exit loop ✅
       │                                       File issues for P2+
       │
       └── No ──► Back to WRITE TESTS for remaining gaps
```

### Test Review Checklist (Claude's Criteria)

Claude evaluates against these criteria via `test-review-request`. Understand these so you write tests that pass review on the first cycle.

**Anti-pattern detection:**
- [ ] No mirror testing — expected values are hardcoded, not computed from implementation
- [ ] No happy-path-only — each tested behavior has at least one edge case or failure test
- [ ] No over-mocking — mocks only at external boundaries (network, fs, time)
- [ ] No trivial assertions — every assertion tests a meaningful contract
- [ ] No framework plumbing tests — setup is not >60% of the test body

**Coverage quality:**
- [ ] Every P0 gap from the audit has a corresponding test
- [ ] Every P1 gap from the audit has a corresponding test
- [ ] Test names describe scenario and expected outcome
- [ ] Error tests check specific error types/messages, not just `is_err()`
- [ ] Async tests use real connections where practical (not all mocked)

**Test hygiene:**
- [ ] Tests are independent (no ordering dependency, no shared mutable state)
- [ ] Tests clean up after themselves (no leaked listeners, temp files, etc.)
- [ ] Tests run in <5 seconds individually (no unnecessary sleeps)
- [ ] Flaky conditions are handled (retry, deterministic ports, controlled time)

### Test Review Severity

| Severity | Meaning | Example |
|----------|---------|---------|
| 🔴 **P0** | Test provides false confidence — looks like it covers a behavior but doesn't actually verify it | Mirror test, assertion that can never fail, test that passes with implementation deleted |
| 🟠 **P1** | Test is meaningful but incomplete or fragile | Happy path only, hardcoded port that could conflict, timing-dependent assertion |
| 🟡 **P2** | Test works but could be improved | Poor naming, verbose setup that should be a helper, missing error context in assertion |
| ⚪ **P3** | Stylistic | Ordering of assertions, test grouping |

### Circuit Breaker

**Maximum iterations: 3 `test-review-request` cycles.**

If the audit still shows P0/P1 gaps after 3 write/review cycles, escalate to human with a summary of what's proving difficult to test and why (usually indicates the code needs refactoring to be testable — that's a design problem, not a test problem).

---

## Loop 3: Issue Filing

After both loops exit, file issues for everything that was deferred.

### Issue Template

```markdown
## [P2/P3] [Module]: [Brief description]

**Source:** [Code Review / Test Audit] iteration N
**Severity:** P2 | P3
**Module:** [file path]

### Description
[What's missing or what could be improved]

### Context
[Why this was deferred — not blocking but worth addressing]

### Suggested approach
[Brief guidance on how to address]

### Acceptance criteria
[How to verify this is done]
```

### Filing Rules

- One issue per finding. Do not batch unrelated findings.
- P2 issues get the label `quality` or `test-gap` as appropriate.
- P3 issues get the label `improvement`.
- Issues from test audits reference the specific behavior from the gap report.
- Issues include enough context that a different agent (or human) can pick them up without re-auditing.

---

## Operational Notes

### Agent Responsibilities Summary

**You (Codex / Gemini) are responsible for:**
- Reading and understanding the task spec
- Writing implementation code
- Writing test code
- Running tests locally and verifying they pass
- Invoking `specialist-review` after implementation and each remediation
- Invoking `test-review-request` after writing tests and each remediation
- Fixing ONLY the findings Claude identifies (no scope creep during remediation)
- Filing P2/P3 issues when loop exits
- Escalating when circuit breaker triggers

**You are NOT responsible for:**
- Reviewing your own code (Claude does this)
- Reviewing your own tests (Claude does this)
- Auditing test gaps (Claude does this)
- Deciding whether a finding is valid (if you disagree, note it in the remediation and let Claude re-evaluate — do not silently skip findings)

### Disagreeing with Claude's Findings

If Claude flags something you believe is incorrect:
1. Do NOT silently ignore the finding.
2. In your remediation response, explicitly state: `Disputed P1-003: [your reasoning]`
3. Send back to `specialist-review` / `test-review-request` with the dispute noted.
4. Claude will either accept your reasoning or reaffirm the finding with additional context.
5. If still disputed after 2 cycles, escalate to human — do not loop forever on a disagreement.

### What "Escalate to Human" Means

When the circuit breaker triggers:
1. Stop all loops.
2. Produce a structured summary:
   - What was attempted
   - What findings remain unresolved
   - Why they persist (agent's best assessment)
   - Recommended human action
3. Do not attempt creative workarounds to avoid escalation.

### Metrics (Track If Tooling Supports)

Per loop run:
- Number of iterations before exit
- Findings by severity per iteration
- Number of findings that regressed (fixed then reappeared)
- Time per iteration
- Circuit breaker activations

These metrics help tune the loop — if you're consistently hitting 3 iterations, either the review checklist is too strict or the implementer instructions need work.

---

## Quick Reference: The Full Pipeline

```
1. TASK SPEC arrives
       │
       ▼
2. CODE CHANGE LOOP
   ├── You: implement
   ├── specialist-review → Claude reviews (max 3 cycles)
   ├── You: remediate P0/P1
   ├── File issues for P2/P3
   └── Exit with clean code
       │
       ▼
3. TEST WRITING LOOP
   ├── Claude: audit gaps (TEST-AUDIT.md)
   ├── Human: scope approval (P0/P1 auto-approved)
   ├── You: write tests (TESTING.md)
   ├── You: verify tests pass locally
   ├── test-review-request → Claude reviews (max 3 cycles)
   ├── You: remediate P0/P1
   ├── Claude: gap check (re-audit)
   ├── File issues for P2/P3
   └── Exit with tested code
       │
       ▼
4. ISSUE FILING
   └── P2/P3 findings → tracked issues
       │
       ▼
5. PR READY FOR HUMAN REVIEW
```
