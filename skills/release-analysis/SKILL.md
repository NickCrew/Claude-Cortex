---
name: release-analysis
description: >-
  User-triggered analysis of how a system gets deployed and recovered — across local (Docker Compose) and cloud (Kubernetes / Eve) release surfaces. Produces mermaid diagrams plus cited reports for promotion paths, environment topology, configuration provenance, and recovery procedures under docs/release/<date>/. Layers on top of architectural-analysis: when a recent docs/architecture/<date>/ report exists, this skill ingests its control-flow, integrations, and failure-modes findings rather than re-deriving them. When verifying cloud-side claims, prefers eve-mcp tools (ShowEnvironments, GetManifest, ShowChannels, ShowDeploymentCrons) over reading manifest YAML by hand. Trigger on "map our release," "trace the promotion path," "where does this config come from," "what's the rollback story," "diagram the environments," "show how a version reaches prod," or any release-shaped question whose deliverable is a diagram plus a cited report. Not for new architectural snapshots (use architectural-analysis), CI pipeline correctness review (use code review), or designing a release process from scratch (use system-design).
keywords:
  - release analysis
  - map our release
  - promotion path
  - rollback story
  - environment topology
  - configuration provenance
  - deployment recovery
---

# Release Analysis

## Overview

Produce diagram-first release reports for a codebase that ships somewhere — locally via Docker Compose, to a Kubernetes cluster via Eve, or both. The primary artifact is a set of mermaid diagrams under `docs/release/<report-date>/<mode>/`, accompanied by markdown reports that resolve every callout to a `path:line` citation (or, for cloud-side topology claims, an `eve-mcp:<tool>:<query>` citation). Every node and every edge in every diagram is grounded in source or in a verifiable platform query — no exceptions outside the synthesized-concept escape hatch.

This skill is a **layer on top of** `architectural-analysis`. When that skill has already run against the same scope and the report is fresh (default: ≤30 days), release-analysis ingests its findings rather than re-deriving them. The seam is explicit and load-bearing — see Phase 0 below.

## When to use

Trigger this skill when the user asks for:

- A full release map of a system ("map how we deploy this," "diagram the release")
- A specific release-shaped question by name ("trace the promotion path to prod," "where does `WAF_ENABLED` come from in stage," "what's the rollback story for the migration job")
- An environment topology view ("show me which manifests run in which namespaces," "which compose profile has which services")

Do not trigger for:

- Architectural snapshots that don't focus on deployment ("diagram the data flow") → use `architectural-analysis`
- CI pipeline correctness or `.gitlab-ci.yml` review → use code review
- Designing a new release process from a blank page → use `system-design`
- Single-question lookups that don't justify diagrams ("what's the prod image tag?") → answer directly

## Modes

Four analysis modes. Each has its own callout prefix, primary mermaid diagram type, and dedicated reference file in `references/`.

| Mode | Prefix | Primary diagram | Reference |
|---|---|---|---|
| Promotion path | `R-` | `flowchart LR` (commit → build → image → manifest → running instance) | `references/mode-promotion-path.md` |
| Environment matrix | `E-` | `graph TD` (env × namespace × cluster) for cloud; profile × service matrix for local | `references/mode-environment-matrix.md` |
| Configuration provenance | `K-` | layered annotation graph (key → source → override order) | `references/mode-configuration-provenance.md` |
| Recovery & rollback | `V-` | `stateDiagram-v2` (healthy → degraded → recovering) plus procedure list | `references/mode-recovery-rollback.md` |

Callout IDs are stable across modes — `R-7` referenced from a recovery report points to the same physical node in the promotion-path diagram. The cross-mode index in the synthesis README binds them.

### Cross-skill callout reuse

Callouts ingested from a prior `architectural-analysis` run keep their original prefix (`I-`, `C-`, `F-`, `X-`, etc.) and are referenced by ID without reproduction. A release-analysis callout `R-7` may cite `[C-17]` from the prior arch-analysis report; the synthesis README links to the originating mode's report rather than copying the entry.

## Three release shapes

Most release-analysis targets are systems that *get* deployed — the unit of analysis is the system itself. But some targets are tooling that *drives* releases for other systems — the unit of analysis flips. The skill recognizes three shapes:

