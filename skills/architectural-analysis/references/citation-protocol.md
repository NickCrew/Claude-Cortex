# Citation Protocol

The load-bearing rule of this skill. A diagram is a set of falsifiable claims; a citation is what makes a claim falsifiable. Without strict citation, the skill produces confident-looking architectural fiction.

## Core rules

1. **Every node carries a callout ID and a `path:line` citation.**
   - Format: `path/to/file.ext:LINE` (use absolute or repo-relative paths consistently within a single report; repo-relative is preferred).
   - The line cited is the line where the symbol is *defined* (function/class/module declaration, route registration, schema field, etc.). Not where it is used.

2. **Every edge carries a citation.**
   - The line where the relationship is established: import statement, call site, route registration, event emission, type reference.
   - If the edge spans multiple lines (e.g., a long call chain), cite the originating line.

3. **Absence claims grep first.**
   - Findings of the shape "no X handler", "missing Y", "doesn't validate Z" must grep for the asserted-missing symbol *before* the finding is recorded.
   - Sub-agents over-fire on absence claims because they reason from a short window of code. The orchestrator discards any absence claim where the symbol turns up in a grep.

4. **Quoted code is exact.**
   - Evidence strings in findings are verbatim copies of the cited line. Paraphrase counts as fabrication; reject and re-cite.

## Synthesized concepts

Some architectural truths don't live in a single file. Examples:

- "The TUI's state machine" — embodied across `tui/main.py`, view modules, and binding maps. No single line declares it.
- "The hook contract" — implicit in how multiple hooks read and write a shared structure, not stated anywhere.
- "The event lifecycle" — emerges from coordinated calls across a worker pool.

These are real and worth diagramming. They are also the primary vector for fabrication. The escape hatch:

### Synthesized-node requirements

- Marked in mermaid with `classDef synthesized stroke-dasharray:5,stroke:#888` (see `mermaid-conventions.md`).
- Listed in a dedicated **Synthesized concepts** section of the report with a written justification.
- Justification names the *contributing files* (cited individually) and explains why no single line owns the concept.
- Cap: **≤20% of nodes per mode** may be synthesized, with one exception:
  - **Interaction patterns mode (`P-`) has a 35% cap.** Pattern detection is inherently more emergent — bands-vs-tabs distinctions, sticky inspectors, and progressive disclosure are rarely declared in any single line. The raised cap reflects the nature of the signal, not a relaxation of rigor. Each synthesized pattern still requires a justification naming ≥2 contributing files.
- If a mode exceeds its cap, either:
  - Promote synthesized nodes to cited nodes by citing the most-canonical contributing file, or
  - Drop the weakest synthesized nodes until under the cap, or
  - Surface the cap breach to the user before proceeding (signals that the codebase pattern is unusually emergent and may need a different framing).

Edges into or out of a synthesized node still need citations on the *cited* end. A synthesized→cited edge cites the line in the cited file where the relationship surfaces.

## Citation format inside reports

In the markdown report, every callout entry resolves once in the **Callouts** table:

```markdown
| ID | Label | Citation | Confidence |
|----|-------|----------|------------|
| I-1 | claude_ctx_py.core.agents | claude_ctx_py/core/agents.py:1 | high |
| I-2 | TUI app shell | claude_ctx_py/tui/main.py:42 | high |
| I-3 | Hook registration contract | — | synthesized |
```

In narrative prose, refer to a callout by ID alone (`[I-1]`), not by re-citing the path. The callout table is the source of truth.

## What is NOT a citation

- A path with no line number (`claude_ctx_py/core/agents.py`) — too vague, fails verification.
- A line range (`agents.py:1-50`) — pick the canonical line; ranges hide imprecision.
- A search query as a stand-in (`grep "def foo" claude_ctx_py/`) — that's how to find the citation, not the citation itself.
- A symbol name without location (`AgentGraph`) — the verification protocol cannot resolve names without a path hint.

## Verification log section

Every per-mode `report.md` includes a **Verification log** section listing:

- Findings discarded as fabricated (with the bad citation and why it failed)
- Absence claims rejected (with grep evidence the asserted-missing symbol exists)
- Synthesized cap pressure (if synthesized share approached the cap)
- Citations the orchestrator could not verify and why (e.g., file not in scope, line moved due to concurrent edits)

A clean verification log is suspicious. A real run nearly always discards something. An empty log signals the orchestrator skipped the pass.
