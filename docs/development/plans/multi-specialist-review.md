# Multi-Specialist Parallel Review

**Status:** Implemented
**Created:** 2026-03-11
**Implemented:** 2026-04-05
**Context:** Evolved from agent-loops single-turn, provider-aware review architecture
**Approach:** Teams-based (Claude Code TeamCreate/Agent API), skipping the bash-orchestrated intermediate step

## Problem

The current `specialist-review.sh` (agent-loops) simulates multiple review perspectives in a single provider session selected by the provider-aware fallback chain. This works well for atomic commits but breaks down on larger reviews (multiple commits, PR-level, milestone-level):

- **Anchoring bias** — Later perspectives are influenced by earlier ones since they share one context
- **Hallucination risk scales with context size** — A 2000-line multi-commit diff exceeds what a single pass can reliably hold
- **No error correction** — Fabricated findings flow into the synthesis unchallenged
- **Inlined content limit** — Current approach inlines all code into the prompt; large reviews hit context limits

## Design Decisions

### Keep agent-loops for atomic commits

Agent-loops works well at the single-commit level (~$0.50/review). Small diffs are inherently grounded — the model can hold the full context without losing track. The multi-specialist approach is for larger reviews where the quality/cost tradeoff justifies it.

### Bash-level parallelism, not Claude teams or subagents

The external caller (codex/gemini) shells out to bash to call the selected reviewer CLI. This means:

- Can't use the review provider's in-process agent/team features from the caller side
- Orchestration must happen at the bash script level
- Multiple parallel provider CLI calls with `&` and `wait`
- Synthesis as a separate provider call

This keeps the **external interface identical** to agent-loops: caller passes a diff, gets back a file path.

### Specialists read real files (not inlined)

Unlike agent-loops (`--tools ""`), specialists get `--allowedTools "Read,Grep,Glob"`:

- Each specialist reads actual source files to verify findings
- Prompt explicitly forbids reporting concerns that can't be verified by reading the code
- Dramatically reduces false positives from pattern-matching against truncated diffs

### Citation verification between phases

A deterministic Python script validates every finding before synthesis:

- Extract file:line references from each specialist's output
- Verify files exist and line ranges are valid
- Verify quoted code matches actual file contents
- Strip any finding that fails verification
- Catches type 1-2 hallucinations (fabricated references, misread patterns) mechanically

### Separate synthesis pass

The synthesizer:

- Receives only verified findings from all specialists
- Cross-references findings (same issue flagged by multiple specialists = high confidence)
- Flags single-source findings as lower confidence
- Produces structured output with confidence scoring

## Architecture

```
codex/gemini shells out to:
┌──────────────────────────────────────────────────────────┐
│  multi-specialist-review.sh --git main..feature-branch   │
│                                                          │
│  Phase 1: Parallel specialist calls                      │
│  ┌─────────────────┐ ┌──────────────┐ ┌────────────────┐│
│  │claude --print    │ │claude --print│ │claude --print  ││
│  │--allowedTools    │ │--allowedTools│ │--allowedTools  ││
│  │"Read,Grep,Glob" │ │"Read,Grep,.."│ │"Read,Grep,.." ││
│  │--permission-mode │ │--permission..│ │--permission..  ││
│  │  bypassPerms     │ │  bypassPerms │ │  bypassPerms   ││
│  │< security.md     │ │< perf.md     │ │< correct.md   ││
│  │> security.out    │ │> perf.out    │ │> correct.out  ││
│  └────────┬─────────┘ └──────┬───────┘ └──────┬────────┘│
│           │                  │                 │         │
│  Phase 2: verify_citations.py (deterministic)            │
│           │                  │                 │         │
│  Phase 3: Synthesis                                      │
│  ┌────────▼──────────────────▼─────────────────▼────────┐│
│  │claude --print --tools ""                             ││
│  │< synthesize.md (inlines all verified reviews)        ││
│  │> final-review.md                                     ││
│  └──────────────────────────────────────────────────────┘│
│                                                          │
│  stdout: path/to/final-review.md                         │
└──────────────────────────────────────────────────────────┘
```

## Specialist Perspectives

Each specialist gets a focused prompt with:
- The diff for orientation
- List of changed files
- Permission to Read/Grep/Glob actual source files
- Strict grounding requirement: every finding must cite file, line range, and quoted code
- If codanna is available (`command -v codanna`), specialists also get impact analysis:
  - `codanna mcp find_callers <symbol> --watch` for upstream dependencies
  - `codanna mcp analyze_impact <symbol> --watch` for blast radius
  - This replaces heuristic grep-based dependency tracing with structural data

### Core specialists (always run)

