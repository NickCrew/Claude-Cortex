# Verification Protocol

The orchestrator's mechanical pass over candidate findings returned by sub-agents. This is what enforces the citation policy. Sub-agents fabricate at predictable rates; verification is the structural safeguard.

## Inputs

A list of candidate findings from one or more sub-agents, each shaped per `subagent-dispatch.md`:

```yaml
- callout_id: I-12
  label: "TUI ContentSwitcher view registry"
  citation: claude_ctx_py/tui/main.py:104
  evidence: "        switcher = ContentSwitcher(initial=\"overview\")"
  relations:
    - to: I-7
      kind: imports
      citation: claude_ctx_py/tui/main.py:14
  confidence: high
```

## Pass 1 — Symbol resolution

For each finding's `citation` (and each `relations[*].citation`):

1. **Codanna first** if `.codanna/` exists in the target. Use `mcp__codanna_*` tools to confirm the symbol is defined at the cited path. Codanna's index is authoritative for "exists" questions.
2. **Grep fallback** if codanna is unavailable. `grep -n "<symbol-or-anchor>" <path>` and confirm a match near the cited line.
3. **Read the line.** Use `Read` with `offset=<line-1>` and a small `limit` (e.g., 3) to fetch the cited line plus context.
4. **Match evidence to line.** The `evidence` string must appear verbatim on (or starting at) the cited line. Trim leading/trailing whitespace before comparing — match on substring, not equality.

If any of these fail, the finding is **discarded** and logged.

## Pass 2 — Absence claims

A finding whose label or evidence asserts absence (`"no X handler"`, `"missing Y validation"`, `"doesn't emit Z"`) is checked separately:

1. Construct a grep target for the asserted-missing symbol (`X handler`, `validate.*Y`, `emit.*Z`).
2. Grep across the *target subtree*, not just the file the sub-agent looked at. Sub-agents narrow context aggressively and over-fire on absence.
3. If the symbol turns up, the finding is discarded. Log it as "absence claim rejected: `<symbol>` exists at `<path:line>`".

## Pass 3 — Synthesized validation

For each finding marked `confidence: synthesized`:

1. Confirm a `synthesized_justification` field exists and is non-trivial (not just "no single owner").
2. Confirm at least two contributing files are named in the justification.
3. Cite each contributing file at a representative line.
4. Track the synthesized count and the verified-cited count for the mode. After all findings are processed, compute synthesized share:

```
synthesized_share = synthesized_count / (synthesized_count + cited_count)
```

Per-mode caps:
- Interaction patterns (`P-`): 0.35
- All other modes: 0.20

If `synthesized_share` exceeds the mode's cap, decide before rendering:

- **Promote**: pick the most-canonical contributing file for each weakest synthesized node and re-classify as cited.
- **Drop**: remove weakest synthesized nodes until under cap.
- **Escalate**: tell the user the synthesized share is high and ask whether to proceed, raise the cap, or rescope. High synthesized share is signal that the architecture is unusually implicit — sometimes that's the finding.

## Pass 4 — Edge consistency

For each verified node, walk its `relations`. Each relation's `to` must be the callout ID of another verified node. Dangling edges (pointing to discarded or non-existent IDs) are dropped, and the drop is logged.

## Outputs

Two artifacts feed the rendering phase:

1. **Verified findings** — survivors of all four passes, ready to commit to mermaid + report.
2. **Discard log** — every dropped finding with reason. Goes verbatim into the report's "Verification log" section.

## Tooling preference

When checking citations, prefer in this order:

1. **codanna MCP** — `mcp__codanna_codebase-intelligence__*` for symbol-level questions when `.codanna/` exists.
2. **`Read`** — for fetching a specific line range to verify content.
3. **`grep` via Bash** — for absence checks and bulk symbol lookups across a subtree.

Do not use the `Explore` agent or any sub-agent for verification. Verification is the orchestrator's job; delegating it re-introduces the fabrication risk it exists to defeat.

## Performance

Verification is the bottleneck. Budget:

- Symbol resolution: ~200ms per finding with codanna, ~500ms with grep.
- Line read: ~50ms per finding.
- Total for ~50 findings per mode × 7 modes ≈ 30s–2min depending on tooling.

Acceptable. Skipping verification to save time is not — fabricated nodes cost days of debugging confusion downstream.

## When verification cannot run

If codanna is unavailable *and* grep fails (e.g., the target is a remote codebase you can't read), this skill cannot produce trustworthy diagrams. Tell the user:

> Architectural analysis with strict citations requires read access to the target codebase. Verification cannot run remotely. Either grant local access or rescope the analysis to a smaller, mirrored subset.

Do not produce a diagram with un-verified citations. That's the failure mode this skill exists to prevent.