| Concern | Compose-shaped (local) | Kube-shaped (cloud) | Driver-shaped (orchestrator) |
|---|---|---|---|
| What the target is | a deployable system, run locally | a deployable system, run in Kube | tooling that performs release operations on other systems |
| Unit | service in `compose.*.yml` | application in a `manifest` | release operation (cut, forward-merge, close-release, environment-roll) |
| Group | profile / compose project | namespace | targeted fleet (the repos / namespaces this tool operates on) |
| Boundary | docker network | cluster + namespace | the set of repos / channels this tool manages |
| Promotion | image rebuild + `docker compose pull` + `up.sh` | channel-based version promotion via Eve | the multi-step pipeline this tool encodes (e.g., cut → forward-merge → close-release) |
| Pinning | image tag in `.env` or `compose.*.yml` | `SetManifestVersion` / `SetNamespaceVersion` | how the tool selects targets per run (`config.json`, `namespaces.json`, `manifests.json`, cron config) |
| Rollback | revert image tag, `docker compose up -d` | `UnpinManifestVersion` then re-promote prior version | the recovery procedures the tool itself implements (or the runbooks for when its operations fail mid-flight) |
| Config layering | compose merge order, `.env`, profile YAMLs | manifest metadata, env-specific overrides, secrets, ConfigMaps | how `config.json`, env vars, `.profile`, per-namespace data files resolve at runtime |

A repo can be one shape, multiple, or — in driver-shaped cases — all three at once if the tool also ships itself. Detection happens in Phase 0.

### Driver-shaped reframe

When the target is driver-shaped (PowerShell tooling that orchestrates fleet releases, deploy-bot scripts, release-cutting CLIs, etc.), each mode reframes:

- **Promotion path** — the multi-step pipeline this tool drives across the targeted fleet, not how the tool itself reaches a runtime. CI publishing of the tool itself is a footnote, not the main diagram.
- **Environment matrix** — the namespaces / clusters / repos the tool manages, sourced from its config files (`namespaces.json`, `manifests.json`, etc.). The tool's *own* runtime is incidental.
- **Configuration provenance** — how the tool's per-run inputs resolve (config files, env vars, profile overrides, cron parameters). Same provenance machinery, different keys.
- **Recovery & rollback** — runbooks the tool documents for partial-pipeline failures (close-release stuck, forward-merge gap, environment-roll mid-state). These are usually the spine of the report; runbook-precedence applies aggressively.

If the target has no Dockerfile, no Compose, no manifests, but does have a `data/` or `config/` directory describing other systems and a `docs/runbooks/` describing fleet operations, it's driver-shaped. Treat the runbooks as the spine and let mode prompts reflect the reframe.

## Workflow

Eight phases. Phases 0, 1b, 5b, and 6 are release-analysis-specific or mirror arch-analysis additions. Do not skip phases.

| Phase | Name | Purpose |
|---|---|---|
| 0 | Ingest prior arch-analysis | Pull in control-flow, integrations, failure-modes findings if a recent report exists |
| 1 | Scope | Establish target, modes, output root, shape detection (compose / kube / driver), eve-mcp availability |
| 1b | Docs inventory | Reuse arch-analysis's `doc-map.md` + `docs-inventory.txt` if ingested; otherwise build fresh. Seeds Phase 5b. |
| 2 | Dispatch sub-agents | Parallel enumeration per mode |
| 3 | Verify | Mechanical citation check (file + eve-mcp) |
| 4 | Render | Mermaid + per-mode reports |
| 5 | Synthesize | Top-level README with cross-mode index |
| 5b | Docs reconciliation | Read in-tree runbooks; reconcile against verified findings; runbooks usually win |
| 6 | Hand-off | Recommend follow-up skills (wiring-audit, doc-claim-validator, etc.) — do not auto-invoke |

### 0. Locate prior architectural analysis (and let it propose scope)

The canonical entry point. A prior arch-analysis run already decided what counts as "the system" — its frontmatter is the source of truth for scope and target_repo. Read it first; let it propose the scope; the user confirms or overrides.

#### Step 0a — Find the most recent prior README

Three resolution paths, in priority order. Stop at the first that resolves.

