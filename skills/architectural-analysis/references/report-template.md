# Report Template

The skeleton for each per-mode `report.md`. One file per mode under `docs/architecture/<date>/<mode>/`.

## Structure

Six sections. Order matters — front-loaded so a reader who only skims the first screen still gets the citation table.

```markdown
---
mode: <information | data-flow | integrations | ui-surfaces | data-model | control-flow | failure-modes>
date: <YYYY-MM-DD>
scope: <repo-relative path or "full">
diagram: <primary diagram filename, e.g., ia.mmd>
secondary_diagrams: [<list of optional secondaries>]
synthesized_share: <0.00–1.00>
---

# <Mode Name>

## Summary

<2–4 sentences: what this mode reveals about the codebase. State the headline finding, not a description of the mode itself.>

## Callouts

| ID | Label | Citation | Confidence |
|----|-------|----------|------------|
| <ID> | <label> | <path:line or "—"> | <high \| medium \| synthesized> |

## Narrative

<Prose explanation organized by structural concern. Reference callouts by ID
([I-1], [I-2]) — never re-cite paths inline. The narrative explains the *story*
the diagram tells; the diagram is the artifact, the narrative is the gloss.>

### <Sub-section per architectural cluster>

<...>

## Synthesized concepts

<Only present if any nodes are confidence=synthesized. Otherwise omit the section entirely.>

| ID | Label | Justification |
|----|-------|---------------|
| <ID> | <label> | <why no single file owns this; names ≥2 contributing files with citations> |

## Verification log

<Every per-mode report includes this section. Empty logs are suspicious — a real
verification pass nearly always discards something.>

### Discarded findings

- `<bad citation>` — `<asserted label>` — reason: <e.g., line content didn't match evidence; symbol not found; absence claim refuted by grep at <path:line>>

### Synthesized cap

- Synthesized share: <N>% (cap: 20% for most modes; 35% for interaction patterns)
- <If approached or exceeded cap: explain action taken — promote / drop / escalate>

### Unverified citations

- <Any citations the orchestrator could not resolve and why>

## Open questions

<Architectural questions surfaced by the analysis but not answered by it.
These are seeds for follow-up work, not findings.>

- <question>
```

## Frontmatter fields

- `mode` — the canonical mode slug (matches the directory name).
- `date` — `YYYY-MM-DD` of the report.
- `scope` — what was analyzed: a repo-relative path (`claude_ctx_py/intelligence/`) or `full` for whole-repo.
- `diagram` — filename of the primary mermaid file in this directory.
- `secondary_diagrams` — list of additional `.mmd` files in this directory.
- `synthesized_share` — actual ratio of synthesized to total nodes, computed from the callouts table. Lets the synthesis README aggregate without re-counting.

## Authoring rules

- **One callout, one row.** A callout never appears twice in the callouts table.
- **Cross-mode references in narrative use the original callout.** If the IA report referenced `[D-3]`, the data-flow report's `[D-3]` is the same node — don't re-introduce it as a new callout.
- **Synthesized cells in the citation column show `—`.** The Confidence column says `synthesized`; the Synthesized concepts section carries the justification.
- **No prose claims that aren't backed by a callout.** "The TUI delegates view rendering to ContentSwitcher" must reference `[I-N]` or `[U-N]`. Bare assertions belong in the Open questions section.

## Length

Reports are not exhaustive — they're indexes into the diagram. Most mode reports run 1–3 pages of markdown. If a report exceeds 5 pages, the diagram is probably trying to do too much; consider splitting into a primary + named secondaries.

## Filename

Always `report.md` inside the mode directory. The synthesis README links to `<mode>/report.md`. Don't customize.
