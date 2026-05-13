---
name: architectural-analysis
description: User-triggered deep architectural analysis of a codebase or scoped subtree across eight modes — information architecture, data flow, integration points, UI surfaces, interaction patterns, data model, control flow, and failure modes. This skill should be used when the user asks to "diagram this codebase," "map the architecture," "show the data flow," "give me an ERD," "trace control flow," "find the integration points," "verify the layout pattern," "audit the UX architecture," or any similar request whose primary deliverable is mermaid diagrams plus cited reports under docs/architecture/. Dispatches haiku/sonnet sub-agents in parallel for per-mode exploration, then verifies every citation mechanically before any node lands in a diagram. Not for one-off prose explanations of code (use code-explanation) or for high-level system design from scratch (use system-design).
---

# Architectural Analysis

## Overview

Produce diagram-first architectural reports for a codebase or a scoped subtree. The primary artifact is a set of mermaid diagrams under `docs/architecture/<report-date>/<mode>/`, accompanied by markdown reports that resolve every callout to a `path:line` citation. Every node and every edge in every diagram is grounded in the source — no exceptions outside the explicit synthesized-concept escape hatch.

## When to use

Trigger this skill when the user asks for:

- A full architectural snapshot of a codebase ("run a full architectural analysis")
- A scoped diagram of a subsystem ("diagram the data flow through `<path>`")
- A specific mode by name ("ERD for this app", "where are the failure modes in `<path>`", "map the integration points")

Do not trigger for:

- Pure prose explanations with no diagram requirement (use `code-explanation`)
- New-system design from a blank page (use `system-design`)
- Single-file walkthroughs (use `diffity-tour`)

## Modes

Eight analysis modes. Each has its own callout prefix, primary mermaid diagram type, and dedicated reference file in `references/`.

| Mode | Prefix | Primary diagram | Reference |
|---|---|---|---|
| Information architecture | `I-` | `graph TD` (module hierarchy) or C4 container | `references/mode-information.md` |
| Data flow | `D-` | `flowchart LR` + `sequenceDiagram` per critical path | `references/mode-data-flow.md` |
| Integrations | `X-` | C4 context boundary | `references/mode-integrations.md` |
| UI surfaces | `U-` | route tree + component graph | `references/mode-ui-surfaces.md` |
| Interaction patterns | `P-` | `graph TD` per-surface pattern decomposition | `references/mode-interaction-patterns.md` |
| Data model | `M-` | `erDiagram` | `references/mode-data-model.md` |
| Control flow | `C-` | `stateDiagram-v2` + `sequenceDiagram` | `references/mode-control-flow.md` |
| Failure modes | `F-` | annotated flowchart with error edges | `references/mode-failure-modes.md` |

Callout IDs are stable across modes — `I-12` referenced from a data-flow report points to the same physical node in the IA diagram. The cross-mode index in the synthesis README binds them.

### Note on interaction patterns

UI surfaces inventories *what* user-facing entry points exist. Interaction patterns answers *how* content within those surfaces is organized: bands vs. tabs, sticky inspector, progressive disclosure, master-detail, wizard, accordion. Two layouts can have identical component imports and still create radically different user mental models — this mode reads composition shape, ARIA roles, state shape, and pattern-naming conventions to surface the difference. See `references/mode-interaction-patterns.md` for signals and the raised synthesized cap (35% vs. 20% for other modes) that reflects the inherently more emergent nature of pattern detection.

## Workflow

Five phases. Do not skip phases. Do not collapse phases. Each phase has a single purpose and discarding work later is cheaper than skipping verification.

### 1. Scope

Establish:

- **Target**: full repo, subtree, or named feature
- **Modes**: which of the seven (default: all if user said "full analysis")
- **Output root**: `docs/architecture/<YYYY-MM-DD>/` — create now if missing
- **Codanna availability**: check for `.codanna/` in the target. Codanna grounds citations faster than grep; if absent, the orchestrator falls back to grep.

### 2. Dispatch sub-agents (parallel)

Read `references/subagent-dispatch.md` for the agent type / model matrix and prompt templates. One sub-agent per mode, dispatched in a single message with multiple `Agent` tool calls (parallel), one-shot — never with `team_name` (see memory: team-spawned agents lose tools).

