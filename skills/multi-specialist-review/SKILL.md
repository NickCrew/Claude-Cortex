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

> **This skill requires the Claude Code `Agent` tool** with the `code-reviewer`
> subagent type available. It cannot be invoked from Codex or Gemini sessions,
> or from external shells. Parallelism comes from issuing multiple `Agent`
> calls in a single assistant message — no team API is needed.

## Cost

Approximately **$2-3 per review** vs ~$2.00 for single-turn `specialist-review`.
The premium buys multi-perspective coverage, grounded findings (sub-agents read
source files, not just diffs), and mechanical citation verification.

## Orchestration Procedure

Follow these phases exactly. You are the orchestrator — do not delegate
orchestration. Each phase is run by you in-context; only Phase 1 spawns
sub-agents, and they are one-shot Agent calls that return and exit.

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

### Phase 1 — Spawn specialists as parallel one-shot Agents

Spawn **all** specialists in a **single assistant message** with one `Agent`
tool call per perspective. Issuing multiple `Agent` calls in one message runs
them concurrently — that is the parallelism mechanism. Do **not** use
`team_name=`, `TeamCreate`, or `TaskCreate`; see the anti-pattern note below
for why.

For each perspective from the triage output:

```
Agent(
  description="Specialist review: {perspective}",
  subagent_type="code-reviewer",
  model="sonnet",
  prompt=<specialist-prompt-template.md with {{PERSPECTIVE}}, {{FOCUS_AREAS}},
          {{CHANGED_FILES}}, {{DIFF_CONTENT}} filled in>
)
```

The template is at `skills/multi-specialist-review/references/specialist-prompt-template.md`.
Each specialist:
- Inherits the `code-reviewer` toolset (Read, Grep, Glob, etc.) because it
  is a one-shot Agent call, not a team spawn
- Reads actual source files via Read/Grep/Glob (not just inlined diffs)
- Returns its structured JSON object as its final assistant message

When each Agent call returns, **you** (the orchestrator) write its JSON
result to `.agents/reviews/specialist-{perspective}-{timestamp}.json`. The
verifier in Phase 2 reads these files from disk.

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

### Phase 3 — Synthesis (orchestrator, no extra agent)

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

There is no team to tear down — one-shot Agent calls return and exit on
their own. Optionally trash the per-specialist `.agents/reviews/specialist-*.json`
intermediates once the synthesized review is written; keep
`verified-findings.json` and the final markdown.

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

- **Spawning specialists via `team_name=` / `TeamCreate`** — Team-spawned
  agents do **not** inherit the `code-reviewer` toolset; they get only
  inter-agent coordination tools (`SendMessage`, `Task*`) and no
  Read/Grep/Glob/Write/Bash. The observable failure is specialists
  announcing "I'll read the files" in plain text, then idling between
  turns without ever invoking a tool. Always use one-shot `Agent()` calls
  in a single message instead — they get the full inherited toolset and
  have no idle-between-turns state.
- **Spawning specialists sequentially** — Launch all in a single message block for parallel execution.
- **Skipping citation verification** — Always run `verify_citations.py`. Specialists hallucinate file references.
- **Adding synthesis as another agent** — The orchestrator does synthesis in-context. No extra spawn needed.
- **Using this for small diffs** — Single-turn `specialist-review.sh` is 4-6x cheaper and sufficient for atomic commits.
- **Reviewing your own code** — The orchestrator must not be the implementer.
- **Invoking autonomously from an agent workflow** — This skill is user-triggered. Agents should signal in their handoff, not execute.
