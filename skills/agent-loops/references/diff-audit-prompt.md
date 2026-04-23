You are performing a per-commit test coverage check on a DIFF. All relevant content (the diff, touched source files, existing tests, testing standards) is provided below. Do NOT read any files — everything you need is in this prompt.

Your output MUST follow the exact markdown contract in "REQUIRED OUTPUT FORMAT". Do not invent alternative section names.

Output the COMPLETE report as a single markdown document to stdout.
The very first non-whitespace characters of your output must be `## Test Gap Report:`.

## SCOPE: DIFF-INTRODUCED BEHAVIORS ONLY

This is a **per-commit test completeness check**, not a module audit. You are
assessing whether the diff's changes are adequately tested — NOT whether the
containing files are fully tested.

**In scope (report gaps for these):**
- New public functions, methods, or classes introduced by the diff
- Modified behaviors in existing functions: new branches, new error paths,
  new return values, new side effects, new edge cases the diff introduces
- Newly-added error types or error conditions
- New integration points or contract changes

**Out of scope (do NOT report gaps for these):**
- Pre-existing functions in touched files that the diff did not modify
- Untested code in neighboring files not in the diff
- Refactors that preserve behavior (no semantic change → no new tests needed)
- Renames, formatting, comment-only changes, dead-code removal
- Documentation or configuration changes

If a function existed before and the diff did not change its behavior, it is
**out of scope** regardless of whether it has tests. Gaps in pre-existing
untested code belong in a dedicated module audit via the `test-review` skill,
not here.

If the diff is entirely non-behavioral (formatting, renames, comments), your
report should have an empty `### Prioritized Gaps` section with `_No
behavioral changes in diff._` and a Behavior Inventory reflecting that.

## CONSTRAINTS

1. **No tools.** Do not use Read, Write, Bash, or any other tools. Output the report directly.
2. **Do NOT spawn sub-agents.**
3. **Stay focused.** Only audit behaviors from the diff.
4. **Use only these coverage labels:** `Covered`, `Shallow`, `Missing`.
5. **Use only these severities for gaps:** `P0`, `P1`, `P2`.
6. **Do not output analysis notes outside the required format.**
7. **Do not prepend status text.** Do not emit MCP notes, tool status, fences, or any text before the first heading.

## TESTING STANDARDS

{{TESTING_STANDARDS}}

## THE DIFF

This is the change under audit. **Every gap you report must trace to a behavior introduced or modified by this diff.** If a behavior is visible in the source below but not in this diff, it is out of scope.

```diff
{{DIFF_CONTENT}}
```

## SOURCE FILES (CURRENT STATE)

The files touched by the diff, at their current (post-diff) state. Use these
for context on how diff-introduced behaviors interact with surrounding code,
but remember: **only behaviors from "THE DIFF" are in scope**.

{{SOURCE_CONTENT}}

## EXISTING TESTS

{{TEST_CONTENT}}

## YOUR TASK

1. **Identify diff-introduced behaviors.** Read "THE DIFF" carefully. List
   every new or modified public behavior. If the diff contains only
   non-behavioral changes (formatting, renames, comments), note that and
   return an empty gap report.

2. **Map each diff-introduced behavior to its test coverage.** Use the tests
   above. Mark each as:
   - **Covered** — a test exercises this behavior with meaningful assertions
   - **Shallow** — a test touches it but weakly (mirror test, trivial assert, happy-path-only, missing error case)
   - **Missing** — no test exercises this behavior

3. **Report gaps for Shallow and Missing behaviors only.**
   - P0: Security flaw or silent incorrect behavior if untested
   - P1: Reliability risk, missing error handling, meaningful edge case introduced by the diff
   - P2: Completeness improvement for this diff's changes

4. **Do not report gaps for pre-existing untested code.** Those are out of
   scope for this audit mode. A module audit (via the `test-review` skill) is
   the right tool for that.

5. **Output** using the format below.

## REQUIRED OUTPUT FORMAT

```markdown
## Test Gap Report: [module path or module name]

**Module:** `[module path]`
**Tests:** `[test path or "(none)"]`
**Mode:** diff

### Behavior Inventory

Behaviors introduced or modified by this diff:

| Behavior | Coverage | Evidence |
|----------|----------|----------|
| [diff-introduced behavior] | Covered / Shallow / Missing | [test name, file, or reason] |

### Prioritized Gaps

#### P0-001: [title]
**Behavior:** [diff-introduced behavior description]
**Status:** Missing / Shallow
**Why it matters:** [risk specific to this change]
**Suggested test approach:** [how to test it]

#### P1-001: [title]
**Behavior:** [diff-introduced behavior description]
**Status:** Missing / Shallow
**Why it matters:** [risk specific to this change]
**Suggested test approach:** [how to test it]

#### P2-001: [title]
**Behavior:** [diff-introduced behavior description]
**Status:** Missing / Shallow
**Why it matters:** [risk specific to this change]
**Suggested test approach:** [how to test it]

### Summary
- Covered: [count]
- Shallow: [count]
- Missing: [count]
- P0: [count]
- P1: [count]
- P2: [count]
```

Additional rules:
- The Behavior Inventory lists **only diff-introduced behaviors**, not every public behavior in the touched files
- If the diff introduced no behaviors (pure formatting/renames), the inventory may have one row noting that
- If there are no gaps, still include `### Prioritized Gaps`, then write `_No prioritized gaps._`
- Number gaps separately within each severity (`P1-001`, `P1-002`, etc.)
- A shallow test must still appear in `### Prioritized Gaps`
- Do not include any sections other than `## Test Gap Report`, `### Behavior Inventory`, `### Prioritized Gaps`, and `### Summary`
- Do not include overall prose introductions before the required sections
- Copy the section headings exactly as written above

**Mode:** diff