**1. User-supplied path (preferred when known).** The user can pass a path explicitly — either to a specific run's directory (`docs/architecture/2026-05-16/`) or to its README (`docs/architecture/2026-05-16/README.md`) or to the parent (`docs/architecture/`, in which case pick the latest dated subdirectory). Examples:

> "run release-analysis against ~/source/docs/architecture/2026-05-16/"
> "build on the arch-analysis at ~/source/docs/architecture/"

When a path is supplied, skip the search below and verify the README exists at the resolved location. If the supplied path doesn't resolve, surface the failure to the user — don't silently fall back to a search.

**2. Search well-known locations.** When no path is supplied:

```bash
# Inside the cwd (single-repo scope)
ls -dt <cwd>/docs/architecture/*/ 2>/dev/null | head -1

# Parent directory (common for multi-repo unified scopes — e.g., ~/source/docs/
# holds the union analysis of ~/source/{mainwebcode,cosential-proxy,dev-stack})
ls -dt <cwd>/../docs/architecture/*/ 2>/dev/null | head -1
```

If multiple candidates resolve (e.g., a per-repo run *and* a unified parent run), prefer the broader scope unless the user specifies otherwise — the broader run usually has more useful integrations and failure-mode coverage. Surface the choice to the user when ambiguity exists.

**3. Ask the user.** When both checks miss: ask whether they have a prior arch-analysis path you should use, or whether to proceed without prior context. Never invent a location.

#### Step 0b — Parse frontmatter and propose scope

Read the README's frontmatter and the first ~30 lines (the Scope section). Extract:

- `scope` — what was analyzed (e.g., `full (mainwebcode + cosential-proxy + dev-stack)`)
- `target_repo` — the actual paths (e.g., `~/source/{mainwebcode,cosential-proxy,dev-stack}`)
- `modes` — which arch-analysis modes ran
- `date` — for staleness check
- The "Scope" section's prose, which often names exclusions ("Gen3 SPA not analyzed," "test code excluded") that should carry forward

Present to the user:

> Found architectural analysis from `<date>` at `<path>`, covering `<scope>` (target: `<target_repo>`). Use the same scope for this release analysis?
>
> - **Yes** — inherit scope and ingest findings.
> - **Override** — supply a different target.
> - **Run fresh** — proceed without prior context (worse signal; note in Provenance).

Default to "Yes" if the user provided no contradicting hint. Don't silently override.

#### Step 0c — Decide ingest vs. fresh run

Once scope is fixed:

- **Prior found, ≤30 days old, scope matches:** ingest. Mine the prior report for release-relevant context:
  - `doc-map.md` (Phase 2 of arch-analysis) → topic→doc index of in-tree runbooks. **Reuse as the spine** for release-analysis's Phase 5b instead of re-discovering docs from scratch. Carry the `*(stale)*` markers forward.
  - `docs-inventory.txt` → raw list of docs found by arch-analysis. Use as starting point for Phase 1b.
  - `control-flow/report.md` → seeds promotion-path (startup ordering, `depends_on`, healthcheck gates).
  - `integrations/report.md` → seeds environment-matrix substrate (boundaries, external systems).
  - `failure-modes/report.md` → seeds recovery & rollback (cascade-blocking, restart policies, opt-in/opt-out flags).
  - The cross-mode callout index → carry forward verbatim; release-analysis findings reference these IDs by their original prefix.
  - **Sub-agent classifications** in arch-analysis findings: each ingested callout carries a `classification` (`confirms`, `drift`, `gap`, `extends`) and `doc_ref`/`doc_claim` fields. Release-analysis preserves these — a `gap` from arch-analysis stays a gap when referenced from release-analysis, and a `drift` carries forward as-is.

- **Prior found, >30 days old:** ask the user. Either trust the older run (note staleness in Provenance) or fall through to the next branch.

- **Prior not found, or user chose "Run fresh":** ask the user before triggering anything else. Do not silently re-run an 8-mode analysis. Offer:
  - **Focused arch-analysis run** of just the release-relevant subset (control-flow + failure-modes + integrations modes only) — 3 sub-agents instead of 8.
  - **Proceed without prior context** — release-analysis sub-agents re-derive with worse signal. Note in Provenance.

