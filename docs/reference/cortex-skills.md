# Cortex Custom Skills

The skills built into Cortex — distinct from the 100+ ecosystem skills the
package bundles. These are first-party, designed and maintained as part of the
framework, and define how Cortex itself wants you to work.

> **16 custom skills** covering implementation workflows, codebase analysis,
> documentation health, quality review, and authoring. For the broader curated
> view across all installed skills, see the [Skill Showcase](skill-showcase.md).

---

## At a glance

| Skill | Category | Use when |
|-------|----------|----------|
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

Drives all work through atomic commits — each loop operates on the smallest
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
memory, no cached priors — the response is genuinely independent.

**Use when:** Stuck on a tough call and want a second opinion, or comparing
how different models approach the same problem.

---

### `verification-before-completion`

**Evidence before assertions, always.**

Run verification commands and confirm output *before* claiming work is
complete, fixed, or passing — before committing, before opening PRs, before
saying "done." Prevents the common failure mode of asserting success based on
intent rather than result.

**Use when:** About to mark a task complete, push a commit, or open a PR.

---

## Codebase analysis & audit

Two skills for understanding existing code: `architectural-analysis` produces
descriptive diagrams (what's there); `wiring-audit` produces prescriptive
findings (what's wrong). They compose — the audit can consume an analysis
report as priors to skip rediscovery.

### `architectural-analysis`

**Diagram-first codebase analysis with strict `path:line` citations across 8 modes.**

Eight modes (information architecture, data flow, integration points, UI
surfaces, interaction patterns, data model, control flow, failure modes), each
producing a mermaid diagram plus cited markdown report under
`docs/architecture/<date>/`. Every node and edge resolves to a citation;
synthesized concepts capped per mode (20% standard, 35% for interaction
patterns where the bands-vs-tabs decision lives across multiple files).
Parallel haiku/sonnet sub-agents per mode; orchestrator runs mechanical
citation verification before any node lands in a diagram. Optional
self-contained HTML output with embedded SVGs and base64-embedded banner.

**Use when:** "Diagram this codebase," "map the architecture," "show data
flow," "give me an ERD," "trace control flow," "audit the UX architecture."

---

### `wiring-audit`

**Surface vs capability drift detection for React + any backend.**

Diffs a project's consumed surface (UI fetch calls, hooks, tRPC clients, server
actions, GraphQL queries) against its produced capability (route handlers,
exported hooks, tRPC routers, GraphQL fields). Eight finding categories with a
severity rubric (broken / drifted / mediated / stale / gap) and explicit
calibration for cycle-coupled persistence patterns (e.g.,
regenerate-with-current-state, form library state, URL-as-state, batched
mutations).

**Use when:** "Audit our wiring," "find UI/backend drift," "find unwired
capabilities," "find unused endpoints," "stale surfaces."

---

## Documentation health

Six skills for keeping documentation honest and complete. `doc-health-audit`
orchestrates the others into a phase-gated full audit; the rest can be run
independently for narrower passes.

### `doc-architecture-review`

**Information architecture for documentation.**

Evaluates navigation paths, discoverability, progressive disclosure,
cross-linking, and mental-model alignment. Surfaces structural problems
(e.g., "this section is unreachable from the landing," "concept X is
introduced after concept Y that depends on it").

**Use when:** Restructuring docs, adding new sections, or when users report
difficulty finding information.

---

### `doc-claim-validator`

**Validate that doc claims match codebase reality.**

Extracts verifiable assertions (file paths, commands, function references,
behavioral claims, dependencies) from markdown and checks them against the
actual project. Catches drift between docs and code that grows quietly during
refactors.

**Use when:** After code changes, before releases, or when documentation feels
untrustworthy.

---

### `doc-completeness-audit`

**Map doc gaps by topic, not by file.**

Compares what a doc set *should* cover against what it *actually* covers,
producing a prioritized gap report organized by topic. Catches missing pages,
shallow pages, and topics covered redundantly across multiple files.

**Use when:** After shipping features, before releases, or when users report
missing documentation.

---

### `doc-health-audit`

**Full 5-dimension doc audit, phase-gated.**

Orchestrates a complete audit across structural health, semantic accuracy,
topic completeness, prose quality, and information architecture — running
each phase in dependency order with phase gates so a failed earlier phase
short-circuits later ones.

**Use when:** Pre-release audits, periodic health checks, or comprehensive
documentation assessments. Bundles `doc-architecture-review`,
`doc-claim-validator`, `doc-completeness-audit`, and `doc-quality-review`.

---

### `doc-maintenance`

**Systematic audit and maintenance with sub-agent dispatch.**

Prescribes folder structure for `docs/` and `manual/`, dispatches haiku
sub-agents for codebase/doc scanning, and routes doc creation to specialized
agents (reference-builder, technical-writer, learning-guide) with
docs-architect as quality gate.

**Use when:** Documentation may be stale, missing, or misorganized — after
feature work, refactors, dependency upgrades, or as a periodic health check.

---

### `doc-quality-review`

**Score readability, consistency, audience fit, and prose clarity.**

Produces a scored review with actionable findings. Distinct from
`doc-architecture-review` (which evaluates structure) — this one evaluates
the *prose itself*.

**Use when:** Before releases, during doc reviews, or when documentation feels
unclear or inconsistent.

---

## Quality review

Two specialized review skills outside the doc-* family.

### `test-review`

**Test quality and coverage audit, producing a prioritized gap report.**

Pipelines testing standards into the audit workflow. The output is a *report*,
not code — the skill explicitly does not write test implementations until the
report is reviewed, so you triage gaps before authoring fixes.

**Use when:** Reviewing existing tests, auditing test gaps, or assessing test
health before writing new tests.

---

### `html-seo-review`

**Static HTML SEO audit for on-page signals and crawlability.**

Audits static HTML for on-page SEO, content quality, easy-win performance
signals, and crawlability. Static HTML only — does not cover Jekyll / Hugo /
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

- **`agent-loops` + `atomic-commits` + `verification-before-completion`** — the
  implementation triad. The loop drives commits; commits stay atomic;
  verification gates every "done" claim.
- **`architectural-analysis` + `wiring-audit`** — analysis produces priors that
  the audit consumes, so the audit's enumerators skip rediscovery (~50% time
  saving when a recent snapshot exists).
- **`doc-health-audit`** orchestrates `doc-architecture-review`,
  `doc-claim-validator`, `doc-completeness-audit`, and `doc-quality-review`
  with phase gating.

## Beyond these 16

Cortex bundles 100+ ecosystem skills covering broader domains (security,
performance, frontend, databases, etc.). Browse the curated highlights in the
[Skill Showcase](skill-showcase.md) or the full discovery mechanism via
`cortex skills list`.
