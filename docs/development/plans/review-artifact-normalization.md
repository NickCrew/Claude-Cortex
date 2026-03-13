# Review Artifact Normalization

## Goal

Recover provider outputs that are semantically valid but fail the review or test-audit
contract because of small formatting drift.

## Observed Failure Shapes

- preamble noise before the first heading, for example provider status text or MCP notes
- the contract heading glued to that preamble on the same line
- near-miss section aliases such as `### Findings` in a test-audit artifact where the
  contract expects `### Prioritized Gaps`

## Normalization Rules

Normalization is intentionally narrow:

1. Strip all content before the first canonical contract heading:
   - `## Code Review:`
   - `## Test Gap Report:`
2. Preserve the rest of the document verbatim except for trailing whitespace cleanup.
3. Rewrite known section aliases only when the canonical section is absent:
   - code review: `### Issues` -> `### Findings`
   - test audit: `### Findings` -> `### Prioritized Gaps`
4. Never invent findings, counts, verdicts, or evidence.
5. If normalization still does not satisfy the validator, keep the artifact invalid.

## Workflow Contract

- Validate raw provider output first.
- If raw output fails, run normalization into a temporary candidate.
- Accept the normalized candidate only if it passes validation.
- When normalized output is accepted, preserve the original provider output as a
  `.raw.md` artifact for debugging.
- If normalization itself errors, treat that as a recoverable failure and continue
  through the normal invalid-artifact path.
- When normalized output still fails, preserve the original provider output as an
  `.invalid.md` artifact.

## Non-Goals

- semantic rewriting
- repairing missing summary counts
- guessing verdicts
- coercing arbitrary headings into compliance
