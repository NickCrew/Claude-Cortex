---
name: mapping-suite
description: User-triggered orchestrator that walks the user through running multiple sibling mapping/audit/doc skills against a shared scope, then assembles their outputs into one navigable artifact. Coaches rather than auto-runs — at each step the orchestrator presents the next sibling skill, recommended scope inheritance, and approval gate; the user invokes the sibling and confirms before moving on. Resolves the prior arch-analysis lookup once at suite start so every sibling skill inherits the same scope. Records each run's output path in a suite manifest. Produces a combined navigation HTML that links to each sibling's standalone HTML for one-stop sharing. Ships two named recipes — "release-driver onboarding" (for tooling that drives releases) and "deployed-system onboarding" (for systems that get deployed) — and supports custom plans. Trigger on "run our mapping suite," "do a complete onboarding," "build the combined report," "I need to onboard to system X," "give me the full picture of this codebase," or when the user names two-or-more sibling analyses to coordinate. Not for running a single sibling skill in isolation (invoke it directly), and not for bypassing approval gates (this skill coaches, never autoruns).
keywords:
  - mapping suite
  - complete onboarding
  - combined report
  - full picture
  - release-driver onboarding
  - deployed-system onboarding
  - coordinate analyses
---

# Mapping Suite

## Overview

You have a small library of skills that map, audit, and document a system from different angles — `architectural-analysis`, `release-analysis`, `wiring-audit`, `doc-claim-validator`, `doc-completeness-audit`, etc. They share conventions (`docs/<skill>/<date>/`, mermaid + cited reports, cross-skill callout reuse, `--style corporate` HTML output) and they share a common prior: a recent `architectural-analysis` run is the foundational artifact most of the others can build on.

Coordinating them by hand means resolving the same scope four times, threading the same prior through four different Phase 0 lookups, and ending up with four standalone HTMLs to share. This skill owns the coordination so you don't.

The skill is a **coach, not an autorunner**. At each step it presents:

1. The next sibling skill in the recipe.
2. The scope it should inherit (resolved once at suite start).
3. The recommended invocation.
4. An approval gate.

You invoke the sibling. The orchestrator records what landed and proposes the next step.

## When to use

Trigger this skill when:

- You want a complete onboarding artifact for a system you don't already know — release-engineer onboarding, on-call rotation prep, knowledge transfer.
- You name two or more sibling skills to run together — "do an arch-analysis and a release-analysis on this repo."
- You want the combined HTML at the end — one navigable artifact spanning multiple sibling outputs.
- You're staring at a fresh codebase and want a recommended sequence of skills to run.

Do not trigger when:

- You only need one sibling skill — invoke it directly.
- You want autonomous execution — this skill always pauses at approval gates. If you want a hands-off run, run each sibling individually with explicit prompts.
- You're already mid-flight in another orchestration — don't nest mapping-suite inside itself.

## Recipes

A recipe is a named sequence of sibling-skill invocations with recommended scope inheritance. v1 ships two; both are release-engineer-onboarding flavored.

### Recipe 1: release-driver onboarding

**For:** tooling that drives releases for other systems (PowerShell fleet orchestrators, deploy-bot scripts, release-cutting CLIs). The unit of analysis is the *operations* the tool performs, not the tool itself.

**Reader:** a release engineer onboarding to a tool they'll be running.

**Plan:** see `references/recipes/release-driver-onboarding.md`. Summary:

1. **release-analysis** with `scope_shape: driver-only` (or `driver+kube` if the tool also ships itself). Skip arch-analysis prior — the tool isn't a deployed system, so an arch-analysis on it would mostly produce noise.
2. **doc-claim-validator** against the runbooks under `docs/runbooks/`, scoped narrowly. Catches drifted procedures the release-analysis Phase 5b reconciliation flagged but didn't resolve.
3. **Combined HTML** linking both outputs. The release-analysis report is the primary; doc-claim-validator's output is the appendix.

### Recipe 2: deployed-system onboarding

**For:** systems that get deployed (single repo or multi-repo union). The unit of analysis is the system itself.

**Reader:** any new engineer onboarding — release-engineer-flavored but applicable to anyone who needs to read the system end-to-end.