#### Step 0d — Record the decision

In `docs/release/<date>/README.md`'s **Provenance** section, capture:
- The path of the prior README (or "none").
- The date and age of the prior run.
- The inherited scope and target_repo (or the override the user supplied).
- Which ingest path was taken.

### 1. Scope

If Phase 0 inherited a scope from prior arch-analysis frontmatter, most of this is already decided — only the release-specific fields remain. If Phase 0 found nothing, scope from scratch.

Establish:

- **Target**: inherited from Phase 0 if a prior run was ingested, otherwise full repo / subtree / multi-repo union. For multi-repo systems (e.g., `~/source/{dev-stack,mainwebcode,cosential-proxy}`), the union is treated like a single scope.
- **Modes**: which of the four (default: all)
- **Output root**: `docs/release/<YYYY-MM-DD>/` — create now if missing. Place under the same parent as the prior arch-analysis run (so `~/source/docs/architecture/2026-05-16/` and `~/source/docs/release/2026-05-17/` are siblings).
- **Shape detection** — see "Three release shapes" above for the framings:
  - **Compose-shaped indicators**: `compose*.yml`, `docker-compose.yml`, `up.sh`/`down.sh`, `.env` with image tags
  - **Kube-shaped indicators**: `kube/` or `aws/` directory with config subdirs (`*-dev-config`, `*-config`); markdown referencing `manifest`/`channel`/`namespace`; `.gitlab-ci.yml` jobs that publish images to a registry; presence of an Eve channel name in any markdown
  - **Driver-shaped indicators**: no Dockerfile / Compose / manifests for the target itself, but presence of a `data/<namespace>/`, `data/manifests.json`, `data/namespaces.json`, or similar describing *other* systems; `docs/runbooks/` directory naming fleet operations (cut, forward-merge, close-release, environment-roll); CLI entrypoints (`.ps1`, scripts/) that take channel/namespace/manifest names as arguments
  - Record what was detected and let it shape the mode prompts. A repo can hit one, two, or all three (a release-driver tool that also ships itself is hybrid).
- **eve-mcp availability**: check whether the `eve-mcp` MCP server is configured. If yes, cloud-side verification (Phase 3) uses live queries on par with codanna/grep — read tools only (`Show*`, `Get*`). Action tools (`Deploy`, `Run*`, `Restart*`, `Set*Version`, `Unpin*`, `Patch*`, `Update*`) are release levers and are never invoked from this skill — they may be cited as mechanism in recovery-rollback findings but are not called. If eve-mcp is not configured, fall back to reading manifest YAML and config-directory markdown — note the fallback in the verification log.

### 1b. Docs inventory (reuse or build)

Find authoritative in-tree release docs. Two paths depending on what Phase 0 ingested:

**If a prior arch-analysis run was ingested**, it already produced `docs-inventory.txt` and (more usefully) `doc-map.md` — the topic→doc index that names which doc is authoritative on which subsystem. Reuse both:

1. Copy `<prior>/docs-inventory.txt` → `docs/release/<date>/docs-inventory.txt`.
2. Copy `<prior>/doc-map.md` → `docs/release/<date>/doc-map.md` (or symlink). This is the spine for Phase 5b.
3. Append release-specific finds the arch-analysis inventory may have missed:

```bash
# Release-specific roots arch-analysis may not have walked
find <target>/kube <target>/aws <target>/*/kube <target>/*/aws -maxdepth 4 -type f \
    \( -name '*.md' -o -name 'README*' \) 2>/dev/null
# Compose-shaped repos: top-level walkthroughs
find <target> -maxdepth 2 -type f \
    \( -name 'CHEATSHEET*' -o -name 'PR.md' -o -name 'up.sh' -o -name 'down.sh' \) 2>/dev/null
# Eve manifest documentationUrl fields (cloud, optional — only when eve-mcp available)
# eve-mcp:GetManifest:name=<each manifest> — capture documentationUrl from metadata
```

Add new finds to `docs-inventory.txt` (mark them with `# release-specific addition` comment). Update `doc-map.md` with rows for the new docs, classifying their topic and which release-analysis modes they overlap.

**If no prior arch-analysis was ingested**, build the inventory from scratch:

```bash
# Generic doc roots
find <target>/docs <target>/*/docs -maxdepth 4 -type f \( -name '*.md' -o -name 'CHANGELOG*' \) 2>/dev/null
# Top-level CLAUDE.md / README.md per repo
find <target>/CLAUDE.md <target>/*/CLAUDE.md <target>/*/README.md 2>/dev/null
# Release-specific roots
find <target>/kube <target>/aws <target>/*/kube <target>/*/aws -maxdepth 4 -type f \
    \( -name '*.md' -o -name 'README*' \) 2>/dev/null
# Compose-shaped repos: top-level walkthroughs
find <target> -maxdepth 2 -type f \
    \( -name 'CHEATSHEET*' -o -name 'PR.md' -o -name 'up.sh' -o -name 'down.sh' \) 2>/dev/null
```

Persist the list to `docs/release/<date>/docs-inventory.txt`. Do not read the files yet — Phase 5b reads them.

If the target has no `docs/`, no `kube/*-config/`, and no top-level markdown beyond `README.md` + `CLAUDE.md`, skip Phase 5b and note the absence in the synthesis README.

### 2. Dispatch sub-agents (parallel)

Read `references/subagent-dispatch.md` for the agent type / model matrix and prompt templates. One sub-agent per mode, dispatched in a single message with multiple `Agent` tool calls (parallel), one-shot — never with `team_name`.

Each sub-agent receives:

- The scope from phase 1
- The detected shape (local-only, cloud-only, both)
- Any **ingested findings** from phase 0 — sub-agents reference these IDs rather than re-discovering the underlying facts
- The structured output contract from `references/subagent-dispatch.md`

Sub-agents return **candidate findings**. Findings are not yet committed to a diagram.

### 3. Verify (orchestrator)

Read `references/verification-protocol.md`. The orchestrator runs the mechanical verification pass:

- Resolve every cited symbol or file (codanna preferred, grep fallback).
- `Read` each cited line and confirm content matches the evidence string.
- For absence claims — grep for the asserted-missing symbol; discard if present.
- For cloud-side topology claims — use eve-mcp queries (`ShowChannels`, `GetManifest`, `ShowDeploymentCrons`, `GetDeploymentCron`) to confirm. Treat eve-mcp results as a verification source on par with codanna.
- For configuration provenance claims — confirm the override order by reading the actual resolution mechanism (compose merge order, manifest metadata resolution), not by inferring from filename order.
- For synthesized concepts — confirm justification names ≥2 contributing files; cap synthesized share at 20% per mode (see `references/citation-protocol.md`).

Maintain a **discard log** for each report's verification log section.

### 4. Render

For each verified mode:

- Author `<mode>/<diagram>.mmd` per `references/mermaid-conventions.md`
- Render to SVG: `bash scripts/render.sh docs/release/<date>/ --style corporate` (produces `<base>-corporate-light.svg` and `<base>-corporate-dark.svg`; render `--style blueprint` too if you want all four combos available)
- Author `<mode>/report.md` per `references/report-template.md`

### 5. Synthesize

- Author top-level `docs/release/<date>/README.md` per `references/synthesis-readme.md` — **Provenance** section (what was ingested from arch-analysis), cross-mode callout index, headline release findings, verification summary.

### 5b. Docs reconciliation (read the in-tree docs now)

Before finalizing the synthesis README, reconcile findings with the docs listed in Phase 1b. Read `references/docs-reconciliation.md` for the full protocol. Summary:

