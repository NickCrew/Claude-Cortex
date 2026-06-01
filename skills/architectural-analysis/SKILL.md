---
name: architectural-analysis
description: User-triggered deep architectural analysis of a codebase or scoped subtree across eight modes — information architecture, data flow, integration points, UI surfaces, interaction patterns, data model, control flow, and failure modes. This skill should be used when the user asks to "diagram this codebase," "map the architecture," "show the data flow," "give me an ERD," "trace control flow," "find the integration points," "verify the layout pattern," "audit the UX architecture," or any similar request whose primary deliverable is mermaid diagrams plus cited reports under docs/architecture/. Dispatches haiku/sonnet sub-agents in parallel for per-mode exploration, then verifies every citation mechanically before any node lands in a diagram. Not for one-off prose explanations of code (use code-explanation) or for high-level system design from scratch (use system-design).
keywords:
  - architectural analysis
  - diagram this codebase
  - map the architecture
  - data flow
  - ERD
  - control flow
  - integration points
  - UX architecture
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

Doc-first. The team's in-tree docs are treated as **the spine of the report**. The analysis confirms documented behavior with citations, flags drift where the doc no longer matches code, and surfaces gaps where code does something undocumented. The deliverable is a single report — readers should not have to consult docs separately to know what's true. Each mode report leads with the doc reference (collapsed for those who already know the territory) and uses the narrative to highlight gaps and drift.

Eight phases. Each has a single purpose; do not collapse them.

### 1. Scope

Establish:

- **Target**: full repo, subtree, or named feature.
- **Modes**: which of the eight (default: all if user said "full analysis").
- **Output root**: `docs/architecture/<YYYY-MM-DD>/` — create now if missing.
- **Codanna availability**: check for `.codanna/`. Falls back to grep if absent.

### 2. Read in-tree docs (load the spine)

Find every authoritative doc and **read each one**. This is the load-bearing change: the docs become the prior the rest of the workflow operates on.

```bash
find <target>/docs <target>/*/docs -maxdepth 4 -type f \( -name '*.md' -o -name 'CHANGELOG*' \) 2>/dev/null
find <target>/CLAUDE.md <target>/*/CLAUDE.md <target>/*/README.md 2>/dev/null
find <target>/cf-web-container*/SHUTDOWN*.md <target>/cf-web-container*/GRACEFUL*.md 2>/dev/null
```

Persist the list to `docs/architecture/<date>/docs-inventory.txt`. **Then read them all** (orchestrator, not delegated — the orchestrator owns the doc map and treats the docs as authoritative). Build a working topic→doc index — which doc is authoritative on which subsystem. The output of this phase is `docs/architecture/<date>/doc-map.md`:

```markdown
# Doc map

| Topic | Doc | Modes |
|-------|-----|-------|
| Handlebars 3-layer cache | mainwebcode/docs/HANDLEBARS_CACHING.md | data-flow, control-flow |
| KV-store migration (cache + persist) | mainwebcode/docs/cache-migration/*.md | control-flow, data-model |
| Container shutdown 5-layer signal flow | mainwebcode/cf-web-container-next/GRACEFUL_SHUTDOWN.md | control-flow, failure-modes |
| WAF triage + DetectionOnly→On runway | cosential-proxy/docs/waf-triage-process.md | failure-modes, integrations |
| Okta Admin auth handshake | mainwebcode/docs/okta-authentication-crm-admin.md | data-flow, integrations |
| SQL metrics instrumentation | mainwebcode/docs/sql-metrics.md | failure-modes, control-flow |
| Tests & test runner | mainwebcode/docs/tests.md | failure-modes |
| Legacy EC2 topology (drift) | mainwebcode/docs/architecture-diagram.md | information *(stale)* |
```

A **stale** marker is set when the orchestrator's read of the doc reveals it describes a topology or stack that's no longer current (e.g., legacy EC2 vs. current k8s). Mark the doc as `*(stale)*` in the table and treat it like a gap target rather than a spine entry.

If a target has no docs beyond `README.md` + `CLAUDE.md`, mark this in the synthesis README ("Greenfield doc surface — analysis is gap-only") and proceed.

### 3. Dispatch sub-agents (parallel, primed with the doc map)

Each sub-agent now receives the doc map plus the doc text relevant to its mode. The contract changes shape: sub-agents don't enumerate everything they find — they classify against the documented spine.

Read `references/subagent-dispatch.md` for the prompt template. The output contract is:

