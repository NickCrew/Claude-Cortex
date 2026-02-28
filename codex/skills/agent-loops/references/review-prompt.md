You are performing a multi-perspective specialist code review. Output the COMPLETE review as a single markdown document to stdout.

## CONSTRAINTS

1. **No tools.** Do not use Read, Write, Bash, or any other tools. Output the review directly.
2. **Fresh perspective.** When switching perspectives, mentally reset. Each perspective is independent.

## PERSPECTIVE CATALOG

{{PERSPECTIVE_CATALOG}}

## PROCEDURE

### Phase 1: Triage (determine perspectives)

Analyze the diff below to determine which 3-5 perspectives are most relevant. Consider:
- File types and extensions in the diff
- Content signals (auth code, DB queries, UI components, etc.)
- Always include Correctness and Maintainability

Output a numbered list of selected perspectives with a one-line justification for each.

### Phase 2: Sequential specialist review

For EACH selected perspective, in order:

1. **Announce the perspective**: write a heading like `## [Perspective Name] Review`
2. **Review the diff** through this lens using the focus areas and trigger signals from the catalog above. For each finding:
   - State the file and line range
   - Classify severity: CRITICAL | IMPORTANT | MINOR | NIT
   - Describe the issue
   - Suggest a fix or improvement
3. If no issues found for this perspective, state "No issues found" and move on.

### Phase 3: Synthesis

After all perspectives are complete, write a synthesis section with:
- **Summary**: 2-3 sentence overall assessment
- **Findings by Severity**: Critical, Important, Minor, Nits (bulleted lists or "None")
- **Cross-Cutting Concerns**: Draw explicit connections between findings from different perspectives. Name the perspectives being linked and explain causal or reinforcing relationships.
- **Risk Interactions**: Identify where findings from separate perspectives combine to create a larger risk than either alone. State the compounding effect.
- **Verdict**: One of APPROVE, APPROVE WITH CHANGES, or REQUEST CHANGES

## PRIOR REVIEW FINDINGS

The following is the output from the previous review cycle. Use it to:
- Verify that cited findings have been addressed in the current diff
- Check for regressions introduced by remediation
- Maintain continuity — do not re-report findings that were already fixed

{{PRIOR_REVIEW}}

## DIFF TO REVIEW

```diff
{{DIFF_CONTENT}}
```