1. **Read each in-tree doc once** (orchestrator, not delegated). Group by topic.
2. **For each doc, decide overlap with each mode.** A runbook for promoting a service overlaps promotion-path; a recovery procedure doc overlaps recovery-rollback; a config-overrides cheatsheet overlaps configuration-provenance.
3. **For overlapping docs, run `doc-claim-validator`** via the Skill tool. Pass the doc and the relevant mode reports as input. Capture (a) confirmed claims, (b) contradicted claims (where verified findings disagree), (c) claims the validator couldn't reach.
4. **Apply the release-specific reconciliation rule** (per `references/docs-reconciliation.md`): when reconciling against a runbook for promotion or recovery, the runbook's *procedure* (the ordered steps) is almost always authoritative — even if the report's mechanism citations are correct. A runbook saying "to roll back, first pause the cron, then unpin" supersedes a report saying "rollback uses `SetManifestVersion(prior)`" because the report is missing the cron-pause prerequisite. Promote the runbook; defer.
5. **Author `docs/release/<date>/docs-reconciliation.md`** — table mapping each in-tree doc to the modes it overlaps, with status per doc:
   - **In-tree doc supersedes** — the doc has more correctness or procedural detail. Reference it from the relevant mode report's narrative.
   - **Report supersedes** — the report's verified finding contradicts the doc; the doc is stale. Flag for the team.
   - **Complementary** — covers different surface; cite both.
   - **Adds capability/view** — fills a gap the report missed entirely (prod runbook, on-call recovery, deployment checklist).
   - **Drift** — both are partially right; surface the contradiction explicitly.
6. **Update the synthesis README** with an "Authoritative in-tree docs" section per `references/synthesis-readme.md`. Lead with this section so readers go to the canonical doc first.
7. **Update individual mode reports** to cite in-tree docs where they supersede the report's coverage. One sentence each in the relevant mode's Summary or Narrative.

This phase is the institutional fix for the failure mode where the analysis duplicates or contradicts existing team runbooks. For release analysis specifically, the cost of skipping is high — runbooks encode hard-won procedural knowledge that report-style mechanism citations don't capture.

### 6. Hand-off

The release analysis is descriptive. If the user wants to act on it:

- **Stale runbooks surfaced in Phase 5b** → invoke `doc-claim-validator` directly to triage the full set, or hand the drift findings to the doc owners.
- **Configuration drift between environments surfaced in `configuration-provenance`** → invoke `wiring-audit` (configuration drift is a wiring concern when the UI or CLI for changing the value is also drifted).
- **Recovery procedures with no documentation** → recommend the team author runbooks for the gap states surfaced in `recovery-rollback`.
- **Stale ingested arch-analysis** → recommend re-running `architectural-analysis` if Phase 6 callout-resolution found significant decay.

Do not auto-invoke. Recommend, let the user choose.

### Shareable artifacts

**HTML — produced automatically.** Two-step pipeline at end of Phase 5/5b, mirrors arch-analysis:

```
bash scripts/render.sh docs/release/<date>/ --style corporate
bash scripts/compile-html.sh docs/release/<date>/
```

Defaults:
- **Style: `corporate`** — Stripe/Linear-style modern SaaS doc (Inter font, generous whitespace, soft shadows, deep-blue accent).
- **Theme: `light`** — initial theme baked at compile time; users toggle at runtime via the top-right button.

Available styles: `corporate` (default), `blueprint` (engineering/violet aesthetic). Both ship with light + dark themes; the runtime toggle just swaps `data-theme` on `<html>` and the paired SVG variants render appropriately.

Flags (passed to `compile-html.sh`):
- `--style {corporate|blueprint}` — must match what `render.sh` produced.
- `--theme {light|dark}` — initial theme. Default `light`.
- `--banner <path>` — header banner image, resolved relative to `--repo-root` (default cwd).
- `--out <path>` — output HTML path. Default `<report-dir>/<dirname>.html`.

**Important:** `render.sh --style <X>` produces `<base>-<X>-light.svg` and `<base>-<X>-dark.svg`. `compile-html.sh --style <X>` looks for those exact filenames. Render both styles upfront if you want all four combos available simultaneously.

**PDF — only on request.** Run `bash scripts/compile-pdf.sh docs/release/<date>/` only when the user explicitly asks for a PDF. Defaults to landscape; pass `--portrait` to override. PDF consumes the style-agnostic `.png` files (no light/dark there).

**Combined report (optional).** When the user wants one artifact spanning multiple sibling analyses (architectural + release + wiring-audit, etc.), use the combined compile flow described under "Combined sibling reports" below.

### Combined sibling reports

Release-analysis is a sibling artifact to other diagram-first analyses that build on the same prior arch-analysis (`wiring-audit`, future `security-audit`, etc.). Convention:

- Each analysis writes its own dated subdirectory: `docs/architecture/<date>/`, `docs/release/<date>/`, `docs/wiring-audit/<date>/`, etc. — all under the same parent.
- Each analysis emits its own self-contained HTML by default. Sibling artifacts stay immutable; nothing rewrites a completed arch-analysis run.
- When the user wants a single combined report, run the combined compile (one level up):

```bash
bash <skill-with-combined>/scripts/compile-combined.sh <parent-docs-dir>/ \
    --include architecture/<date> \
    --include release/<date> \
    --include wiring-audit/<date> \
    --banner <path>
# → <parent-docs-dir>/combined-<YYYY-MM-DD>.html
```

The combined script concatenates the included analyses' README + per-mode reports, resolves cross-skill callout references in-document, and embeds all SVGs. Cross-skill references (e.g., a release-analysis `[R-5]` referencing arch-analysis `[C-17]`) become anchor links rather than text-only IDs.

The combined compile script is not yet implemented in this skill — it's a planned addition. Until it lands, share each sibling's HTML separately and let the cross-skill ID conventions do the linking work.

## Output layout

```
docs/release/2026-05-16/
├── README.md                          # synthesis + provenance + cross-mode callout index
│                                      # — leads with "Authoritative in-tree docs" section
├── docs-inventory.txt                 # Phase 1b: list of in-tree release docs (reused or built)
├── doc-map.md                         # Phase 1b: topic→doc index (reused from arch-analysis,
│                                      #   or built fresh; spine for Phase 5b)
├── docs-reconciliation.md             # Phase 5b: per-doc overlap + status table
├── promotion-path/
│   ├── promotion.mmd
│   ├── promotion-corporate-light.svg
│   ├── promotion-corporate-dark.svg
│   └── report.md
├── environment-matrix/{matrix.mmd, *.svg, report.md}
├── configuration-provenance/{provenance.mmd, *.svg, report.md}
├── recovery-rollback/{recovery.mmd, *.svg, report.md}
├── 2026-05-16.html                    # automatic, compile-html.sh
└── 2026-05-16.pdf                     # opt-in only, compile-pdf.sh
```

## Strict citation policy

Read `references/citation-protocol.md` before authoring any diagram. Summary:

- Every node carries a callout ID and either a `path:line` citation or an `eve-mcp:<tool>:<query>` citation.
- Every edge carries a citation.
- Synthesized concepts are visually distinct in the diagram (`classDef synthesized stroke-dasharray:5`) and listed separately in the report. Cap: ≤20% per mode.
- Every report carries a verification log of what was discarded and why.
- **Release-specific rule**: configuration override-order claims must be confirmed by reading the resolution mechanism, not inferred from filename ordering. **Release-specific rule**: cloud topology claims preferentially cite eve-mcp queries when available.

Fabricated citations are the dominant failure mode for diagram-first analysis. The verification phase is the load-bearing part of this skill — do not skip it.

## Resources

- `references/citation-protocol.md` — strict citation rules, eve-mcp citation format, synthesized cap
- `references/verification-protocol.md` — orchestrator's mechanical verification pass with eve-mcp hooks
- `references/subagent-dispatch.md` — agent/model matrix, prompt templates, ingested-findings handoff
- `references/mermaid-conventions.md` — diagram types, callout prefixes, classDef rules
- `references/report-template.md` — per-mode `report.md` skeleton
- `references/synthesis-readme.md` — top-level `README.md` template (incl. Authoritative in-tree docs and Provenance sections)
- `references/docs-reconciliation.md` — Phase 5b protocol: reading in-tree runbooks, dispatching `doc-claim-validator`, release-specific procedure-precedence rule
- `references/mode-promotion-path.md`
- `references/mode-environment-matrix.md`
- `references/mode-configuration-provenance.md`
- `references/mode-recovery-rollback.md`
- `scripts/render.sh` — render `*.mmd` to `*.svg` via `mmdc`
- `scripts/compile-html.sh` — combine reports into a single self-contained styled HTML via pandoc
- `scripts/compile-pdf.sh` — combine reports into a single PDF via pandoc
- `scripts/verify-citations.sh` — quick path:line existence check over a report
- `assets/template.html` — pandoc HTML template
- `assets/styles/{corporate,blueprint}/` — stylesheet + mermaid theme JSONs (pass `--style` to `compile-html.sh`)