```yaml
- callout_id: D-12
  label: "Handlebars Layer 3 cache.put 60s TTL"
  citation: app/com/util/handlebars.cfc:99
  evidence: "this.cache.put(cbKey, local.result, 60000);"
  classification: confirms              # confirms | drift | gap | extends
  doc_ref: mainwebcode/docs/HANDLEBARS_CACHING.md
  doc_claim: "Layer 3: handlebars_templates_{hash} TTL 60,000s"
  notes: "Doc claim verified; cited line matches the TTL value."
```

- **confirms** — code matches the doc claim. Cited for evidence, but the doc is the spine.
- **drift** — code disagrees with the doc. Cited explicitly with the doc claim quoted alongside the code claim. **Drift findings always make it into the report's Drift section, not collapsed.**
- **gap** — code does something the docs don't cover. **Gap findings drive the synthesis README.**
- **extends** — code adds detail the doc doesn't claim. Edge case between confirms and gap.

Sub-agents must NOT re-document territory the spine doc covers cleanly. If `HANDLEBARS_CACHING.md` already explains the 3-layer cache, the data-flow sub-agent's job is to (a) cite the canonical line for each layer (confirms) and (b) report drift or gaps — not to write its own cache description.

Dispatch in a single message with parallel `Agent` tool calls. One sub-agent per mode. Never with `team_name`.

### 4. Verify (orchestrator)

Mechanical pass per `references/verification-protocol.md`:

- Resolve every cited symbol (codanna or grep).
- `Read` each cited line; evidence string must match verbatim.
- Absence claims (`gap` findings often) — grep first; discard if the asserted-missing symbol exists.
- For drift findings — read both the doc claim location and the code; confirm the disagreement is real.
- For gap findings — confirm no doc in the spine covers the behavior.

### 5. Render diagrams

Same as before. Author `<mode>/<diagram>.mmd` per `references/mermaid-conventions.md`. Run `bash scripts/render.sh <report-dir>/ --style corporate`.

### 6. Author mode reports (doc-led, gap-first narrative)

Per `references/report-template.md`. The new template's structure:

1. **Summary** — one paragraph. Lead with the spine doc reference: "Per `HANDLEBARS_CACHING.md`, the cache is three-layer with TTLs 60s/no-expiry/60s; this report verifies that and surfaces N gaps." If there's no spine doc, say "No in-tree doc covers this mode; this report is the documentation."
2. **Diagram** — the rendered .svg/.png.
3. **Doc reference (collapsed)** — `<details class="receipts">` containing the relevant excerpt or link from the spine doc(s) plus a `confirms`-classification table. Readers who already know the territory keep it collapsed.
4. **Drift** (only if any) — never collapsed. Each drift item: doc claim → code reality → impact → recommendation.
5. **Gaps** — what the code does that no doc covers. The narrative section. **This is the section worth reading.** Each gap is a callout-cited finding with prose.
6. **Receipts (collapsed)** — Callouts table, Verification log, Synthesized concepts. Available for click-through verification but not in the reading flow.

The diagram is built from confirms + drift + gap nodes together. Drift edges are styled `-.->|drift|`. Gap nodes use `classDef gap fill:...,stroke-dasharray:2`.

### 7. Synthesize (gap-first README)

Author `docs/architecture/<date>/README.md` per `references/synthesis-readme.md`. The new shape:

1. **Scope + doc map** — one paragraph + the doc-map table from Phase 2. Sets the spine.
2. **Undocumented behaviors** — the gap inventory across all modes. The institutional risk register. **This is the lead.**
3. **Documentation drift** — every drift finding from Phase 6 reports. Curated, not dumped.
4. **Headline architectural findings** — 3-7 cross-cutting findings the reader should leave with. Reference both confirms and gaps.
5. **Verification summary** — the per-mode counts (verified/drift/gap/synthesized).
6. **Open questions** — de-duplicated from per-mode reports.

