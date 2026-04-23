---
name: multi-specialist-review
description: User-triggered multi-agent code review. Spawns 3-5 parallel specialist sub-agents that read actual source files, runs mechanical citation verification, and synthesizes a single review artifact. Use for PR-level changes, multi-commit ranges, or security-sensitive work where single-turn review is insufficient.
keywords:
  - multi-specialist review
  - team review
  - parallel code review
  - specialist review
  - PR review
  - security review
  - citation verification
---

# Multi-Specialist Review

Team-based code review that spawns 3-5 parallel specialist sub-agents to examine
a diff through different perspectives (correctness, security, performance,
architecture, etc.), mechanically verifies every finding against the actual
source files, and synthesizes a single prioritized review artifact.

## When to Use

This skill is **user-triggered**. It is not part of routine agent workflows — the
cost and authority profile warrants explicit user invocation. Use when:

- PR-level changes (5+ modified files)
- Multi-commit ranges (`main..feature-branch`) rather than atomic commits
- Security-sensitive paths (auth, crypto, payments, input validation)
- Single-turn `specialist-review` flagged quality concerns that need deeper scrutiny

For atomic-commit review, use the baseline `specialist-review.sh` from the
`agent-loops` skill instead — it's 4-6x cheaper and sufficient for small diffs.

## Prerequisites — Claude Code Only

> **This skill requires the Claude Code team API** (`TeamCreate`, `Agent`,
> `TaskCreate`, `SendMessage`). It cannot be invoked from Codex or Gemini
> sessions, or from external shells. The parallel sub-agent orchestration and
> cross-agent coordination depend on primitives only Claude Code provides.

## Cost

Approximately **$2-3 per review** vs ~$2.00 for single-turn `specialist-review`.
The premium buys multi-perspective coverage, grounded findings (sub-agents read
source files, not just diffs), and mechanical citation verification.

## Orchestration Procedure

Follow these phases exactly. You are the team lead — do not delegate orchestration.

### Phase 0 — Triage (deterministic, no API cost)

Generate the diff you want reviewed, then select perspectives:

```bash
# Generate the diff
git diff main..HEAD -- src/ > /tmp/review-diff.patch

# Select perspectives (3-5 from the catalog based on file types and content signals)
python3 skills/multi-specialist-review/scripts/triage_perspectives.py /tmp/review-diff.patch
```

This outputs JSON with `perspectives`, `display_names`, `focus_areas`, and
`changed_files`. Save the output — you'll use it to parameterize each specialist.

### Phase 1 — Create team and spawn specialists

1. Create the team:
   ```
   TeamCreate(team_name="review-YYYYMMDD-HHMMSS")
   ```

2. Create one task per perspective:
   ```
   TaskCreate(subject="Review: Correctness", description="Review changed files through Correctness lens")
   ```

3. Spawn all specialists **in a single message** for parallel execution. For each
   perspective from the triage output, use the specialist prompt template:

   ```
   Agent(
     name="specialist-{perspective}",
     subagent_type="code-reviewer",
     model="sonnet",
     team_name="review-YYYYMMDD-HHMMSS",
     prompt=<specialist-prompt-template.md with {{PERSPECTIVE}}, {{FOCUS_AREAS}},
             {{CHANGED_FILES}}, {{DIFF_CONTENT}} filled in>
   )
   ```

   The template is at `skills/multi-specialist-review/references/specialist-prompt-template.md`.
   Each specialist:
   - Reads actual source files via Read/Grep/Glob (not just inlined diffs)
   - Outputs structured JSON with grounded, verifiable findings
   - Writes output to `.agents/reviews/specialist-{perspective}-{timestamp}.json`

4. Assign each task to its corresponding specialist via TaskUpdate.

5. Wait for all specialists to report completion (automatic via team notifications).

### Phase 2 — Citation verification (deterministic, no API cost)

Run the citation verifier on all specialist output files:

