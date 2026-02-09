You are performing a test coverage audit. Follow these instructions exactly.

## CRITICAL CONSTRAINTS

1. **Load the test-review skill first.** Read it before doing anything else:

```
cat skills/test-review/SKILL.md
```

2. **Follow the skill pipeline exactly.** The test-review skill defines a three-phase pipeline. Execute all three phases in order.

3. **Write the report to disk.** The report MUST be saved to a file using the Write tool.

## PROCEDURE

### Phase 1: Load the Standards

As specified by the test-review skill, read the testing standards:

```
cat skills/test-review/references/testing-standards.md
```

Internalize the anti-patterns, required test categories, and quality criteria before reading any test code.

### Phase 2: Discovery (Haiku Agent)

As specified by the test-review skill, spawn a Haiku sub-agent (using the Task tool with `model: haiku` and `subagent_type: Explore`) to perform the mechanical discovery work.

The agent should:
1. Read the audit workflow: `skills/test-review/references/audit-workflow.md`
2. Execute **Step 1: Map the Public Contract** for the module at: `{{MODULE_PATH}}`
3. Execute **Step 2: Map Existing Test Coverage** using test files at: `{{TEST_PATH}}`
4. Return the structured inventory (behavior list with coverage status markers)

Do NOT ask the Haiku agent to analyze, prioritize, or judge. Its job is factual inventory only.

### Phase 3: Analysis and Report

Using the Haiku agent's inventory, perform the deeper analysis:

1. **Adversarial analysis** (Step 3 of audit-workflow.md) — probe input boundaries, error handling, state, integration seams using the questions defined in the workflow
2. **Produce the gap report** (Step 4 of audit-workflow.md) — assign P0/P1/P2 priorities using the criteria in audit-workflow.md, cite testing-standards.md rules

### Phase 4: Save

Write the COMPLETE gap report to this file:
```
{{OUTPUT_FILE}}
```

Use the Write tool to save the report. The file must contain the full gap report in the format defined by audit-workflow.md. After writing, confirm by stating the output file path.

## AUDIT TARGET

- **Module path:** `{{MODULE_PATH}}`
- **Test path:** `{{TEST_PATH}}`
- **Mode:** {{MODE}}
