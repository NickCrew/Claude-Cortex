# Synthesis README

The top-level `docs/release/<date>/README.md`. Indexes all per-mode reports, resolves cross-mode and cross-skill references, and records what was ingested from the prior architectural-analysis run.

## Structure

```markdown
---
date: <YYYY-MM-DD>
scope: <repo-relative path or "full" or list of paths>
scope_shape: <compose-only | kube-only | driver-only | compose+kube | driver+compose | driver+kube | all-three>
modes: [<list of modes included>]
target_repo: <repo name or path>
ingested_from: <path to prior arch-analysis README, or "none">
eve_mcp_used: <true | false | partial>
---

<!-- scope_shape values:
     compose-only / kube-only / driver-only — single shape
     compose+kube / driver+compose / driver+kube — two shapes (e.g., a driver tool that ships itself via Compose)
     all-three — driver tool that also ships itself via both Compose and Kube
     Match the precise combination detected in Phase 1; "hybrid" is too vague. -->


# Release Analysis — <YYYY-MM-DD>

## Scope

<1–2 sentences: what was analyzed, what shape (compose / kube / hybrid), what was excluded.>

## Authoritative in-tree docs

<Lead with this section so readers go to the canonical doc first. Built from
docs-reconciliation.md (Phase 5b). Omit only if no in-tree docs exist — note
the absence explicitly.>

This analysis was reconciled against the in-tree release documentation. Where
these overlap with mode reports, **the in-tree doc usually wins** — runbooks
encode procedural knowledge (ordering, prerequisites, judgment calls) that
mechanism citations don't capture. Treat this report as a complement
(cross-system synthesis, gap-finding, falsifiable catalog of mechanisms) rather
than a replacement.

| In-tree doc | Authoritative on | This report's overlapping section | Status |
|---|---|---|---|
| <path/to/runbook.md> | <topic> | <mode references> | <In-tree doc supersedes / Complementary / Adds capability/view / Drift> |

What this report still adds on top of those:

- <bullet — typically: live-platform-state verification, falsifiable mechanism catalog, cross-environment drift detection, gap states with no documented recovery, cross-skill links to architectural-analysis findings>

## Provenance

<This section is unique to release-analysis. It records the relationship to a prior architectural-analysis run, if any.>

- **Ingested from:** <path to prior README, or "none — proceeded without prior context">
- **Ingest age:** <N days, or N/A>
- **Ingested callouts:** <count of [I-N], [C-N], [F-N], [X-N] callouts referenced from this run>
- **Eve-mcp:** <available | unavailable | partial — note any tools that failed>

If `ingested_from: none`, briefly note what context was missing and how this affected the report's depth.

## Modes included

- **[Promotion path](promotion-path/report.md)** — <one-line headline finding>
- **[Environment matrix](environment-matrix/report.md)** — <…>
- **[Configuration provenance](configuration-provenance/report.md)** — <…>
- **[Recovery & rollback](recovery-rollback/report.md)** — <…>

## Cross-mode index

<Every callout that's referenced from a different mode than its origin, including ingested arch-analysis callouts.>

| Callout | Origin mode | Also referenced from | Label |
|---------|-------------|----------------------|-------|
| [R-5] | promotion-path | recovery-rollback | schema migration job |
| [E-2] | environment-matrix | configuration-provenance | namespace: crm-services-prod |
| [C-17] | (arch-analysis: control-flow) | promotion-path, recovery-rollback | depends_on cascade |
| [F-13] | (arch-analysis: failure-modes) | configuration-provenance, recovery-rollback | WAF off when not enabled |

## Headline findings

<3–6 bullets summarizing the most release-significant findings across modes. These are conclusions a reader should leave with, not summaries of each mode.>

1. <Cross-cutting finding referencing callouts from multiple modes — e.g.,
   "Promotion to prod has no automated gate beyond CI [R-2]; rollback requires
   pause-cron-then-unpin [V-7] which isn't documented in any runbook.">
2. <…>

## Verification summary

| Mode | Findings | Verified | Drift | Discarded | Synthesized | Synthesized share | Eve-mcp citations | File citations |
|------|----------|----------|-------|-----------|-------------|-------------------|-------------------|----------------|
| Promotion path | 18 | 16 | 1 | 1 | 2 | 11% | 6 | 11 |
| Environment matrix | 24 | 21 | 3 | 0 | 0 | 0% | 18 | 6 |
| Configuration provenance | 22 | 18 | 1 | 3 | 4 | 18% | 4 | 18 |
| Recovery & rollback | 16 | 15 | 0 | 1 | 3 | 19% | 7 | 9 |

**Column semantics:**
- **Verified** — claim resolves and matches the cited source. The standard "this is true" outcome.
- **Drift** — claim resolves *as a discrepancy*. The finding documents that two sources disagree (doc vs. code, snapshot vs. live state, runbook vs. mechanism); the discrepancy itself is verified, even though one side is wrong. Drift findings are first-class output, not failures.
- **Discarded** — citation didn't resolve, evidence didn't match, or absence claim was refuted. Listed in per-mode verification log.
- **Synthesized** — no single owning source; meets the cap of ≤20% per mode.

A finding is counted in exactly one of Verified / Drift / Discarded / Synthesized.

## Diagrams

- [Promotion path](promotion-path/promotion.svg) | [Sequence — multi-actor](promotion-path/sequence.svg) (optional)
- [Environment matrix](environment-matrix/matrix.svg)
- [Configuration provenance](configuration-provenance/provenance.svg)
- [Recovery & rollback](recovery-rollback/recovery.svg)

## Open questions

<Aggregated open questions across all per-mode reports, de-duplicated.>

- <question>

## Methodology note

This report was generated by the `release-analysis` skill. Every node and edge in every diagram is grounded in either a `path:line` citation or an `eve-mcp:<tool>:<query>` citation, with the exception of clearly-marked synthesized concepts (capped at 20% per mode).

<If ingested_from is non-empty:>
This run layers on top of the architectural-analysis report at `<path>`. Ingested callouts are referenced by their original IDs (`[I-N]`, `[C-N]`, `[F-N]`, `[X-N]`) and are not re-derived here. Cross-skill references appear in each per-mode report's callouts table under "Cross-skill references."

<If eve_mcp_used is true or partial:>
Cloud-side topology and version-pinning claims were verified against eve-mcp queries (`ShowChannels`, `GetManifest`, `ShowDeploymentCrons`, `GetAuditRecords`). Where eve-mcp was unavailable, claims fell back to repo-side citations and are noted in each per-mode report's "Eve-mcp fallbacks" verification subsection.

Fabricated citations were filtered by the verification protocol; see each per-mode report's "Verification log" for what was discarded.
```

