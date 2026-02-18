# Backlog Integration: Filing Deferred Review Findings

When codex review identifies P2-P4 findings that you choose not to fix immediately, file them as backlog issues with proper labeling and implementation plans.

---

## Issue Filing Rules

1. **One issue per finding** — Do not batch unrelated findings into a single issue
2. **Type label required** — Use `remediation` for all deferred review findings
3. **Severity label** — Use `P2` or `P3` (not P4 unless explicitly from review)
4. **Origin label** — Tag with `origin:ai-review` so findings are traceable to this review cycle
5. **Include plan** — Codex identified the problem; you provide the structured approach based on their suggestion

---

## Command Template

```bash
backlog task create "Title of the finding" \
  -d "Description of the issue" \
  -l remediation \
  -p 2 \
  --ac "Acceptance criteria from review" \
  --plan "Implementation plan based on codex suggestion"
```

### Required Parameters

- **`-l remediation`** — Type label (always `remediation` for review findings)
- **`-p 2`** or **`-p 3`** — Priority (P2 or P3 from the review)
- **`--ac "..."`** — Acceptance criteria (what makes this issue done?)
- **`--plan "..."`** — Implementation plan (how to approach the fix)

---

## Field Mapping from Review

Map codex review findings to backlog fields:

| Codex Review | Backlog Field | Notes |
|--------------|---------------|-------|
| Finding Title | `-create "Title"` | Brief, descriptive |
| Issue description | `-d "Description"` | The problem statement from codex |
| Suggested fix | `--plan "..."` | Becomes the implementation plan |
| File location | Mention in description or plan | e.g., "File: `src/auth.ts:78`" |
| P2 or P3 | `-p 2` or `-p 3` | Priority level |
| Type: Code Quality | `-l remediation` | Standard label for all review findings |

---

## Examples

### Example 1: Documentation Improvement (P2)

**Codex Finding:**
```
#### P2-001: Missing JSDoc for `setToken()`

**File:** `src/auth.ts:30`
**Issue:** Public function `setToken()` has no documentation.
**Recommendation:** Add JSDoc explaining parameter types, side effects (e.g., updates localStorage), and return value.
```

**Backlog Issue:**
```bash
backlog task create "Auth: Add JSDoc to setToken() function" \
  -d "File: \`src/auth.ts:30\`\n\nPublic function setToken() lacks documentation. This impairs developer experience and IDE support." \
  -l remediation \
  -p 2 \
  --ac "JSDoc comment added above setToken() with parameter types, side effects, and return value documented" \
  --plan "Add JSDoc comment block above the setToken() function definition. Include @param for all parameters, @returns, and @description of side effects (localStorage mutation)."
```

### Example 2: Error Handling Gap (P2)

**Codex Finding:**
```
#### P2-003: Missing error handling in callback chain

**File:** `src/handlers/webhook.ts:105-112`
**Issue:** The Promise chain in handleWebhook() has a `.then()` but no `.catch()` for network failures.
**Recommendation:** Add error boundary or `.catch()` to log and recover gracefully from network errors.
```

**Backlog Issue:**
```bash
backlog task create "Webhooks: Add error handling to handleWebhook callback" \
  -d "File: \`src/handlers/webhook.ts:105-112\`\n\nThe Promise chain lacks error handling for network failures, potentially causing unhandled rejections." \
  -l remediation \
  -p 2 \
  --ac "Promise rejection handled gracefully with error logging and fallback behavior" \
  --plan "Add .catch() to the Promise chain in handleWebhook(). Log errors to monitoring system. Implement exponential backoff or dead-letter queue for failed webhooks."
```

### Example 3: Test Coverage Gap (P2)

**Codex Finding:**
```
#### P2-005: Missing edge case test for empty list

**File:** `src/utils/processItems.test.ts`
**Issue:** Tests only cover non-empty lists. Edge case: empty list [] is untested.
**Recommendation:** Add test case for `processItems([])` to verify handling of empty input.
```

**Backlog Issue:**
```bash
backlog task create "Tests: Add edge case test for empty list in processItems()" \
  -d "File: \`src/utils/processItems.test.ts\`\n\nEdge case for empty input is untested. Current tests only cover non-empty lists." \
  -l remediation \
  -p 2 \
  --ac "New test case for processItems([]) exists and passes" \
  --plan "Add test case: describe('empty list', () => { expect(processItems([])).toEqual([...]); });. Verify correct behavior for empty input based on function contract."
```

### Example 4: Code Clarity (P3)

**Codex Finding:**
```
#### P3-002: Variable name could be clearer

**File:** `src/lib/parser.ts:67`
**Issue:** Variable `tmp` is ambiguous. Unclear what it holds (temp result? temporary state?).
**Recommendation:** Rename to something descriptive like `parsedToken` or `intermediateResult`.
```

**Backlog Issue:**
```bash
backlog task create "Code clarity: Rename ambiguous variable in parser" \
  -d "File: \`src/lib/parser.ts:67\`\n\nVariable \`tmp\` is ambiguous and reduces code clarity." \
  -l remediation \
  -p 3 \
  --ac "Variable renamed to something descriptive; all references updated; tests still pass" \
  --plan "Rename \`tmp\` to \`parsedToken\` (or similar based on what it contains). Update all references in the parseInput() function and any calling code."
```

---

## Labels and Conventions

### Type Label (Required)

Always use **`-l remediation`** for all findings from codex review. This distinguishes them from other issue types.

### Additional Labels (Optional)

After `-l remediation`, you can add custom labels for organization:

```bash
backlog task create "Title" \
  -l remediation \
  -p 2 \
  -l security        # Additional custom label if relevant
  -l performance     # Additional custom label if relevant
  --ac "..." \
  --plan "..."
```

### Severity Priority

- **P2** — Important for code quality or reliability; address in current or next sprint
- **P3** — Nice-to-have improvements; lower priority; backlog candidate

---

## Integration Timing

### When to File

After codex review completes:
- P0/P1 findings are fixed (loop exits)
- P2/P4 findings are ready to be deferred

File issues **before** exiting the skill workflow or **immediately after** the review loop completes.

### What to Include in the Plan

The implementation plan should include:
1. **What to change** — Specific file, function, or area
2. **How to change it** — Based on codex's suggested approach
3. **Expected outcome** — What the code should look like after
4. **Any dependencies** — E.g., "Requires updating other tests" or "Follows pattern X from module Y"

---

## Backlog CLI Examples

### List recent remediation issues

```bash
backlog task list -l remediation --plain
```

### Search for issues from this review cycle

```bash
backlog search "origin:ai-review" --plain
```

### Work an issue

```bash
backlog task 42 --plain          # Read all details
backlog task edit 42 -s "In Progress" -a @myself
backlog task edit 42 --final-summary "Issue fixed via PR #123"
backlog task edit 42 -s Done
```

---

## Notes

- **Do not file P0/P1 findings** — These are fixed during the review loop, not deferred
- **Do file P2/P3 findings** — You decide whether to fix immediately or defer
- **One issue per finding** — Keeps backlog granular and trackable
- **Use the origin label** — `origin:ai-review` makes these findings searchable and traces them back to the review workflow
- **Include a plan** — Codex identified the problem; your plan shows you understand the fix approach

See the `backlog-md` skill documentation for complete CLI reference.
