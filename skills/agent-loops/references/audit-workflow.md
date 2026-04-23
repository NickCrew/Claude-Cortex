# Test Audit Workflow

This document defines the process for discovering untested or under-tested behavior in a codebase. The output is a prioritized gap report — **not code**. Do not write test implementations until the report is reviewed and approved.

See `testing-standards.md` for test quality standards that apply when tests are eventually written.

---

## When to Run This Audit

- Before starting a new feature in an existing module
- After a significant refactor
- When preparing a module for production deployment
- On request ("audit tests for module X")
- Periodically as a codebase health check

---

## Audit Process

### Step 1: Map the Public Contract

Read the module's source code and produce a list of every **public behavior** it promises. This is NOT a list of functions — it's a list of things the module does.

Sources of contract information (check all of these):
- Public function/method signatures and their doc comments
- Type definitions and their invariants (e.g., "port must be 1-65535")
- Error types and when each variant should occur
- Trait implementations and what they promise
- Configuration options and their effects
- State transitions (if stateful)
- Concurrency guarantees (Send, Sync, thread-safe claims)
- Performance claims (timeouts, capacity limits, eviction policies)

**Format each behavior as a plain-English statement:**

```
BEHAVIORS for connect_parser:
- Parses valid CONNECT requests into (host, port) pairs
- Rejects CONNECT requests with missing port
- Rejects CONNECT requests with non-numeric port
- Rejects CONNECT requests with port outside 1-65535
- Rejects non-CONNECT HTTP methods
- Handles IPv6 addresses in bracket notation
- Handles IDN / punycode hostnames
- Preserves original Host header if present
- Returns specific error variants for each failure mode
```

### Step 2: Map Existing Test Coverage

Read every test file that covers the module. For each test, record:
- What behavior it exercises (map to Step 1 list)
- Whether it tests the happy path, edge case, or failure mode
- Whether assertions are meaningful (see testing-standards.md anti-patterns)

**Mark each behavior from Step 1:**
- ✅ **Covered** — at least one test verifies this with meaningful assertions
- ⚠️ **Shallow** — a test touches this but doesn't properly verify it (e.g., only happy path, trivial assertions, mirror testing)
- ❌ **Missing** — no test exercises this behavior

### Step 3: Adversarial Analysis

For each module, ask these questions. If you can't confidently answer "yes, a test catches that," it's a gap.

**Input boundaries:**
- What happens at zero / empty / None for every input?
- What happens at maximum values (u32::MAX, max capacity, longest valid string)?
- What happens one past maximum?
- What happens with malformed input that's almost-valid?
- What happens with unicode / special characters where strings are accepted?

**Error handling:**
- Does every `Result::Err` variant have a test that triggers it?
- Does every `Option::None` path have a test?
- If a function calls a fallible dependency, is the failure case tested?
- Are error messages/types specific enough to diagnose issues?

**State and concurrency:**
- If the module has state, is every transition tested?
- If state has limits (LRU capacity, TTL), are eviction/expiry tested?
- If shared across threads, is concurrent access tested?
- Is cleanup on drop/shutdown tested?

**Integration seams:**
- Where this module connects to another, is the contract at the boundary tested?
- If this module consumes config, are invalid/missing config values tested?
- If this module emits metrics, are metric values verified (not just "didn't panic")?

**The "subtle bug" test:**
For each critical function, imagine these mutations and ask if any test would catch them:
- Off-by-one on a comparison (`<` vs `<=`)
- Swapped arguments in a function call
- Wrong default value
- Missing `.await` on an async call (for Rust: this is a compile error, skip)
- Short-circuit evaluation hiding a bug (early return before important side effect)
- Integer overflow / underflow on arithmetic

### Step 4: Produce the Gap Report

---

## Gap Report Format

