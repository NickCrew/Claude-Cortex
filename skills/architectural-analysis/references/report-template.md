# Mode Report Template (doc-led, gap-first)

The skeleton for each per-mode `report.md`. The new shape treats in-tree docs as the spine: confirms collapse into a "Doc reference" details block, drift sits prominently, gaps drive the narrative.

## Structure

Six sections. Order matters — front-load the doc reference, lead the narrative with gaps and drift, hide the receipts.

```markdown
---
mode: <information | data-flow | integrations | ui-surfaces | data-model | control-flow | failure-modes>
date: <YYYY-MM-DD>
scope: <repo-relative path or "full">
diagram: <primary diagram filename, e.g., ia.mmd>
spine_docs: [<list of in-tree docs this mode leads with — empty list if greenfield>]
synthesized_share: <0.00–1.00>
verified_count: <integer>
drift_count: <integer>
gap_count: <integer>
---

# <Mode Name>

## Summary

<One paragraph. Lead with the spine doc(s):

- "Per `<DOC.md>`, <one-sentence claim>. This report verifies that against
  the code (N callouts), surfaces M drift items, and identifies K
  undocumented behaviors."

If there's no spine doc:

- "No in-tree doc covers this mode. This report is the documentation."

End with one sentence pointing readers at what's worth their time —
typically the Gaps section or the Drift section if either is non-empty.>

![](<diagram-name>.png)

## Doc reference (collapsed) {#doc-reference}

<details class="receipts">
<summary>Doc reference — <DOC.md> verified against code</summary>

<Brief excerpt or restatement of the spine doc's authoritative claim
(2-4 sentences). The full doc is the source of truth; this excerpt
exists so the reader doesn't have to leave the report to know what
the doc says.>

| Doc claim | Code citation | Status |
|-----------|---------------|--------|
| <claim from the doc> | <path:line> | confirms |
| <claim from the doc> | <path:line> | confirms |

</details>

## Drift

<Only present if any drift findings. Never collapsed.

For each drift item:

### <short title>

- **Doc claim** (`<DOC.md>:<line-or-section>`): <quoted or paraphrased>
- **Code reality** (`<path:line>`): <what the code actually does>
- **Impact**: <who is affected if they trust the doc>
- **Recommendation**: update the doc / update the code / file a follow-up>

## Gaps

<The narrative section. The most-read part of the report.

Each gap has a callout id and a short paragraph. Group by theme if there
are many; otherwise just list them.

### <gap title>

[<G-id>] <one-paragraph explanation: what the code does, why it's worth
knowing, why no doc covers it. Cite path:line(s).>

If a gap is severe enough that someone might break it without knowing,
mark it with `{.danger}` (rendered as a red banner in the HTML).>

## Receipts (collapsed) {#receipts}

<details class="receipts">
<summary>Callouts table</summary>

| ID | Label | Citation | Class | Confidence |
|----|-------|----------|-------|------------|
| <ID> | <label> | <path:line or "—"> | confirms \| drift \| gap \| extends | high \| medium \| synthesized |

</details>

<details class="receipts">
<summary>Synthesized concepts</summary>

<Only emit if any nodes are confidence=synthesized.>

| ID | Label | Justification |
|----|-------|---------------|
| <ID> | <label> | <why no single file owns this; ≥2 contributing files cited> |

</details>

<details class="receipts">
<summary>Verification log</summary>

### Discarded findings

- `<bad citation>` — <reason>

### Synthesized cap

- Synthesized share: <N>% (cap: 20% for most modes; 35% for interaction patterns)

### Unverified citations

- <Any citations the orchestrator could not resolve and why>

</details>

## Open questions

<Architectural questions surfaced by the analysis but not answered by it.>

- <question>
```

## Authoring rules

- **The Summary line names the spine doc.** No exceptions; if there's no spine doc, say so explicitly. Readers should know within the first sentence whether to trust the doc or the report.
- **Confirms collapse, drift and gaps don't.** A reader scrolling through the HTML should see drift and gap content immediately and be able to expand confirms only if they want to verify the spine.
- **Drift is rare and expensive.** Each drift item costs a doc edit somewhere. Be conservative — only flag drift when the doc explicitly says X and the code does Y.
- **Gaps drive synthesis.** Each gap finding here feeds the synthesis README's "Undocumented behaviors" section. Mark gaps with the `{.danger}` class only when ignorance is materially risky (security boundary, data integrity, fail-open default).

## Diagram conventions

The diagram still shows the structural picture. Add classes for the new finding types — **stroke-width and stroke-dasharray only, no colors** (theme-aware fills come from `mermaid-config.json`):

```mermaid
classDef synthesized stroke-width:1px,stroke-dasharray:5
classDef drift stroke-width:2px
classDef gap stroke-width:2px,stroke-dasharray:3
```

A drift edge: `A -.->|drift: doc says X| B`. A gap node: nodes at the boundary of documented territory get `class N gap`. See `references/mermaid-conventions.md` for the full classDef catalog.

## Length

Mode reports should be **shorter** than the previous template. Most of the descriptive content used to live in the Narrative section; that content is now in the spine doc itself. The new Narrative is just gaps + drift, which is naturally shorter for well-documented codebases.

If a report exceeds 4 pages of markdown, the diagram is probably trying to do too much; split into a primary + named secondaries.

## Filename

Always `report.md` inside the mode directory.
