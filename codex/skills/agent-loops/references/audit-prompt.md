You are performing a test coverage audit. All source code, test code, and reference standards are provided below. Do NOT read any files — everything you need is in this prompt.

Your output MUST follow the exact markdown contract in "REQUIRED OUTPUT FORMAT". Do not invent alternative section names.

Output the COMPLETE report as a single markdown document to stdout.

## CONSTRAINTS

1. **No tools.** Do not use Read, Write, Bash, or any other tools. Output the report directly.
2. **Do NOT spawn sub-agents.**
3. **Stay focused.** Only audit the provided module and tests.
4. **Use only these coverage labels:** `Covered`, `Shallow`, `Missing`.
5. **Use only these severities for gaps:** `P0`, `P1`, `P2`.
6. **Do not output analysis notes outside the required format.**

## TESTING STANDARDS

{{TESTING_STANDARDS}}

## AUDIT WORKFLOW

{{AUDIT_WORKFLOW}}

## SOURCE CODE

**Module:** `{{MODULE_PATH}}`

{{SOURCE_CONTENT}}

## TEST CODE

**Tests:** `{{TEST_PATH}}`

{{TEST_CONTENT}}

## YOUR TASK

1. **Map the public contract** from the source code above — list every public function/method, its error conditions, edge cases, state transitions, and integration points.

2. **Map existing test coverage** from the test code above — mark each behavior as:
   - **Covered** — a test exercises it with meaningful assertions
   - **Shallow** — a test touches it but assertions are weak (mirror test, trivial assert, no edge case)
   - **Missing** — no test exercises it

3. **Analyze and prioritize** each Missing or Shallow behavior:
   - P0: Security flaw or silent incorrect behavior if untested
   - P1: Reliability risk, missing error handling, edge cases
   - P2: Completeness improvement, nice-to-have coverage

4. **Output the report** directly to stdout using the exact format below.

## REQUIRED OUTPUT FORMAT

```markdown
## Test Gap Report: [module path or module name]

**Module:** `[module path]`
**Tests:** `[test path or "(none)"]`
**Mode:** [full|quick]

### Behavior Inventory

| Behavior | Coverage | Evidence |
|----------|----------|----------|
| [behavior description] | Covered / Shallow / Missing | [test name, file, or reason] |

### Prioritized Gaps

#### P0-001: [title]
**Behavior:** [behavior description]
**Status:** Missing / Shallow
**Why it matters:** [risk]
**Suggested test approach:** [how to test it]

#### P1-001: [title]
**Behavior:** [behavior description]
**Status:** Missing / Shallow
**Why it matters:** [risk]
**Suggested test approach:** [how to test it]

#### P2-001: [title]
**Behavior:** [behavior description]
**Status:** Missing / Shallow
**Why it matters:** [risk]
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
- Include every public behavior in `### Behavior Inventory`
- If there are no gaps, still include `### Prioritized Gaps`, then write `_No prioritized gaps._`
- Number gaps separately within each severity (`P1-001`, `P1-002`, etc.)
- A shallow test must still appear in `### Prioritized Gaps`
- Do not include any sections other than `## Test Gap Report`, `### Behavior Inventory`, `### Prioritized Gaps`, and `### Summary`
- Do not include overall prose introductions before the required sections

**Mode:** {{MODE}}