**Plan:** see `references/recipes/deployed-system-onboarding.md`. Summary:

1. **architectural-analysis** with full mode set (or scope-driven subset if the user specifies). Foundational.
2. **release-analysis** layered on the arch-analysis output. Phase 0 inherits scope automatically from the prior README's frontmatter.
3. **wiring-audit** (optional) — runs against the same scope, opportunistically consumes the arch-analysis's UI-surfaces and integrations findings as priors.
4. **Combined HTML** linking all sibling outputs. Architecture-analysis is the primary read; release-analysis is the secondary; wiring-audit (if run) is the appendix.

### Custom plans

The user can name a sequence directly: *"run release-analysis, then doc-completeness-audit, then combined HTML."* The orchestrator treats this as a one-off recipe — same coaching loop, same manifest, same combined-HTML output. No need to formalize it as a stored recipe.

## Workflow

Six phases. Phases 0 and 5 are unique to this skill; phases 1–4 are the coaching loop.

| Phase | Name | Purpose |
|---|---|---|
| 0 | Resolve scope and prior arch-analysis | Same three-tier resolution release-analysis uses. Result is shared with every sibling. |
| 1 | Choose recipe | Named recipe (release-driver onboarding, deployed-system onboarding) or user-defined sequence. |
| 2 | Generate run plan | Sequence of sibling-skill invocations with inherited scope and recommended args. |
| 3 | Coach through the plan | For each step: present, wait for user to invoke, capture output path, update manifest, propose next. |
| 4 | Combine | Run `scripts/compile-combined.sh` against the manifest to produce one navigation HTML. |
| 5 | Hand-off | Recommend next steps based on what each sibling surfaced (e.g., "doc-claim-validator flagged 3 drifted runbooks — want to invoke doc-maintenance?"). |

### 0. Resolve scope and prior arch-analysis (one-time)

Same three-tier resolution as `release-analysis`'s Phase 0:

1. **User-supplied path** (preferred) — *"run mapping-suite for `~/source/source-control-automation` building on `~/source/docs/architecture/2026-05-16/`."* Skip search.
2. **Search well-known locations** — `<cwd>/docs/architecture/*/` and `<cwd>/../docs/architecture/*/`.
3. **Ask** — when both miss.

Parse the prior README's frontmatter:

- `scope`, `target_repo`, `modes`, `date`.

Propose the inherited scope to the user. Confirm before proceeding.

