# Codex Review Output Format

## Overview

After running `codex --full-auto c`, the review output is written as markdown to `.agent/reviews/review-<TIMESTAMP>.md`.

This document specifies the format so you can parse findings programmatically or manually.

---

## Top-Level Structure

```markdown
# Code Review: [Brief description of what was reviewed]

**Files reviewed:** [comma-separated list of file paths]
**Iteration:** N of 3

### Findings

[Findings grouped by severity: P0, P1, P2, P3]

### Summary

[Statistics and verdict]
```

---

## Findings Section

### P0 Findings (Security/Correctness Critical)

These MUST be fixed before exiting the review loop.

```markdown
#### P0-001: [Title of the finding]

**File:** `path/to/file.rs:45-52`
**Issue:** [Description of what is wrong]
**Impact:** [What happens if not fixed — security risk, data loss, crash, etc.]
**Suggested fix:** [Specific, actionable guidance on how to fix it]
```

### P1 Findings (Reliability/Edge Cases)

These MUST be fixed before exiting the review loop.

```markdown
#### P1-001: [Title of the finding]

**File:** `path/to/module.ts:120`
**Issue:** [Description of what is wrong]
**Impact:** [What happens if not fixed — unhandled errors, resource leaks, etc.]
**Suggested fix:** [Specific guidance]
```

### P2 Findings (Code Quality)

Can be fixed now or deferred to backlog.

```markdown
#### P2-001: [Title of the finding]

**File:** `path/to/file.py:88-95`
**Issue:** [What could be improved]
**Recommendation:** [How to improve it]
```

### P3 Findings (Style/Preferences)

Can be fixed now or deferred. Usually low priority.

```markdown
#### P3-001: [Title of the finding]

**File:** `path/to/file.go:50`
**Issue:** [Style or preference issue]
**Recommendation:** [Suggested change]
```

---

## Summary Section

```markdown
### Summary

- **P0:** N findings (MUST fix)
- **P1:** N findings (MUST fix)
- **P2:** N findings (optional)
- **P3:** N findings (optional)

**Verdict:** APPROVE / REQUEST CHANGES / BLOCKED
```

### Verdict Meanings

| Verdict | Meaning |
|---------|---------|
| **APPROVE** | No P0/P1 findings. All findings are P2/P3 or none at all. Safe to proceed. |
| **REQUEST CHANGES** | Has P0 or P1 findings. Must be fixed before approval. |
| **BLOCKED** | Critical issues; unusual. Indicates major problems that may require escalation. |

---

## Complete Example

```markdown
# Code Review: Auth Module - Token Refresh

**Files reviewed:** `src/auth.ts`, `src/auth.test.ts`
**Iteration:** 2 of 3

### Findings

#### P0-001: Race condition in token refresh

**File:** `src/auth.ts:45-52`
**Issue:** Multiple concurrent calls to `refreshToken()` can issue multiple refresh requests simultaneously, leading to issued but unused tokens. The check for "in-flight refresh" is not atomic.
**Impact:** Token exhaustion. If tokens have a per-user limit, attackers could exhaust the token quota.
**Suggested fix:** Use a promise-based semaphore or mutex to ensure only one refresh request is in flight at a time. See the `p-queue` or native `AbortController` pattern for inspiration.

#### P1-001: Unhandled promise rejection

**File:** `src/auth.ts:78`
**Issue:** `refreshToken()` returns a promise that can reject (network error, 401, etc.), but callers may not always `catch()` the rejection.
**Impact:** Unhandled rejections cause app crashes. Users lose their session without feedback.
**Suggested fix:** Either (1) ensure all callers have `.catch()`, or (2) wrap the promise chain with an error boundary in the auth module itself.

#### P2-001: Missing JSDoc for `setToken()`

**File:** `src/auth.ts:30`
**Issue:** Public function `setToken()` has no documentation.
**Recommendation:** Add JSDoc explaining parameter types, side effects (e.g., updates localStorage), and return value.

### Summary

- **P0:** 1 finding (MUST fix)
- **P1:** 1 finding (MUST fix)
- **P2:** 1 finding (optional)
- **P3:** 0 findings

**Verdict:** REQUEST CHANGES
```

---

## Parsing Tips

### Count Findings by Severity

Search for headings `#### P0-`, `#### P1-`, `#### P2-`, `#### P3-` and count occurrences.

```bash
grep -c "^#### P0-" review.md  # Count P0 findings
grep -c "^#### P1-" review.md  # Count P1 findings
grep -c "^#### P2-" review.md  # Count P2 findings
grep -c "^#### P3-" review.md  # Count P3 findings
```

### Extract Verdict

Look for the line starting with `**Verdict:**` in the Summary section.

```bash
grep "^\\*\\*Verdict:\\*\\*" review.md
```

### Extract File Locations

Each finding has a `**File:**` line. Extract file paths and line ranges:

```bash
grep "^\*\*File:\*\*" review.md
# Example output:
# **File:** `src/auth.ts:45-52`
# **File:** `src/auth.ts:78`
```

### Check Iteration Count

Look for the line `**Iteration:**` near the top.

```bash
grep "^\\*\\*Iteration:\\*\\*" review.md
# Example output:
# **Iteration:** 2 of 3
```

---

## When No Findings Are Present

If the code is clean, the review still has a "Findings" section but it may be empty:

```markdown
# Code Review: Auth Module

**Files reviewed:** `src/auth.ts`
**Iteration:** 1 of 3

### Findings

(No findings.)

### Summary

- **P0:** 0 findings
- **P1:** 0 findings
- **P2:** 0 findings
- **P3:** 0 findings

**Verdict:** APPROVE
```

---

## Integration with Remediation Loop

**After Reading Review:**

1. Count P0 + P1 findings
2. If count > 0:
   - Fix each finding per suggested guidance
   - Amend or update code
   - Re-run codex review (loop back to step 1)
3. If count == 0:
   - File issues for P2/P3 findings (if deferring)
   - Exit the loop

**After 3 Iterations:**

If P0/P1 findings still exist, stop remediating and escalate to user.

---

## Notes

- Review markdown files are **temporary and accumulate** in `.agent/reviews/`. Older reviews can be cleaned up after the remediation loop completes.
- Always **read the latest review file** (highest timestamp) to ensure you're acting on the current cycle's findings.
- If a finding is **disputed**, note your disagreement in the remediation and run the review again. Codex will re-evaluate.