```bash
python3 skills/multi-specialist-review/scripts/verify_citations.py \
  .agents/reviews/specialist-*.json > .agents/reviews/verified-findings.json
```

This mechanically validates every finding:
- File exists on disk
- Line range is within file length
- Quoted code actually appears near the cited lines (±5 line window, whitespace-normalized)

Findings that fail verification are stripped with documented reasons.

### Phase 3 — Synthesis (team lead, no extra agent)

Read the verified findings JSON and
`skills/multi-specialist-review/references/synthesis-prompt.md`.
Follow the synthesis instructions to:

1. Deduplicate findings that flag the same file+line range from multiple perspectives
2. Merge duplicates using the highest severity
3. Annotate multi-perspective findings as "(multi-perspective)" in the title
4. Renumber all findings sequentially (P0-001, P0-002, P1-001, etc.)
5. Produce the final markdown matching the review output contract

Write the final review to `.agents/reviews/review-{timestamp}.md`.

### Phase 4 — Validate and clean up

```bash
# Validate the final output (contract validator lives in agent-loops as shared infra)
python3 skills/agent-loops/scripts/validate-review-contract.py code-review \
  .agents/reviews/review-{timestamp}.md
```

Then shut down all teammates and delete the team:
```
SendMessage(to="*", message={type: "shutdown_request"})
# Wait for shutdown confirmations, then:
TeamDelete()
```

The output file path is the review artifact — return its path to the user.

## Specialist Prompt Template

Located at `skills/multi-specialist-review/references/specialist-prompt-template.md`.
A single parameterized template used for all perspectives. Fill these placeholders
before passing to each specialist:

| Placeholder | Source |
|-------------|--------|
| `{{PERSPECTIVE}}` | Display name from triage output (e.g., "Security") |
| `{{FOCUS_AREAS}}` | Focus description from triage output |
| `{{CHANGED_FILES}}` | Bullet list of changed file paths |
| `{{DIFF_CONTENT}}` | The unified diff |

## Bundled Assets

**Scripts:**
- `scripts/triage_perspectives.py` — Deterministic perspective selection (Phase 0)
- `scripts/verify_citations.py` — Mechanical citation verification (Phase 2)

**References:**
- `references/specialist-prompt-template.md` — Parameterized prompt for each specialist
- `references/synthesis-prompt.md` — Instructions for Phase 3 synthesis

**External dependency:**
- `skills/agent-loops/scripts/validate-review-contract.py` — Shared review contract validator
  used by both this skill and the single-turn `specialist-review.sh` flow. Lives in
  `agent-loops` because it's baseline review infrastructure used across multiple flows.

## Relationship to `agent-loops`

This skill was extracted from `agent-loops` when we recognized that team-based
review has a different authority profile than routine per-commit review:

- **`agent-loops` single-turn review** (via `specialist-review.sh`) — autonomous,
  per-atomic-commit, cross-model independence via provider rotation.
  Runs continuously during implementation work.
- **`multi-specialist-review` (this skill)** — user-triggered, PR-level or
  security-sensitive, within-model multi-perspective diversity, grounded findings
  via sub-agent source reading.

Implementer agents using `agent-loops` will flag in their handoff when a change
warrants team review, but **they do not invoke this skill themselves**. The user
decides and triggers it.

## Anti-Patterns

- **Spawning specialists sequentially** — Launch all in a single message block for parallel execution.
- **Skipping citation verification** — Always run `verify_citations.py`. Specialists hallucinate file references.
- **Adding synthesis as another agent** — The team lead does synthesis in-context. No extra spawn needed.
- **Using this for small diffs** — Single-turn `specialist-review.sh` is 4-6x cheaper and sufficient for atomic commits.
- **Reviewing your own code** — The team lead must not be the implementer.
- **Invoking autonomously from an agent workflow** — This skill is user-triggered. Agents should signal in their handoff, not execute.