If no prior arch-analysis exists *and* the recipe needs one (deployed-system onboarding does; release-driver onboarding doesn't), this is the first decision point: run arch-analysis first, or proceed without prior context. Ask.

Persist the result to `docs/<suite-date>-suite/suite-scope.md`:

```markdown
---
suite_date: 2026-05-18
recipe: release-driver-onboarding
scope: source-control-automation
target_repo: ~/source/source-control-automation
prior_arch_analysis: none (recipe doesn't require one)
eve_mcp_used: true
---
```

### 1. Choose recipe

Present the recipes:

```
Two recipes are available. Which fits this run?

1. release-driver onboarding — for tooling that drives releases for other systems
2. deployed-system onboarding — for systems that get deployed

Or describe a custom sequence.
```

If the user named a recipe in the trigger, skip the prompt and confirm: *"Running release-driver onboarding. Plan: release-analysis + doc-claim-validator + combined HTML. Sound right?"*

### 2. Generate run plan

Read `references/recipes/<recipe>.md` for the recipe-specific plan. The plan is a list of steps; each step has:

- Skill name.
- Scope (typically inherited from suite-scope.md).
- Recommended invocation prompt.
- Approval gate description.
- Expected output path (used to populate the manifest).

Write the plan to `docs/<suite-date>-suite/suite.yaml` per `references/suite-manifest.md`. Initialize all steps with `status: pending`.

### 3. Coach through the plan

For each step in order:

1. **Present.** Show the user:
   - Step number and skill name.
   - Why this step (one sentence).
   - The recommended invocation prompt (verbatim, as a code block they can copy).
   - What output to expect.
2. **Wait for user invocation.** The user runs the sibling skill themselves via `Skill` tool or by typing the prompt. The orchestrator does not auto-invoke.
3. **Capture output.** Once the sibling finishes, ask the user for the output path (or detect it via `find docs/<skill>/*/`). Validate the path resolves to a directory containing the expected artifacts (per the recipe's `expected output path`).
4. **Update manifest.** Mark the step `completed`, record the path. If the user skipped the step, mark `skipped` with a note.
5. **Propose next.** *"Step 1 done. Next: doc-claim-validator. Proceed?"*

If a step fails (sibling skill errored, user hit a blocker), mark `failed` in the manifest with the error reason and present options: retry, skip, or pause the suite. Do not silently retry.

### 4. Combine

When all required steps are completed (or skipped), run:

```bash
bash scripts/compile-combined.sh docs/<suite-date>-suite/
```

This produces `docs/<suite-date>-suite/<suite-date>-suite.html` — a navigation HTML that links to each sibling's standalone HTML in the recommended reading order. Per the v1 design, it's a *shell* (navigation + brief summaries) with *links* to the per-skill HTMLs. No content is inlined; each sibling HTML stays canonical.

Pass `--banner <path>` to add a header banner.

If a sibling skill didn't produce HTML output (some doc skills produce only markdown), the navigation links to the markdown report instead.

### 5. Hand-off

Survey the sibling outputs and propose next-step skills:

- **`doc-claim-validator` flagged drifted claims** → recommend `doc-maintenance` to triage.
- **`release-analysis` surfaced gap states with no documented recovery** → recommend the team author runbooks; `doc-completeness-audit` can confirm the coverage gap.
- **`wiring-audit` found broken or stale UI↔backend wires** → recommend addressing the worst severity findings before the next release.
- **Stale ingested arch-analysis** → recommend re-running `architectural-analysis` if findings depended on outdated context.

Do not auto-invoke. Recommend, let the user choose.

## Output layout

```
docs/2026-05-18-suite/
├── suite-scope.md              # Phase 0: one-time scope resolution
├── suite.yaml                  # Phase 2-3: run manifest, status per step
├── 2026-05-18-suite.html       # Phase 4: combined navigation HTML

# Sibling artifacts stay where they live (immutable):
docs/release/2026-05-18/        # release-analysis output
docs/architecture/2026-05-16/   # ingested arch-analysis (untouched)
docs/wiring-audit/2026-05-18/   # if run
```

The suite parent (`<date>-suite/`) is *separate* from each sibling's own dir. Suites are coordination metadata; sibling outputs are the actual reports.

## Scope sharing convention

Every sibling skill that participates in a mapping-suite run reads `docs/<suite-date>-suite/suite-scope.md` for inherited scope. This is the **shared seam** that makes the suite work without each skill re-resolving scope.

Practical implication: when you invoke a sibling under a suite, pass the suite-scope path explicitly:

> "Run release-analysis using the scope at `docs/2026-05-18-suite/suite-scope.md`."

The sibling's Phase 0 / Phase 1 reads it, applies the same target_repo and prior-arch-analysis path the suite resolved, and proceeds. No second confirmation prompt.

For sibling skills that don't yet read suite-scope.md (only release-analysis does so far in v1), the orchestrator passes the scope by repeating it in the invocation prompt. Future siblings can opt into the shared-scope contract.

## Resources

- `references/recipes/release-driver-onboarding.md` — recipe 1 detail
- `references/recipes/deployed-system-onboarding.md` — recipe 2 detail
- `references/suite-manifest.md` — `suite.yaml` schema and lifecycle
- `references/scope-sharing.md` — the suite-scope.md convention sibling skills read
- `scripts/compile-combined.sh` — generate the combined navigation HTML
- `assets/template.html` — pandoc template for the combined HTML (symlink to architectural-analysis's template; same shell, different content)

## What this skill does NOT do

- **Auto-invoke sibling skills.** Always pauses at approval gates.
- **Run a single skill.** Use the sibling directly.
- **Bypass scope resolution.** Phase 0 is mandatory; the suite scope is the seam every sibling consumes.
- **Edit sibling outputs.** Sibling artifacts are immutable; the orchestrator only links to them.
- **Generate findings of its own.** The orchestrator has no opinions about the system being analyzed; it only routes between siblings.
