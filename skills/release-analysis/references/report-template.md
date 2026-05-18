# Report Template

The skeleton for each per-mode `report.md`. One file per mode under `docs/release/<date>/<mode>/`.

## Structure

Six sections. Order matters — front-loaded so a reader who only skims the first screen still gets the citation table.

```markdown
---
mode: <promotion-path | environment-matrix | configuration-provenance | recovery-rollback>
date: <YYYY-MM-DD>
scope: <repo-relative path or "full" or list of paths>
scope_shape: <compose-only | kube-only | driver-only | compose+kube | driver+compose | driver+kube | all-three>
diagram: <primary diagram filename, e.g., promotion.mmd>
secondary_diagrams: [<list of optional secondaries>]
synthesized_share: <0.00–1.00>
drift_count: <integer — number of findings classified as drift in this mode>
ingested_from: <path to prior arch-analysis README, or "none">
---

# <Mode Name>

## Summary

<2–4 sentences: what this mode reveals about the release process. State the headline finding, not a description of the mode itself.>

## Callouts

| ID | Label | Citation | Status |
|----|-------|----------|--------|
| <ID> | <label> | <path:line or eve-mcp:tool:query or "—"> | <verified \| drift \| synthesized> |

**Status semantics:**
- **verified** — claim resolves and matches the cited source.
- **drift** — claim resolves *as a discrepancy*: two sources disagree (doc vs. code, snapshot vs. live state, runbook vs. mechanism). The discrepancy itself is verified. Drift findings are first-class output. List both sides of the disagreement in the row's evidence or in the Narrative.
- **synthesized** — no single owning source. Cell shows `—` in citation column; justification in the Synthesized concepts section.

Findings that fail to resolve are not listed here; they appear in the Verification log under "Discarded findings."

Cross-skill references (callouts ingested from prior architectural-analysis):

| ID | Origin | Label | From |
|----|--------|-------|------|
| [C-17] | control-flow | depends_on cascade | docs/architecture/2026-05-16/ |

## Narrative

<Prose explanation organized by structural concern. Reference callouts by ID — never re-cite paths inline.>

### <Sub-section per release concern>

<...>

## Synthesized concepts

<Only present if any nodes are confidence=synthesized.>

| ID | Label | Justification |
|----|-------|---------------|
| <ID> | <label> | <why no single source owns this; ≥2 contributing files or queries with citations> |

## Verification log

<Always present. Empty logs are suspicious.>

### Drift findings

<Per-mode list of drift findings (status=drift in the callouts table). Each names both sides of the discrepancy.>

- [<callout-id>] `<label>` — Side A: <claim, citation>; Side B: <conflicting claim, citation>. Resolution: <which side is right, or "ambiguous, surface to team">.

### Discarded findings

- `<bad citation>` — `<asserted label>` — reason: <...>

### Synthesized cap

- Synthesized share: <N>% (cap: 20%)
- <If approached or exceeded: action taken>

### Eve-mcp fallbacks

- <Cloud-side claims that fell back to repo-side citations because eve-mcp was unavailable, or partially unavailable>

### Unverified citations

- <Any citations the orchestrator could not resolve and why>

## Open questions

<Release questions surfaced by the analysis but not answered.>

- <question>
```

## Frontmatter fields

- `mode` — canonical mode slug (matches directory name).
- `date` — `YYYY-MM-DD` of the report.
- `scope` — what was analyzed.
- `scope_shape` — precise shape combination from Phase 1 detection: `compose-only`, `kube-only`, `driver-only`, `compose+kube`, `driver+compose`, `driver+kube`, or `all-three`. Determines which signal sets applied. Avoid the older `hybrid` value — name the combination.
- `diagram` — primary mermaid filename.
- `secondary_diagrams` — list of additional `.mmd` files.
- `synthesized_share` — actual ratio of synthesized to total nodes.
- `drift_count` — number of findings classified as drift in this mode. Surfaces in the synthesis README's verification summary table.
- `ingested_from` — path to prior arch-analysis README if Phase 0 ingested, else "none".

## Authoring rules

- **One callout, one row.**
- **Cross-skill references in narrative use the original callout ID.** A `[C-17]` from an ingested arch-analysis report stays `[C-17]` — don't re-introduce it as a new release-analysis callout.
- **Cross-skill references appear in their own sub-table** under the main callouts table, naming the originating mode and report.
- **Synthesized cells in the citation column show `—`.**
- **No prose claims that aren't backed by a callout.**
- **Cite the resolution mechanism, not the inferred order.** For configuration-provenance findings especially: cite the `up.sh` line that orders compose files, not the directory listing.

## Length

Most release-analysis mode reports run 1–4 pages of markdown. Recovery & rollback reports run longer when many recovery procedures are documented (each procedure is its own sub-section). If a report exceeds 6 pages, consider splitting the diagram into a primary + named secondaries.

## Filename

Always `report.md` inside the mode directory.
