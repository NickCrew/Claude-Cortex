# Skill suites: the meta-skill composition pattern

## Problem

The skill library has ~150 skills tagged across 16 categories, and **79% of them
carry more than one category** — the taxonomy is a tag set, not a tree. That makes
the categories useless as a primary organizing axis: there is no single "domain" to
group `accessibility-audit` (security + design + analysis) under, and no rename
scheme can fix that because the skill genuinely serves three domains.

The friction this produces is not "I can't find a skill" — the TUI already groups by
category and the suggestion hook surfaces individual skills. It is: **related skills
that form a natural pipeline are scattered across categories, and there is no first-
class way to run them together against one target and synthesize the result.**

Example: a comprehensive UI/UX review wants `user-journey-mapping` (design),
`ux-review` (design/analysis), `ui-design-aesthetics` (design), and
`interaction-design` (design) run against the same screens, with one prioritized
report at the end. Coordinating that by hand means resolving the same target four
times and stitching four separate outputs.

## Solution: the `-suite` meta-skill

A **suite** is an orchestrator skill that composes two or more sibling skills —
usually cross-category — against a shared target, then synthesizes their outputs.
Composition is the right tool for "related skills in different categories": it cuts
across the taxonomy instead of fighting it. No renames, no recategorization.

Three suite-shaped skills already exist and validate the pattern:

| Skill | Composes | Execution model |
|-------|----------|-----------------|
| `mapping-suite` | `architectural-analysis`, `release-analysis`, `wiring-audit`, `doc-claim-validator`, … | **coach** — manual gate between heavy siblings |
| `doc-health-audit` | `doc-architecture-review`, `doc-claim-validator`, `doc-completeness-audit`, `doc-quality-review` | **autorun, phased** — dependency-ordered, phase-gated |
| `multi-specialist-review` | N parallel review specialists | **autorun, parallel** — fan-out + synthesize |

They use *different* execution models on purpose. That is the central design lesson:
the execution model is chosen per suite from the weight and dependencies of its
siblings, not fixed by the pattern.

## Connection to the `workflow-*` cleanup

The `workflow-bug-fix` / `workflow-feature` / `workflow-performance` /
`workflow-security-audit` skills are **failed suites**: they hardcode a linear phase
list (Analyze → Plan → Implement → Review → Test → Document) but never actually
compose the sibling skills that own each phase. They are a table of contents
pretending to be an orchestrator. The `-suite` pattern is what they were reaching
for. The cleanup deletes them; the roadmap below is where their intent goes to live
properly — e.g. `workflow-security-audit` → `security-review-suite`.

## The reusable parts

Every suite is assembled from the same six components. A new suite is a fill-in-the-
blanks job against this list.

1. **Shared target seam.** Resolve the target *once* (the repo, the running app +
   screens, the module) and persist it to a scope file every sibling inherits. This
   is the seam that stops each sibling re-resolving scope. `mapping-suite` uses
   `docs/<date>-suite/suite-scope.md`.

2. **Lens assignment + dedup.** Each sibling owns one **distinct lens**. Overlapping
   siblings must be scoped down so the synthesis is not three agents reporting the
   same finding. (In the UI/UX suite, `ux-review` already claims to cover interaction
   and a11y, so it is scoped to *heuristics + WCAG only* and `interaction-design` is
   given the *state-coverage* lens.)

3. **Manifest.** Per-step status (`pending` / `completed` / `skipped` / `failed`) so a
   suite run is resumable and auditable. `mapping-suite` uses `suite.yaml`.

4. **Execution model** — the one real design axis:
   - **Coach** — present sibling, user invokes, capture output, gate, next. For
     *heavy* siblings the user wants to inspect between steps (mapping-suite).
   - **Autorun, parallel** — fan out independent siblings, then synthesize. For
     *light, independent* lenses (multi-specialist-review).
   - **Autorun, phased** — run in dependency order with gates. When later siblings
     consume earlier outputs (doc-health-audit).

5. **Synthesis artifact** — two flavors, chosen by what the siblings emit:
   - **Navigation shell** — siblings emit their own standalone HTML; the suite
     produces a linking index (mapping-suite's `compile-combined.sh`).
   - **Authored synthesis** — siblings emit inline findings; the orchestrator writes
     one merged, deduped, prioritized report. The UI/UX suite needs this flavor.

6. **Hand-off** — survey findings and recommend follow-up skills. Never auto-invoke.

## Naming convention

`<domain>-suite` or `<domain>-<verb>-suite`: `mapping-suite`, `ui-ux-review-suite`,
`security-review-suite`, `test-health-suite`. The existing `doc-health-audit` and
`multi-specialist-review` predate the convention and are recognized as suites without
renaming — consistency here is not worth the blast radius (a skill name is referenced
in 8 places including hardcoded slugs in `skill_recommender.py`).

## Roadmap

| Suite | Composes | Model | Status |
|-------|----------|-------|--------|
| `ui-ux-review-suite` | `user-journey-mapping`, `ui-design-aesthetics`, `interaction-design`, `ux-review` | coach | **building** |
| `mapping-suite` | arch/release/wiring/doc siblings | coach | exists |
| `doc-health-audit` | doc-* siblings | autorun, phased | exists |
| `multi-specialist-review` | parallel review specialists | autorun, parallel | exists |
| `security-review-suite` | `threat-modeling-techniques`, `vibe-security`, `security-testing-patterns`, `secure-coding-practices`, `compliance-audit` | coach / phased | candidate — replaces `workflow-security-audit` |
| `test-health-suite` | `test-review`, `test-generation`, `test-guardrails`, `python-testing-patterns` | coach | candidate |
| `release-readiness-suite` | `verification-before-completion`, `release-prep`, `release-analysis`, `finishing-a-development-branch` | coach | candidate |
| `performance-suite` | `performance-analysis`, `python-performance-optimization`, `react-performance-optimization`, `build-optimization` | coach | candidate |

Candidates are ordered by value: `security-review-suite` is highest because it
directly replaces a skill being deleted; `test-health-suite` next because
`test-review` → `test-generation` is already a hand-run pipeline.

## Key decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| Organize by composition, not renaming | Suites | 79% of skills are multi-category; a domain prefix is not derivable |
| Execution model | Per-suite, from sibling weight | The 3 existing suites already diverge; mandating one would be wrong |
| UI/UX suite model | Coach | Lenses are inspection-worthy; consistent with `mapping-suite` |
| Synthesis flavor | Authored report (not nav shell) | UX lenses emit inline findings, not standalone HTML |
| Naming | `<domain>-suite`, don't retro-rename | Name is referenced in 8 places incl. hardcoded Python slugs |
