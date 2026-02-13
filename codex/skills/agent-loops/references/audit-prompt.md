You are performing a test coverage audit. All source code, test code, and reference standards are provided below. Do NOT read any files — everything you need is in this prompt.

Output the COMPLETE report as a single markdown document to stdout.

## CONSTRAINTS

1. **No tools.** Do not use Read, Write, Bash, or any other tools. Output the report directly.
2. **Do NOT spawn sub-agents.**
3. **Stay focused.** Only audit the provided module and tests.

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

4. **Output the report** directly to stdout. The report must include:
- Behavior inventory table (all public behaviors with coverage status)
- Prioritized gap list (P0 first, then P1, then P2)
- For each gap: what's missing, why it matters, suggested test approach
- For shallow tests: what's wrong and how to fix it

**Mode:** {{MODE}}