```markdown
# Test Gap Report: [Module Name]

**Audit date:** YYYY-MM-DD
**Source files audited:** [list paths]
**Test files audited:** [list paths]
**Current test count:** N tests
**Estimated coverage:** X% (if tooling available, otherwise "manual audit")

---

## Summary

[2-3 sentences: overall assessment of test health for this module]

Total behaviors identified: N
- ✅ Covered: N
- ⚠️ Shallow: N  
- ❌ Missing: N

---

## Gaps by Priority

### 🔴 P0 — Security / Correctness Critical

Tests that, if missing, could allow security vulnerabilities, data corruption,
or silent incorrect behavior in production.

| # | Behavior | Current State | Why P0 | Suggested Test |
|---|----------|---------------|--------|----------------|
| 1 | [behavior] | ❌ Missing | [what breaks] | [one-line description] |
| 2 | [behavior] | ⚠️ Shallow | [what's wrong with current test] | [what to fix] |

### 🟠 P1 — Reliability / Edge Cases

Tests for error handling, boundary conditions, and graceful degradation.
Missing these won't cause security issues but will cause operational pain.

| # | Behavior | Current State | Why P1 | Suggested Test |
|---|----------|---------------|--------|----------------|
| 1 | [behavior] | ❌ Missing | [what breaks] | [one-line description] |

### 🟡 P2 — Completeness / Confidence

Tests that round out coverage and prevent regressions during future changes.
Nice to have, lower urgency.

| # | Behavior | Current State | Why P2 | Suggested Test |
|---|----------|---------------|--------|----------------|
| 1 | [behavior] | ❌ Missing | [context] | [one-line description] |

### ✅ Well-Tested (No Action Needed)

[List behaviors that are adequately covered, briefly, so the report shows
the full picture and not just the gaps]

---

## Shallow Test Details

For each ⚠️ Shallow entry, explain what's wrong with the existing test:

### [Test name / behavior]
**Current test:** [what it does]
**Problem:** [mirror testing / happy path only / trivial assertion / over-mocked]
**Recommended fix:** [specific change needed]

---

## Notes

[Any observations about test infrastructure, missing test utilities,
or patterns that would make future testing easier]
```

---

## Priority Assignment Criteria

### 🔴 P0 — Security / Correctness Critical

Assign P0 when the untested behavior:
- Involves authentication, authorization, or access control
- Parses untrusted input (HTTP requests, TLS ClientHello, config from external sources)
- Makes a security decision (block/allow, risk scoring threshold)
- Handles sensitive data (API keys, credentials, PII in transit)
- Has correctness requirements where "wrong answer silently" is worse than "crash"
- Involves cryptographic operations or certificate validation

**Examples:**
- CONNECT parser doesn't test request smuggling patterns → P0
- Domain allowlist doesn't test bypass via case sensitivity → P0
- Risk score calculation doesn't test overflow past 100 → P0
- Auth token validation doesn't test expired tokens → P0

### 🟠 P1 — Reliability / Edge Cases

Assign P1 when the untested behavior:
- Handles a failure mode (network timeout, disk full, OOM)
- Manages resource limits (connection pools, LRU caches, rate limits)
- Involves state transitions that could get stuck or leak
- Deals with concurrency (shared state, race conditions)
- Processes boundary values (empty input, max capacity)
- Affects operational visibility (metrics, logging, health checks)

**Examples:**
- LRU cache doesn't test eviction under memory pressure → P1
- Tunnel relay doesn't test what happens when origin hangs → P1
- Metric counters don't test overflow after long uptime → P1
- Graceful shutdown doesn't test mid-tunnel disconnect → P1

### 🟡 P2 — Completeness / Confidence

Assign P2 when the untested behavior:
- Has a working happy-path test but no edge case coverage
- Is configuration-driven with reasonable defaults
- Involves display / formatting logic (not security-relevant)
- Is covered indirectly by integration tests but lacks unit verification
- Would catch regressions during refactors but isn't currently at risk

**Examples:**
- Config parser doesn't test YAML with extra unknown fields → P2
- Log formatting doesn't test very long message truncation → P2
- Metric labels don't test special character escaping → P2
- CLI help text doesn't test all flag combinations → P2

---

## What This Audit is NOT

- **Not a coverage report.** Line coverage misses semantic gaps. A line can be "covered" by a test that asserts nothing meaningful.
- **Not a test plan.** This report identifies WHAT is missing. How to implement the tests is governed by `testing-standards.md`.
- **Not busywork.** If a module is genuinely well-tested, the report should say so clearly and move on. Don't manufacture gaps to look thorough.
