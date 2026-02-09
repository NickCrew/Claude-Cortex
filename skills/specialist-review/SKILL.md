---
name: specialist-review
description: Multi-perspective specialist code review without sub-agents. This skill should be used when an agent needs a thorough, multi-angle review of code changes (diffs). Instead of spawning sub-agents (which risk hallucination from shallow context), a single Claude instance sequentially adopts different specialist perspectives, loading relevant skills just-in-time for each. Results are saved to a file for the caller to consume.
---

# Specialist Review

Perform a multi-perspective code review from a single Claude context. Adopt specialist
perspectives sequentially — security, performance, architecture, etc. — loading domain
skills just-in-time for each perspective to keep context fresh and grounded.

## When to Use

- After completing a feature or significant code change, before merge
- When a calling agent needs a thorough review of a diff
- When multiple review angles are needed but sub-agent hallucination is a concern
- As a replacement for `requesting-code-review` when sub-agents are not desired

## Key Principles

1. **No sub-agents.** A single Claude instance performs the entire review. This avoids
   hallucination from sub-agents that lack sufficient context.
2. **JIT skill loading.** Identify relevant skills for each perspective but load them
   only when beginning that perspective's review. This ensures fresh, focused context.
3. **Perspective isolation.** Each perspective is reviewed independently. Findings from
   one perspective do not bias the next.
4. **File-based output.** The complete review is written to a file so calling agents
   or humans can consume it asynchronously.

## Invocation

### Option A: Shell script (for calling agents)

The bundled script handles diff generation, prompt construction, and Claude CLI invocation.

```bash
# Review current changes vs last commit
skills/specialist-review/scripts/specialist-review.sh --git

# Review changes since a specific ref
skills/specialist-review/scripts/specialist-review.sh --git origin/main

# Review a diff file
skills/specialist-review/scripts/specialist-review.sh /path/to/changes.diff

# Pipe in a diff
git diff HEAD~5..HEAD | skills/specialist-review/scripts/specialist-review.sh -

# Custom output directory
skills/specialist-review/scripts/specialist-review.sh --git HEAD~1 ./my-reviews
```

The script prints the output file path to stdout on success.

### Option B: Direct invocation (when already inside Claude)

When already operating as the reviewing Claude instance (e.g., invoked by the script
or manually by a user), follow the procedure below directly.

## Review Procedure

### Phase 1: Triage

Read the perspective catalog to determine applicable review angles:

```
cat skills/specialist-review/references/perspective-catalog.md
```

Analyze the diff to select 3-5 perspectives. Selection criteria:

1. **Always include**: Correctness, Maintainability
2. **Match by file type**: `.py` → Python performance/testing; `.tsx`/`.jsx` → React
   performance, accessibility, UX; `.tf` → Infrastructure; etc.
3. **Match by content signals**: Auth code → Security; DB queries → Performance +
   Architecture; API endpoints → API Contract + Security; etc.
4. **Cap at 5**: If more seem relevant, prioritize by change volume and risk.

Output a numbered list of selected perspectives with one-line justifications.

### Phase 2: Sequential specialist reviews

For each selected perspective, in order:

1. **Announce**: Start a `## [Perspective] Review` section
2. **Load skills**: Read the SKILL.md files listed in the perspective catalog for this
   perspective. Read them NOW — not before, not after. This is the JIT loading step.
   ```
   cat skills/{skill-name}/SKILL.md
   ```
3. **Review**: Examine the diff through this perspective's lens. For each finding:
   - **Location**: File path and line range
   - **Severity**: `CRITICAL` | `IMPORTANT` | `MINOR` | `NIT`
   - **Issue**: What is wrong or concerning
   - **Suggestion**: How to fix or improve
4. **No findings?** State "No issues found from this perspective" and proceed.

### Phase 3: Synthesis

After completing all perspective reviews, write a synthesis:

```markdown
## Synthesis

### Summary
[2-3 sentence overall assessment of the changes]

### Findings by Severity

#### Critical
[Bulleted list, or "None"]

#### Important
[Bulleted list, or "None"]

#### Minor
[Bulleted list, or "None"]

#### Nits
[Bulleted list, or "None"]

### Cross-Cutting Concerns
[Issues that surfaced across multiple perspectives, indicating systemic patterns.
Draw explicit connections between findings from different perspectives. For example:
a correctness issue in input parsing may also be a security vulnerability; a
performance concern in a hot path may trace back to an architectural coupling;
a maintainability problem may explain why test coverage is weak in that area.
Name the perspectives being linked and explain the causal or reinforcing relationship.]

### Risk Interactions
[Identify cases where findings from separate perspectives combine to create a
larger risk than either finding alone. For example: a missing auth check (Security)
on a high-throughput endpoint (Performance) creates an amplified attack surface;
or a complex abstraction (Maintainability) hiding a race condition (Correctness)
makes the bug harder to catch in review. State the compounding effect.]

### Verdict
One of:
- APPROVE — No critical or important issues found
- APPROVE WITH CHANGES — Important issues identified; address before merge
- REQUEST CHANGES — Critical issues that must be resolved
```

### Phase 4: Save results

Write the complete review (phases 1-3) to the designated output file using the Write
tool. Default location: `.beads/reviews/review-YYYYMMDD-HHMMSS.md`

## Output Format

The review file follows this structure:

```markdown
# Specialist Review — YYYY-MM-DD

## Triage
[Selected perspectives with justifications]

## Correctness Review
[Findings...]

## Security Review
[Findings...]

## [Other Perspective] Review
[Findings...]

## Synthesis
[Summary, severity breakdown, cross-cutting concerns, verdict]
```

## Anti-Patterns

- **Loading all skills upfront** — Wastes context, causes cross-contamination between
  perspectives. Load per-perspective only.
- **Using sub-agents** — The entire point of this skill is single-context review.
  Sub-agents lose context and hallucinate.
- **Skipping the catalog** — The perspective catalog maps perspectives to skills.
  Without it, skill loading is guesswork.
- **Reviewing without reading the diff** — Every finding must reference specific
  file paths and line ranges from the actual diff.
- **Rubber-stamping** — If genuine issues exist, report them. The review has no value
  if it only says "looks good."