Each sub-agent returns **candidate findings** in the structured contract from `references/subagent-dispatch.md`. Findings are not yet committed to a diagram.

### 3. Verify (orchestrator)

Read `references/verification-protocol.md`. The orchestrator runs the mechanical verification pass over each candidate finding:

- Resolve every cited symbol (codanna preferred, grep fallback).
- `Read` each cited line and confirm content matches the evidence string.
- For "missing X" or absence claims — grep for X and discard the finding if X exists.
- For synthesized concepts — confirm justification is present; cap synthesized share at 20% per mode (see `references/citation-protocol.md`).

Maintain a **discard log** for the verification log section of each report.

### 4. Render

For each verified mode:

- Author `<mode>/<diagram>.mmd` per `references/mermaid-conventions.md`
- Render to SVG: `bash scripts/render.sh docs/architecture/<date>/`
- Author `<mode>/report.md` per `references/report-template.md`

### 5. Synthesize

- Author top-level `docs/architecture/<date>/README.md` per `references/synthesis-readme.md` — cross-mode callout index, scope, verification summary.
- Optional shareable artifacts:
  - `bash scripts/compile-html.sh docs/architecture/<date>/` produces a single self-contained `<date>.html` (embedded SVGs + inline CSS, dark theme). Pass `--banner <path>` to add a header banner image; for product-specific use, pass the project's banner asset (e.g., `--banner docs/assets/images/cortex-banner.png`).
  - `bash scripts/compile-pdf.sh docs/architecture/<date>/` produces `<date>.pdf` via pandoc. Useful for archival; HTML is preferred for sharing.
  - Run only if the user asked for a shareable artifact.

## Output layout

```
docs/architecture/2026-05-09/
├── README.md                          # synthesis + cross-mode callout index
├── information/
│   ├── ia.mmd
│   ├── ia.svg
│   └── report.md
├── data-flow/
│   ├── flow.mmd
│   ├── sequence-<critical-path>.mmd
│   ├── *.svg
│   └── report.md
├── integrations/{boundaries.mmd,*.svg,report.md}
├── ui-surfaces/{routes.mmd,components.mmd,*.svg,report.md}
├── interaction-patterns/{patterns.mmd,*.svg,report.md}
├── data-model/{erd.mmd,erd.svg,report.md}
├── control-flow/{state.mmd,sequence-*.mmd,*.svg,report.md}
├── failure-modes/{failures.mmd,failures.svg,report.md}
├── 2026-05-09.html                    # optional, scripts/compile-html.sh
└── 2026-05-09.pdf                     # optional, scripts/compile-pdf.sh
```

## Strict citation policy

Read `references/citation-protocol.md` before authoring any diagram. Summary:

- Every node carries a callout ID and a `path:line` citation.
- Every edge carries a citation (line where A → B occurs) or is marked synthesized.
- Synthesized concepts (no single owning file) are visually distinct in the diagram (`classDef synthesized stroke-dasharray:5`) and listed separately in the report. Cap: ≤20% of nodes per mode.
- Every report carries a verification log of what was discarded and why.

Fabricated citations are the dominant failure mode for diagram-first analysis. The verification phase is the load-bearing part of this skill — do not skip it.

## Resources

- `references/citation-protocol.md` — strict citation rules and synthesized cap
- `references/verification-protocol.md` — orchestrator's mechanical verification pass
- `references/subagent-dispatch.md` — agent/model matrix and prompt templates
- `references/mermaid-conventions.md` — diagram types, callout prefixes, classDef rules
- `references/report-template.md` — per-mode `report.md` skeleton
- `references/synthesis-readme.md` — top-level `README.md` template
- `references/mode-{information,data-flow,integrations,ui-surfaces,interaction-patterns,data-model,control-flow,failure-modes}.md` — per-mode guides
- `scripts/render.sh` — render `*.mmd` to `*.svg` via `mmdc`
- `scripts/compile-html.sh` — combine reports into a single self-contained styled HTML via pandoc; supports `--banner <path>`
- `scripts/compile-pdf.sh` — combine reports into a single PDF via pandoc
- `scripts/verify-citations.sh` — quick path:line existence check over a report
- `assets/template.html` — pandoc HTML template used by compile-html.sh
- `assets/report.css` — dark theme stylesheet used by compile-html.sh
