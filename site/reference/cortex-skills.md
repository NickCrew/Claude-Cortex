---
layout: default
title: Cortex Custom Skills
parent: Reference
nav_order: 2
---

# Cortex Custom Skills

The skills built into Cortex --- distinct from the 100+ ecosystem skills the
package bundles. These are first-party, designed and maintained as part of the
framework, and define how Cortex itself wants you to work.
{: .fs-6 .fw-300 }

> **16 custom skills** covering implementation workflows, codebase analysis,
> documentation health, quality review, and authoring. For the broader curated
> view across all installed skills, see the [Skill Showcase]({% link reference/skills.md %}).
{: .note }

---

## At a glance

| Skill | Category | Use when |
|:------|:---------|:---------|
| [`agent-loops`](#agent-loops) | Implementation | Starting any implementation task |
| [`atomic-commits`](#atomic-commits) | Implementation | Working tree has mixed uncommitted work |
| [`multi-llm-consult`](#multi-llm-consult) | Implementation | Second opinion from Gemini / Codex / Qwen |
| [`verification-before-completion`](#verification-before-completion) | Implementation | About to claim work is done |
| [`architectural-analysis`](#architectural-analysis) | Analysis | Diagramming a codebase across 8 modes |
| [`wiring-audit`](#wiring-audit) | Analysis | Finding UI/backend drift |
| [`doc-architecture-review`](#doc-architecture-review) | Documentation | Restructuring docs IA |
| [`doc-claim-validator`](#doc-claim-validator) | Documentation | Verifying doc claims against code |
| [`doc-completeness-audit`](#doc-completeness-audit) | Documentation | Mapping doc gaps by topic |
| [`doc-health-audit`](#doc-health-audit) | Documentation | Full 5-dimension doc audit |
| [`doc-maintenance`](#doc-maintenance) | Documentation | Stale or drifted docs |
| [`doc-quality-review`](#doc-quality-review) | Documentation | Readability and consistency review |
| [`test-review`](#test-review) | Quality | Test coverage and quality audit |
| [`html-seo-review`](#html-seo-review) | Quality | Static HTML SEO audit |
| [`brand-library-architect`](#brand-library-architect) | Authoring | Building a brand library + press kit |
| [`justfile-author`](#justfile-author) | Authoring | Scaffolding a justfile + Makefile wrapper |

---

## Implementation workflows

The day-to-day code change loop. These four skills compose: `agent-loops`
drives the loop, `atomic-commits` shapes how work lands in git,
`verification-before-completion` is the gate before any "done" claim, and
`multi-llm-consult` is the escape hatch when a second opinion is warranted.

### `agent-loops`

**Complete operational workflow for implementer agents making code changes.**

Drives all work through atomic commits --- each loop operates on the smallest
complete, reviewable change. Defines the Code Change Loop, Test Writing Loop,
Lint Gate, and Issue Filing process with circuit breakers, severity levels, and
escalation rules. Requires `cortex git commit` for all commits. Bundles
provider-aware review scripts that keep same-model shell-outs as the last
resort, plus a fresh-context Codex fallback for code review and test audit.

**Use when:** Starting any implementation task with Codex, Gemini, or another
implementer agent.

---

### `atomic-commits`

**Split a mixed working tree into a sequence of atomic commits.**

Used after a long session, an agent hand-off, a rebase resolution, or any time
`git status` shows mixed work that wasn't committed as it landed. Treats the
working tree as evidence to investigate before grouping. Optimizes for
`git bisect`: each commit is the smallest buildable and deployable unit, and
no smaller. Uses `cortex git commit` for file-level commits and
`cortex git patch --diff` when unrelated changes share a file.

**Use when:** The working tree has accumulated more than one logical group of
changes that need to land as separate commits.

---

### `multi-llm-consult`

**Consult Gemini, Codex, or Qwen for second opinions and delegated work.**

For when the user asks for another model's perspective, wants to compare
answers, or requests delegating a subtask. Distinct from in-conversation
sub-agents because the consulted model runs with fresh context, no shared
memory, no cached priors --- the response is genuinely independent.

**Use when:** Stuck on a tough call and want a second opinion, or comparing
how different models approach the same problem.

---

### `verification-before-completion`

**Evidence before assertions, always.**

Run verification commands and confirm output *before* claiming work is complete,
fixed, or passing --- before committing, before opening PRs, before saying
"done." Prevents the common failure mode of asserting success based on intent
rather than result.

**Use when:** About to mark a task complete, push a commit, or open a PR.

---

## Codebase analysis & audit

Two skills for understanding existing code: `architectural-analysis` produces
descriptive diagrams (what's there); `wiring-audit` produces prescriptive
findings (what's wrong). They compose --- the audit can consume an analysis
report as priors to skip rediscovery.

### `architectural-analysis`

**Diagram-first codebase analysis with strict `path:line` citations across 8 modes.**

Eight modes (information architecture, data flow, integration points, UI
surfaces, interaction patterns, data model, control flow, failure modes), each
producing a mermaid diagram plus cited markdown report under
`docs/architecture/<date>/`. Every node and edge resolves to a citation;
synthesized concepts capped per mode (20% standard, 35% for interaction
patterns where the bands-vs-tabs decision lives across multiple files). Parallel
haiku/sonnet sub-agents per mode; orchestrator runs mechanical citation
verification before any node lands in a diagram. Optional self-contained HTML
output with embedded SVGs and base64-embedded banner.

**Use when:** "Diagram this codebase," "map the architecture," "show data
flow," "give me an ERD," "trace control flow," "audit the UX architecture."

---

### `wiring-audit`

**Surface vs capability drift detection for React + any backend.**

Diffs a project's consumed surface (UI fetch calls, hooks, tRPC clients, server
actions, GraphQL queries) against its produced capability (route handlers,
exported hooks, tRPC routers, GraphQL fields). Eight finding categories with a
severity rubric (broken / drifted / mediated / stale / gap) and explicit
calibration for cycle-coupled persistence patterns (e.g., regenerate-with-
current-state, form library state, URL-as-state, batched mutations).

**Use when:** "Audit our wiring," "find UI/backend drift," "find unwired
capabilities," "find unused endpoints," "stale surfaces."

---

## Documentation health

Six skills for keeping documentation honest and complete. `doc-health-audit`
orchestrates the others into a phase-gated full audit; the rest can be run
independently for narrower passes.

### `doc-architecture-review`

**Persona-aware information architecture review with doc-type-specific rubrics.**

Establishes 1--3 reader personas (from a shared library: Onboarding User,
API Looker-Up, Incident Responder, Architect Debugger, Contributor,
Operator) in Phase 0, then evaluates seven IA heuristics with rubrics that
vary by doc type. Progressive Disclosure correctly scores `N/A` for
reference and ADRs and *inverted* for runbooks, instead of misjudging
flat-by-design docs as "poorly hierarchical." Bundles `scripts/link_graph.py`
for mechanical orphan / reciprocity / broken-link / hub detection; dispatches
sonnet sub-agents per-doc-type for the judgment-heavy parts (Findability,
Cross-Linking, Consistency). Outputs per-persona scores and surfaces
persona conflicts explicitly rather than averaging them away.

**Use when:** Restructuring docs, adding new sections, or when users report
difficulty finding information.

---

### `doc-claim-validator`

**Validate doc claims against codebase reality across 9 claim types.**

Phase 1 deterministically extracts seven claim types via regex (file paths,
commands, code refs, imports, configs, URLs, and *architectural prose* via
verb-anchored patterns like `uses X`, `built with X`, `delegated to X`,
`follows the X pattern`). Phase 2 dispatches AI verifiers: dependency
(haiku, manifest pattern matching), behavioral / architectural / code-example
(sonnet + `general-purpose`, per-docfile batching for full-file traces).
Closes the prior gap where anchorless prose claims slipped through unaudited
and behavioral claims got one undersized haiku call for the whole doc set.

**Use when:** After code changes, before releases, or when documentation feels
untrustworthy.

---

### `doc-completeness-audit`

**Map doc gaps by topic across 5 inventory sources, then sonnet-classify coverage.**

Phase 1 builds the "should exist" inventory from five sources: a
deterministic code-surface script (env vars, CLI commands, config keys,
HTTP endpoints, public exports, error types), user-facing features,
operational surface, existing doc cross-references, and a sonnet
topic-discovery pass for architectural patterns, user flows, migration
paths, and operational runbooks (topics that don't surface as greppable
symbols). Phase 2 maps inventory items to docs via bulk-grep then
per-docfile sonnet dispatch classifying each as Documented / Shallow /
Misplaced / No-real-match. Priority-weights by audience.

**Use when:** After shipping features, before releases, or when users report
missing documentation.

---

### `doc-health-audit`

**Full 5-dimension doc audit, phase-gated.**

Orchestrates a complete audit across structural health, semantic accuracy,
topic completeness, prose quality, and information architecture --- running
each phase in dependency order with phase gates so a failed earlier phase
short-circuits later ones.

**Use when:** Pre-release audits, periodic health checks, or comprehensive
documentation assessments. Bundles `doc-architecture-review`,
`doc-claim-validator`, `doc-completeness-audit`, and `doc-quality-review`.

---

### `doc-maintenance`

**Systematic audit and maintenance with task-calibrated agent dispatch.**

Prescribes folder structure for `docs/` and `manual/`. Phase 1b dispatches
five agents: haiku + `Explore` for pattern enumeration (code-to-doc coverage,
structure compliance, ASCII-diagram detection), sonnet + `general-purpose`
per-docfile for correlation and judgment (doc-to-code freshness verification,
missing-diagram judgment scan). Stale-detection switched from absolute file
age to *code-commits-since-doc-was-touched* --- surfaces docs at risk of
drifting from heavily-churning subtrees and stops flagging stable docs on
stable code. Routes doc creation to specialized agents (reference-builder,
technical-writer, learning-guide) with docs-architect as quality gate.

**Use when:** Documentation may be stale, missing, or misorganized --- after
feature work, refactors, dependency upgrades, or as a periodic health check.

---

### `doc-quality-review`

**Persona-aware prose review with doc-type-specific rubrics.**

Phase 1 identifies 1--3 reader personas per doc (from a shared library:
Onboarding User, API Looker-Up, Incident Responder, Architect Debugger,
Contributor, Operator) and assigns doc types. Phase 2 dispatches one
sonnet agent per docfile with persona profiles inlined and doc-type-specific
rubric cells from `quality-dimensions.md` --- so a reference doc gets
scored against reference criteria (terse, scannable, table-heavy) instead
of generic prose ideals, and a runbook against runbook criteria
(imperative, copy-pasteable, decision-tree shaped). Distinct from
`doc-architecture-review` (structure) --- this one evaluates the *prose itself*.
Reports per-persona scores with explicit conflict surfacing.

**Use when:** Before releases, during doc reviews, or when documentation feels
unclear or inconsistent.

---

## Quality review

Two specialized review skills outside the doc-* family.

### `test-review`

**Test quality and coverage audit, producing a prioritized gap report.**

Pipelines testing standards into the audit workflow. The output is a *report*,
not code --- the skill explicitly does not write test implementations until the
report is reviewed, so you triage gaps before authoring fixes.

**Use when:** Reviewing existing tests, auditing test gaps, or assessing test
health before writing new tests.

---

### `html-seo-review`

**Static HTML SEO audit for on-page signals and crawlability.**

Audits static HTML for on-page SEO, content quality, easy-win performance
signals, and crawlability. Static HTML only --- does not cover Jekyll / Hugo /
Astro / Next.js source, off-page factors, or live-rendered Core Web Vitals.

**Use when:** "Review the HTML for SEO issues," "audit this landing page,"
"check SEO on these pages before I publish."

---

## Authoring

Two skills that build something new (rather than analyze something existing).

### `brand-library-architect`

**Complete brand library: visual identity + documentation set + press kit.**

Builds a visual asset render pipeline, a brand documentation set (BRAND, COPY,
MANIFESTO, BIOS, FAQ, GLOSSARY, TONE, PRICING), open-source convention files
(README, CONTRIBUTING, SECURITY, CODE_OF_CONDUCT), and a self-contained press
kit. Apply phase-by-phase or run end-to-end. Templates are product-agnostic
and use `{{TOKEN}}` placeholders the skill prompts you to fill.

**Use when:** "Build a brand library / brand kit / press kit / brand assets,"
"set up a brand library workflow," or "create a positioning manifesto plus
visual identity."

---

### `justfile-author`

**Scaffold a justfile + Makefile wrapper following Cortex conventions.**

Produces a justfile using zsh syntax with the standard `svc-*` tmux service
family, the canonical build/lint/dev/test recipes, a thin Makefile passthrough
wrapper that auto-installs `just`, and per-service `tx-start.sh` helpers.

**Use when:** "Create a justfile," "add a justfile to this project," "set up
just for...," "wire up tmux services," or "scaffold the task runner."

---

## How these compose

Several Cortex skills are designed to compose:

- **`agent-loops` + `atomic-commits` + `verification-before-completion`** --- the
  implementation triad. The loop drives commits; commits stay atomic;
  verification gates every "done" claim.
- **`architectural-analysis` + `wiring-audit`** --- analysis produces priors that
  the audit consumes, so the audit's enumerators skip rediscovery (~50% time
  saving when a recent snapshot exists).
- **`doc-health-audit`** orchestrates `doc-architecture-review`,
  `doc-claim-validator`, `doc-completeness-audit`, and `doc-quality-review`
  with phase gating.
- **`doc-architecture-review` + `doc-quality-review`** share a personas library
  (`references/personas.md` --- six concrete reader profiles synced between
  the two skills). Both skills score per-persona against doc-type-specific
  rubrics rather than a generic "good doc" standard, which means a flat
  reference doc isn't misjudged as "poorly hierarchical" and a runbook with
  no background isn't misjudged as "missing explanation."
- **Task-calibrated model dispatch** is consistent across the doc-* family:
  haiku + `Explore` for pattern enumeration (manifest scanning, ASCII
  diagram detection, structure compliance); sonnet + `general-purpose`
  per-docfile for multi-file correlation, judgment, and persona-aware
  scoring. The pattern keeps cost tied to doc-set size while ensuring
  judgment-heavy work gets the model that can do it.

## Beyond these 16

Cortex bundles 100+ ecosystem skills covering broader domains (security,
performance, frontend, databases, etc.). Browse the curated highlights in the
[Skill Showcase]({% link reference/skills.md %}) or the full discovery
mechanism via `cortex skills list`.