## Authoring sequence

1. Write each per-mode `report.md` first.
2. Run Phase 5b (docs reconciliation per `references/docs-reconciliation.md`) — produces `docs-reconciliation.md` and updates per-mode reports with "see also" pointers.
3. Aggregate into the synthesis README:
   - Walk every report's callouts table.
   - Build the cross-mode index, including cross-skill (ingested arch-analysis) references.
   - Build the **Authoritative in-tree docs** section from `docs-reconciliation.md`.
   - Sum the verification stats.
   - Tally eve-mcp vs. file citations per mode.
4. Write the **Provenance** section explicitly — record what was ingested from arch-analysis, when, from where. Load-bearing for trust calibration.
5. Write headline findings *last* — require having read all four reports, the ingested arch-analysis context, and the reconciliation table. Where a finding has been reframed by an in-tree runbook (e.g., "rollback procedure requires cron pause first per runbook X"), reflect that nuance rather than asserting an unqualified mechanism claim.
6. Open questions are de-duplicated from the per-mode reports.

## What NOT to put in the synthesis README

- **Detailed callout tables** — those live in per-mode reports.
- **New findings introduced in synthesis** — every claim in headline findings traces to per-mode callouts or to an authoritative in-tree doc cited from the reconciliation table.
- **Pure summaries of each mode.**
- **Reproduction of arch-analysis findings** — link, don't copy. The Provenance section names what was ingested; the cross-mode index links into the prior report.
- **Reproduction of in-tree runbook content** — link, don't copy. The Authoritative in-tree docs section names what's canonical; readers should follow the link.
