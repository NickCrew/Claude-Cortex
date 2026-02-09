You are performing a test coverage audit. Follow these instructions exactly.

## CRITICAL CONSTRAINTS

1. **Do NOT spawn sub-agents.** You are running in a CLI invocation with a fresh context. Do all work directly — reading files, mapping behaviors, analyzing gaps. Sub-agents add latency and indirection you don't need here.

2. **Write the report to disk.** The report MUST be saved to a file using the Write tool.

3. **Stay focused on the target module.** Do not audit the entire codebase. Only audit the specified module and its tests.

## PROCEDURE

### Step 1: Load the Standards

Read the testing standards so you know what good tests look like:

```
cat skills/test-review/references/testing-standards.md
```

Internalize the anti-patterns, required test categories, and quality criteria before reading any test code.

### Step 2: Load the Audit Workflow

Read the audit workflow so you know the gap report format and priority criteria:

```
cat skills/test-review/references/audit-workflow.md
```

### Step 3: Map the Public Contract

Read the source files at `{{MODULE_PATH}}` and list every public behavior:
- Public functions/methods with their signatures
- Error conditions and edge cases
- State transitions and side effects
- Integration points (external calls, I/O)

### Step 4: Map Existing Test Coverage

Read the test files at `{{TEST_PATH}}` and mark each behavior from Step 3 as:
- **Covered** — a test exercises this behavior with meaningful assertions
- **Shallow** — a test touches this code path but assertions are weak (mirror test, trivial assert, no edge case)
- **Missing** — no test exercises this behavior

### Step 5: Analyze and Prioritize

For each Missing or Shallow behavior:
1. Assess risk: what happens if this behavior breaks silently?
2. Assign priority per audit-workflow.md criteria (P0/P1/P2)
3. For Shallow tests, note the specific quality issue (mirror, flaky, trivial, etc.)

### Step 6: Write the Report

Write the COMPLETE gap report to this file:
```
{{OUTPUT_FILE}}
```

Use the Write tool to save the report. The report must include:
- Behavior inventory (all public behaviors with coverage status)
- Prioritized gap list (P0 first, then P1, then P2)
- For each gap: what's missing, why it matters, suggested test approach
- For shallow tests: what's wrong and how to fix it

After writing, confirm by stating the output file path.

## AUDIT TARGET

- **Module path:** `{{MODULE_PATH}}`
- **Test path:** `{{TEST_PATH}}`
- **Mode:** {{MODE}}