1. **Correctness** — Logic errors, off-by-one, state management, error handling
2. **Security** — Injection, auth bypass, data exposure, input validation

### Conditional specialists (based on diff content signals)

3. **Performance** — N+1 queries, unnecessary allocations, algorithmic complexity
4. **Concurrency** — Race conditions, deadlocks, shared state (triggered by async/thread/lock signals)
5. **API contract** — Breaking changes, backwards compatibility (triggered by interface/schema changes)

A triage step before Phase 1 determines which 3-5 specialists to run based on file types, content signals, and diff size.

## Input/Output Contract

### Input (same interface as agent-loops)

```bash
# Review changes across multiple commits
multi-specialist-review.sh --git main..feature-branch

# Review with path filters
multi-specialist-review.sh --git main..HEAD -- src/auth/ src/db/

# Pipe a diff
git diff main...HEAD | multi-specialist-review.sh -

# Review a diff file
multi-specialist-review.sh /path/to/changes.diff
```

### Output

File path to final review markdown on stdout (same as agent-loops).

The review markdown includes:
- Per-specialist findings with severity and confidence
- Cross-specialist synthesis
- Confidence scoring (multi-source = high, single-source = flagged)
- Verdict: APPROVE / APPROVE WITH CHANGES / REQUEST CHANGES

## Cost Model

| Component | Estimated cost | Notes |
|-----------|---------------|-------|
| 3 specialist calls | ~$0.50 each | Read access increases token usage vs inlined |
| Synthesis call | ~$0.50 | Inlines verified findings only |
| Citation verifier | ~$0 | Deterministic Python, no API calls |
| **Total** | **~$2-3** | vs ~$0.50 for agent-loops single-turn |

Justified when reviewing: PR merges, multi-commit ranges, security-sensitive paths, or when agent-loops single-turn quality is insufficient.

## Implementation Pieces

1. `scripts/multi-specialist-review.sh` — Orchestrator (bash)
2. `scripts/verify_citations.py` — Citation checker (Python)
3. `references/specialist-security.md` — Security specialist prompt
4. `references/specialist-correctness.md` — Correctness specialist prompt
5. `references/specialist-performance.md` — Performance specialist prompt
6. `references/specialist-concurrency.md` — Concurrency specialist prompt
7. `references/specialist-api-contract.md` — API contract specialist prompt
8. `references/synthesize-prompt.md` — Synthesis prompt template
9. `SKILL.md` updates — Document the multi-specialist mode

## Open Questions

- **Triage mechanism:** How to determine which specialists to run? Static rules (file extensions, keyword grep) or a cheap Claude call?
- **Budget scaling:** Should budget per specialist scale with diff size?
- **Incremental mode:** Can specialists share a file-read cache to avoid redundant reads?
- **Team upgrade path:** If/when Claude teams stabilize, the specialists could be upgraded to team members for cross-challenge capability. The bash orchestrator would be replaced by a team lead prompt, but the specialist prompts and verification hook would carry over.

## Codanna Integration (Optional Enhancement)

When codanna is installed, it can enhance the multi-specialist review at three stages:

### Pre-review phase

Before spawning specialists, run `codanna mcp analyze_impact` via CLI against the
changed symbols to gather structural context. Inject the impact data into each
specialist's prompt so they start with grounded dependency knowledge instead of
inferring it from the diff.

```bash
# Gather impact data for each changed symbol before specialist calls
for symbol in $CHANGED_SYMBOLS; do
  codanna mcp analyze_impact "$symbol" --watch --json >> impact-context.json
done
```

### During review

If the codanna MCP server is running (`codanna serve --watch`), specialists can
query codanna directly via MCP tools — `find_callers`, `analyze_impact`,
`find_symbol` — to verify dependency assumptions in real time rather than relying
solely on Read/Grep/Glob.

### Triage

`codanna mcp analyze_impact` can inform which specialists to activate. For example,
if impact analysis shows database-layer callers are affected, activate the
performance specialist. If the impact graph touches auth modules, activate the
security specialist. This addresses the open question about triage mechanism by
providing structural signals rather than relying solely on file extensions and
keyword grep.

### Availability

Codanna is optional. The multi-specialist review works without it. When available,
it replaces heuristic grep-based dependency tracing with structural call graph data,
reducing false positives and improving specialist focus.

## Relationship to Agent-Loops

This does NOT replace agent-loops. The intended usage:

```
Atomic commit review        → agent-loops specialist-review.sh  (current, ~$0.50)
Multi-commit / PR review    → multi-specialist-review.sh        (this plan, ~$2-3)
High-stakes / pre-merge     → future team-based review          (pending teams stability)
```

Agent-loops remains the default for per-commit reviews invoked automatically by codex.