Drop the standalone "Authoritative in-tree docs" table — its content is now the doc-map header (Phase 2's output) and is referenced inline by every mode report's Summary.

### 8. Compile HTML (automatic)

Run `bash scripts/render.sh <report-dir>/ --style corporate` then `bash scripts/compile-html.sh <report-dir>/`. The HTML carries light + dark diagram variants and a runtime theme toggle.

### Optional: hand-off

The architectural analysis is descriptive (with a curated gap list). If the user wants to act on it:

- For undocumented behaviors that need writeup → invoke `doc-maintenance` (with the gap inventory as prior).
- For UI↔backend mismatches surfaced in gaps → invoke `wiring-audit`.
- For documentation drift → invoke `doc-claim-validator` to confirm before patching docs.
- For test-coverage gaps → invoke `test-review`.

Do not auto-invoke. Recommend, let the user choose.

### Shareable artifacts

**HTML — produce automatically.** Two-step pipeline after Phase 5/5b:

```
bash scripts/render.sh docs/architecture/<date>/ --style corporate
bash scripts/compile-html.sh docs/architecture/<date>/
```

Defaults:
- **Style: `corporate`** — Stripe/Linear-style modern SaaS doc. Inter font, generous whitespace, soft shadows, single deep-blue accent, card-based sections.
- **Theme: `light`** — initial theme baked at compile time; users toggle at runtime via the top-right button (preference persists to localStorage).

Available styles: `corporate` (default), `blueprint` (the engineering/violet aesthetic). Both ship with light + dark themes; the runtime toggle just swaps `data-theme` on `<html>` and CSS variables + paired SVG variants do the rest.

Flags:
- `--style {corporate|blueprint}` — visual style (must match what render.sh produced).
- `--theme {light|dark}` — initial theme. Default `light`.
- `--banner <path>` — header banner image, resolved relative to `--repo-root` (default cwd).
- `--repo-root <path>` — repo root for banner resolution.
- `--out <path>` — output HTML path. Default `<report-dir>/<dirname>.html`.

**Important:** `render.sh --style <X>` produces `<base>-<X>-light.svg` and `<base>-<X>-dark.svg` for each diagram. `compile-html.sh --style <X>` looks for those exact filenames. If you compile with a style that wasn't rendered first, images will be broken; render both styles to keep all four combos available simultaneously.

**PDF — only on request.** Run `bash scripts/compile-pdf.sh docs/architecture/<date>/` only if the user explicitly asks for a PDF. Defaults to landscape; pass `--portrait` to override. PDF consumes the style-agnostic `.png` files (no light/dark there). Useful for archival; HTML is preferred for everyday sharing.

## Output layout

```
docs/architecture/2026-05-09/
├── README.md                          # synthesis — gap inventory leads,
│                                      #   then drift, then headline findings
├── docs-inventory.txt                 # Phase 2: list of in-tree docs found
├── doc-map.md                         # Phase 2: topic→doc index (the spine)
├── information/
│   ├── ia.mmd
│   ├── ia-corporate-light.svg
│   ├── ia-corporate-dark.svg
│   └── report.md
├── data-flow/{flow.mmd, *.svg, report.md}
├── integrations/{boundaries.mmd, *.svg, report.md}
├── ui-surfaces/{routes.mmd, *.svg, report.md}
├── interaction-patterns/{patterns.mmd, *.svg, report.md}
├── data-model/{erd.mmd, *.svg, report.md}
├── control-flow/{state.mmd, *.svg, report.md}
├── failure-modes/{failures.mmd, *.svg, report.md}
├── 2026-05-09.html                    # automatic, compile-html.sh
└── 2026-05-09.pdf                     # opt-in only, compile-pdf.sh
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
- `references/subagent-dispatch.md` — agent/model matrix and the doc-led prompt template (with `confirms`/`drift`/`gap`/`extends` classification contract)
- `references/mermaid-conventions.md` — diagram types, callout prefixes, classDef rules (including `drift` and `gap` styling)
- `references/report-template.md` — per-mode `report.md` skeleton (doc-led, gap-first)
- `references/synthesis-readme.md` — top-level `README.md` template (gap inventory first, drift second, headline findings third)
- `references/doc-map.md` — Phase 2 doc map template and authoring guidance
- `references/mode-{information,data-flow,integrations,ui-surfaces,interaction-patterns,data-model,control-flow,failure-modes}.md` — per-mode guides
- `scripts/render.sh` — render `*.mmd` to `*.svg` AND `*.png` via `mmdc` (PNG is what compile-pdf.sh consumes; SVG for HTML/screen)
- `scripts/compile-html.sh` — combine reports into a single self-contained styled HTML via pandoc; supports `--banner <path>`
- `scripts/compile-pdf.sh` — combine reports into a single PDF via pandoc; defaults to landscape, supports `--portrait`; injects table-friendly CSS overlay when weasyprint is the engine
- `scripts/verify-citations.sh` — quick path:line existence check over a report
- `assets/template.html` — pandoc HTML template used by compile-html.sh
- `assets/report.css` — dark theme stylesheet used by compile-html.sh
- `assets/mermaid-config.json` — mermaid CLI config (`htmlLabels: false`, `useMaxWidth: false`) used by render.sh to keep text rendering correct in PDF and let wide diagrams scale up
