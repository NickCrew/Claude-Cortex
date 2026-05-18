# Docs Reconciliation (Phase 5b)

The institutional fix for the failure mode where this skill duplicates or contradicts existing team runbooks. Release knowledge is heavily runbook-driven — the team has procedures for promoting, rolling back, restarting, and configuring that encode hard-won judgment calls. Mechanism citations alone (the `Set*Version` lever, the `RestartManifest` call) miss the *order* and *prerequisites* that runbooks capture. Reconciliation extracts the value from each.

## Why this is Phase 5b, not Phase 1

Reading docs early anchors the analysis to existing assumptions. The point of the per-mode sub-agents is that they enumerate from code and live platform state without that bias — and they routinely surface things runbooks missed (drift, undocumented overrides, mechanisms the runbook doesn't mention). If the orchestrator preloaded docs, those signals would be suppressed.

Phase 1b *lists* docs without reading them so Phase 5b knows what to reconcile against. Phase 5b reads them only after verified findings exist.

## Inputs

- `docs/release/<date>/docs-inventory.txt` — list of in-tree docs from Phase 1b.
- `docs/release/<date>/doc-map.md` — topic→doc spine. **If ingested from arch-analysis**, this already classifies which doc is authoritative on which subsystem; use it as the prior. Phase 5b's job becomes "extend and verify" rather than "build from scratch."
- All per-mode `report.md` files with verified findings (Phase 5 done).
- Read access to the `doc-claim-validator` skill.

## Workflow

### Step 1 — Read each in-tree doc once

Orchestrator reads, not delegated. Sub-agents lose cross-doc reasoning when context is split.

**If `doc-map.md` was inherited from arch-analysis**, the topic→doc map is already built. Read each doc in the inherited map plus any release-specific additions Phase 1b appended. The map's classifications carry forward; you're confirming them against release-mode findings, not re-classifying from scratch. Watch for `*(stale)*` markers from arch-analysis — those docs are gap targets, not spine.

**If no doc-map was inherited**, build the topic→doc index from the inventory by reading each doc and classifying as you go.

For each doc, scan and note:

- **Title and stated purpose.** What is this doc supposed to explain?
- **Surface covered.** Which mode(s) does this overlap?
  - A `RUNBOOK-deploy.md` overlaps promotion-path.
  - A `recovery-procedures.md` or oncall doc overlaps recovery-rollback.
  - A `aws/<env>-config/README.md` overlaps environment-matrix and configuration-provenance.
  - A `secrets-management.md` overlaps configuration-provenance.
  - A `CHEATSHEET.md` or top-level walkthrough may overlap all four.
- **Concrete claims.** What specific procedures, file paths, environment names, image tags, manifests, or commands does it assert?

Skip:
- `docs/archive/`, `docs/deprecated/` — historical, not current.
- Auto-generated docs (manifest YAML rendered to markdown, etc.).
- `CHANGELOG.md` for older entries — only the latest 1–3 entries are typically relevant.

### Step 2 — Map docs to modes

For each doc, list the modes whose verified findings overlap.

| Category | Definition | Example |
|---|---|---|
| **Single-mode overlap** | Doc covers one analytical mode | A rollback runbook → recovery-rollback only |
| **Multi-mode overlap** | Doc spans modes | `eve-deployment-guide.md` → promotion-path + environment-matrix + recovery-rollback |
| **Out-of-scope** | Doc covers something this analysis didn't address | Capacity planning when scope was promotion topology |

Out-of-scope docs still get a row in the reconciliation table — labeled "adds capability/view" — because the synthesis README should cite them so readers know where to go for the gap.

### Step 3 — Run `doc-claim-validator` per overlapping doc

Use the Skill tool to invoke `doc-claim-validator` for each doc with multi-mode or significant single-mode overlap. Skip for docs that are pure narrative with no verifiable claims.

Pass:
- The doc's path.
- A pointer to the relevant mode reports as priors.
- The `--scope` flag limited to the doc's path.

Capture three buckets per doc:
- **Confirmed** — claims the validator verified against current code or eve-mcp state.
- **Contradicted** — claims that disagree with verified findings; report is right, doc is stale.
- **Unverifiable** — claims requiring human judgment.

### Step 4 — Decide status per doc (with the release-specific rule)

Two distinct status taxonomies operate at different scopes. **Don't conflate them.**

**Doc-level status** — a verdict on the doc as a whole. Applied per-row in the reconciliation table. Asks "is this doc trustworthy on its surface?":

| Doc-level status | When to use | Action |
|---|---|---|
| **In-tree doc supersedes** | Doc covers same surface as a mode with more accuracy or procedural detail | Cite the doc from the relevant mode report's narrative. The report's findings stand but defer to the doc for "what to read first." |
| **Report supersedes** | Most of the doc's claims are contradicted by current code or eve-mcp state; the doc is broadly stale | Flag for the team. Note in `docs-reconciliation.md`; the relevant mode report's Open Questions can name a doc-rewrite recommendation. |
| **Complementary** | Doc and report cover overlapping but distinct surface, both correct | Cite the doc as a "see also." |
| **Adds capability/view** | Doc covers a surface the analysis didn't address (oncall procedures, capacity, customer-facing release notes) | Cite in the synthesis README's Authoritative docs section under "adds capability." |

**Finding-level status** — applied per individual claim during sub-agent enumeration and verification. Distinct from doc-level. A doc can be "In-tree doc supersedes" overall while still containing one or two individual drifted claims. Asks "is this specific claim true?":

| Finding-level status | When to use | Where it lives |
|---|---|---|
| **verified** | Claim resolves and matches the cited source | Mode report callouts table (status column) |
| **drift** | Claim resolves *as a discrepancy* (doc says X, code says Y) | Mode report callouts table (status=drift) and Verification log Drift findings section |
| **synthesized** | No single owning source, ≥2 contributing files | Mode report callouts (status=synthesized) and Synthesized concepts section |
| **discarded** | Citation didn't resolve, evidence didn't match, absence claim was refuted | Verification log only — not in callouts table |

Most reports have **In-tree doc supersedes** at the doc level for several runbooks, *and* a handful of **drift** at the finding level inside those same docs. Both are normal. The reconciliation table records doc-level; per-mode reports record finding-level; the synthesis README's verification summary aggregates finding-level counts.

### Release-specific reconciliation rule

When a runbook describes a **promotion** or **recovery procedure**, the runbook's *ordered procedure* is almost always authoritative — even if the report's mechanism citations are correct on a per-step basis.

Why: a report can correctly cite that `SetManifestVersion(prior)` is the rollback lever and miss that the runbook says **"first pause the cron, then unpin, then re-pin"**. Each step's mechanism is real, but the *prerequisites* and *ordering* live in the runbook. Reports generated from code + live state see the levers but not the reasons one comes before another.

Apply the rule like this:

1. If a doc says "to do X, run A then B then C" and the report cites A, B, and C separately as mechanisms — the doc supersedes. Promote the runbook to authoritative.
2. The report's verified findings still stand as the *catalog* of what mechanisms exist, but the Recovery & Rollback report's procedure list should defer to the runbook: "See `<doc>` for the canonical procedure; the report enumerates underlying mechanisms."
3. If the runbook is missing a mechanism the report found (e.g., references `SetManifestVersion` but never mentions a recently-added `Unpin*` call), surface as **drift** — the runbook is missing a step the report's verification proves exists.
4. If the report is missing prerequisite knowledge the runbook supplies (e.g., "always pause cron first"), the runbook is authoritative on procedure and the report should add a "see runbook" pointer.

This is the most common high-value finding the skill produces. Capture it explicitly.

### Step 5 — Author `docs-reconciliation.md`

Place at `docs/release/<date>/docs-reconciliation.md`. Structure:

```markdown
---
date: YYYY-MM-DD
docs_reviewed: <N>
status_counts: {supersedes: N, report-supersedes: N, complementary: N, adds: N, drift: N}
---

# Docs Reconciliation

## Summary

<2–3 sentences: how much in-tree release documentation exists, how it relates to this analysis, headline take.>

## Reconciliation table

| In-tree doc | Modes overlapped | Status | Notes |
|---|---|---|---|
| docs/X.md | promotion-path, recovery-rollback | In-tree doc supersedes | Authoritative on rollback procedure ordering |
| docs/Y.md | configuration-provenance | Drift | Doc says envs read .env.local; report shows up.sh doesn't pass it |
| ... | ... | ... | ... |

## Per-doc detail

### docs/X.md
- **Modes overlapped:** promotion-path, recovery-rollback
- **Confirmed claims:** N
- **Contradicted claims:** N (with citations showing report is right)
- **Action:** Cited from recovery-rollback/report.md; report defers to doc for procedure ordering. Promotion-path report adds "see also: docs/X.md for the deploy-day runbook."

<repeat per doc>

## Drift findings (highest value)

<Findings flagged as "Report supersedes" or "Drift". Provide both the report's verified citation and the doc's stale claim. These are stale runbooks that should be updated by the team.>
```

### Step 6 — Update synthesis README

Add an "Authoritative in-tree docs" section near the top of `docs/release/<date>/README.md`. Lead with this section. Per-doc rows derived from the reconciliation table. Include a one-paragraph "what this report still adds on top of those" so the report's value is clear.

### Step 7 — Update individual mode reports

For each "In-tree doc supersedes" or "Complementary" status, add one sentence to the relevant mode's Summary or first Narrative paragraph:

> See also: [docs/path/to/doc.md] which is authoritative on [topic].

For recovery-rollback specifically: when a runbook is authoritative on a procedure, the procedure list in the report's supplementary detail should be a *summary* of the runbook with citation, not a re-derivation. The state diagram remains required and authoritative on which states exist; the runbook is authoritative on how to recover from them.

Don't rewrite mode reports around in-tree docs. They serve different purposes — mode reports are falsifiable cited-claim catalogs with cross-mode links; in-tree docs are how the team explains intent and procedure. Keep both.

## Output budget

Phase 5b should run in well under 10% of total skill time. If a project has more than ~20 in-tree docs, batch:

- Run `doc-claim-validator` on the top 5–10 docs with strongest overlap first.
- Bulk-classify the rest (no per-doc validation, just status by metadata).
- Mark the deferred docs with "[deferred]" status in the table.

## Anti-patterns

- **Don't read docs in Phase 1.** Anchors the analysis. Phase 1b only lists; Phase 5b reads.
- **Don't rewrite the report around the docs.** The report's value is the falsifiable catalog of mechanisms and topology. Defer where the doc is more accurate; don't merge.
- **Don't validate every claim.** `doc-claim-validator` is bounded by claim count, not doc count. Run on docs with significant overlap.
- **Don't auto-fix stale runbooks.** Surface them. Fixing requires team context.
- **Don't substitute a runbook reference for the state diagram in recovery-rollback.** The diagram remains required; the runbook supplements it on procedure.
- **Don't skip Phase 5b silently.** If no docs exist, say so in the synthesis README.

## Hand-off to `doc-claim-validator`

When invoking from this phase, pass:

```
Skill: doc-claim-validator
Args: --root <repo-root> --scope <docs/subpath>
Context: The release-analysis skill has produced verified findings under
         docs/release/<date>/. Compare the claims in this doc against:
         - The mode reports under docs/release/<date>/<mode>/report.md
         - Current code at <repo-root>
         - Live platform state via eve-mcp queries (when available)
         Return: confirmed claims, contradicted claims (with which side is right
         based on code / eve-mcp), unverifiable claims.
         Pay special attention to procedural ordering — runbooks that name the
         right steps in the wrong order are a common drift pattern.
```
