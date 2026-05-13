---
name: doc-quality-review
description: Assess documentation quality across readability, consistency, audience fit, and prose clarity. Produces a scored review with actionable findings. This skill should be used before releases, during doc reviews, or when documentation feels unclear or inconsistent.
version: 1.0.0
tags:
  - documentation
  - review
  - quality
  - readability
  - consistency
triggers:
  - review doc quality
  - is this doc well-written
  - doc readability
  - documentation consistency
  - improve doc quality
  - prose review
dependencies:
  skills: []
  tools:
    - Read
    - Grep
    - Glob
    - Agent
token_estimate: ~3500
keywords:
  - doc quality
  - prose quality
  - readability
  - doc
  - quality
  - review
  - doc quality review
---

# Documentation Quality Review

Assess whether documentation is well-written, consistent, and appropriate for its
audience. The output is a scored review with specific findings — not rewrites.

## When to Use

- Before releases — ensure docs meet a quality bar
- During doc review — structured alternative to "looks good to me"
- When users report docs are confusing, inconsistent, or too technical
- After bulk doc generation — verify machine-written docs read naturally
- Periodic quality check on documentation health

## Quick Reference

| Resource | Purpose | Load when |
|----------|---------|-----------|
| `references/personas.md` | Six concrete reader personas with quality signals | Always (Phase 1) |
| `references/quality-dimensions.md` | Doc-type-aware scoring rubrics for each dimension | Always (Phase 1) |
| `references/style-checklist.md` | Concrete style rules for common issues | Phase 2 (review pass) |

---

## Workflow Overview

```
Phase 1: Scope       → Identify docs to review and their intended audience
Phase 2: Review      → Score each doc across quality dimensions
Phase 3: Synthesize  → Aggregate findings, identify patterns
Phase 4: Report      → Produce the scored quality review
```

---

## Phase 1: Scope the Review (with persona discovery)

Before reviewing, establish context. **Persona discovery is foundational** —
without it, scoring applies a generic standard that systematically
misjudges docs whose audience differs from default. A reference doc that
serves API Looker-Up reads as "too terse" against a generic readability
rubric; against the right persona, that terseness is the goal.

1. **Identify the docs** — which files or sections are in scope?
2. **Identify the doc type** per file — reference, tutorial, guide,
   explanation, ADR, runbook, or README. (Use the type → default
   persona mapping in `references/personas.md`.)
3. **Identify the personas** — which 1–3 personas from
   `references/personas.md` are the primary readers per doc? When the
   doc type strongly suggests a persona, prefer that default unless
   the doc itself shows evidence of a different audience.
4. **Note conflicts** — when one doc legitimately serves multiple
   personas with different needs (e.g., a CLI reference serves both
   API Looker-Up and Operator), capture this. Per-persona scoring
   surfaces conflicts in the report.
5. **Load the rubrics** — `references/quality-dimensions.md` is now
   doc-type-aware. Each dimension has different 5/5 criteria per type.

### Output of Phase 1

A scope manifest:

```yaml
docs:
  - path: <path>
    type: reference | tutorial | guide | explanation | ADR | runbook | README
    primary_persona: <persona name from library>
    secondary_persona: <if applicable>
    conflict_notes: <if multiple personas with different needs>
```

This manifest feeds Phase 2's per-docfile sonnet dispatch.

---

## Phase 2: Review Each Document (per-docfile sonnet dispatch)

Scoring 5 weighted dimensions across many docs strains an orchestrator's
context window — reading 50+ docs sequentially blows up the budget and
sequential scoring is slow. Dispatch one `general-purpose` + `sonnet` agent
per docfile. Each agent receives:

- The full doc content
- The rubric from `references/quality-dimensions.md`
- The style checklist from `references/style-checklist.md`
- Audience and doc-type metadata established in Phase 1
- The dimension weighting table for the doc type

Each agent returns scores + specific findings for that one doc.

### Dispatch parameters

```
subagent_type: "general-purpose"
model: "sonnet"
description: "Quality review for <docfile>"
```

Run dispatches in parallel batches of 4–8 (memory-aware) until all docs are
scored. The orchestrator collects results and proceeds to Phase 3 synthesis.

### Per-docfile prompt template

```
Score the document at <DOCFILE_PATH> across five quality dimensions,
calibrated to the persona(s) and doc type identified in Phase 1.

Doc metadata (from Phase 1 scope manifest):
- doc type: <reference | tutorial | guide | explanation | ADR | runbook | README>
- primary persona: <persona name>
- secondary persona: <if applicable>

Personas (verbatim from references/personas.md):
<INLINE FULL PERSONA PROFILE — do not summarize. Each profile is the
five-field structure plus the "evaluates positively / negatively"
lists. The agent calibrates against these signals.>

Doc-type-aware rubric (verbatim from references/quality-dimensions.md):
<INLINE the relevant per-doc-type criteria for each dimension. Specifically:
- The "5/5 looks like" example for this doc type
- The "common readability failure" / equivalent rows for this type
- The score table rows for this type>

Style checklist (from references/style-checklist.md):
<inline relevant style rules>

Dimension weighting for this doc type:
<INLINE the row from the weighting table>

Universal flags:
<INLINE the universal flag table>

Process:
1. Read the full document.
2. For each of the 5 dimensions, score against THIS doc type's rubric
   (not a generic standard). When the rubric says a dimension applies
   differently or N/A for this doc type, follow the rubric — do not
   apply a default.
3. Score per-persona when multiple personas are listed. Identify
   places where one persona scores high and another low; surface the
   conflict explicitly rather than averaging.
4. List specific findings per dimension with location, issue, fix.
5. Apply the weighting; report the weighted total per persona.

Output as YAML:

doc_path: <path>
doc_type: <...>
personas_evaluated: [<persona1>, <persona2>]
per_persona_scores:
  <persona1>:
    readability:    { raw: N, justification: "...", evidence: "verbatim quote with line ref" }
    consistency:    { raw: N, justification: "...", evidence: "..." }
    audience_fit:   { raw: N, justification: "...", evidence: "..." }
    structure:      { raw: N, justification: "...", evidence: "..." }
    actionability:  { raw: N, justification: "...", evidence: "..." }
    weighted_total: N
  <persona2>:
    ...
findings:
  - severity: critical | major | minor
    dimension: readability | consistency | audience_fit | structure | actionability
    affected_persona: <which persona this hurts most>
    location: "L42 or '## Section heading'"
    issue: "..."
    fix: "..."
persona_conflicts:
  - dimension: <which>
    description: "Doc favors <persona A> via <pattern>, costs <persona B> in <way>"
    recommendation: "<resolution: split doc, add structure for both, accept bias intentionally>"
strengths:
  - persona: <which>
    evidence: "<specific passage worth emulating for this persona>"

Critical: do NOT apply a generic 'good doc' standard. Apply the rubric
for THIS doc type and persona. A reference doc with no Quick Start is
correctly structured for its persona, not a deficiency. A runbook with
no background context is correctly structured under incident pressure,
not "missing explanation." Score against the rubric you were given.

Optimize for accuracy over volume. Cite specific lines or sections —
generic findings ("prose is dense") without location aren't actionable.
```

### Why sonnet, not haiku

Quality scoring across 5 dimensions requires reading the full doc *and*
holding the rubric + style rules + audience expectations in mind
simultaneously. Haiku's excerpt reads + smaller context window strain on
this combination. Sonnet handles the dimension juggling reliably; haiku
tends to score by pattern-match (long sentences → low readability) without
the calibration the rubric requires.

The cost trade-off: ~50 sonnet calls for a 50-doc set vs. one big haiku
call. Per-docfile sonnet is cheaper than per-claim sonnet (where the count
multiplies with claims) and produces substantially more reliable scores.

### Scoring dimensions

Score each document across the five dimensions below. The agent prompt above
inlines this table so the dispatched agent doesn't have to load the file.

### Dimension 1: Readability

How easily can the target audience read and understand this?

| Score | Criteria |
|-------|----------|
| 5 | Clear, concise prose. Short paragraphs. Active voice. Appropriate vocabulary for audience |
| 4 | Generally clear. Minor instances of passive voice, long sentences, or unnecessary jargon |
| 3 | Readable but effortful. Multiple long paragraphs, some jargon without definition, occasional ambiguity |
| 2 | Difficult. Dense prose, heavy jargon, passive constructions, unclear antecedents |
| 1 | Impenetrable. Wall of text, undefined terms, ambiguous instructions, no structure |

**What to check:**
- Sentence length — flag sentences over 30 words
- Paragraph length — flag paragraphs over 6 sentences
- Passive voice density — flag sections where >40% of sentences are passive
- Jargon — flag technical terms used without definition on first occurrence
- Ambiguous pronouns — "it", "this", "that" without clear referent
- Nominalizations — "perform an installation" instead of "install"

### Dimension 2: Consistency

Does this doc use the same terms, formatting, and conventions throughout — and
match the rest of the doc set?

| Score | Criteria |
|-------|----------|
| 5 | Consistent terminology, formatting, heading style, code block conventions, and tone throughout |
| 4 | Minor inconsistencies (e.g., "config" vs "configuration" in different sections) |
| 3 | Noticeable inconsistencies across sections but each section is internally consistent |
| 2 | Frequent inconsistencies in terminology, formatting, or conventions |
| 1 | No discernible consistency — reads like it was written by different people at different times |

**What to check:**
- Term alignment — same concept should use the same word everywhere
- Heading hierarchy — consistent use of `##` vs `###`, capitalization style
- Code block formatting — language tags present, consistent indentation
- List formatting — bullet vs number, punctuation, capitalization
- Admonition/callout style — consistent use of note/warning/tip conventions
- Tense — consistent within a doc type (imperative for instructions, present for descriptions)

### Dimension 3: Audience Fit

Is the content calibrated to the right level for its intended readers?

| Score | Criteria |
|-------|----------|
| 5 | Perfectly pitched. Prerequisites stated. Appropriate depth. No unexplained leaps |
| 4 | Mostly well-calibrated. Occasional assumption of knowledge not established |
| 3 | Uneven. Some sections too basic, others too advanced. Prerequisites unclear |
| 2 | Significant mismatch. Beginner docs assume expert knowledge, or expert docs over-explain basics |
| 1 | Wrong audience entirely. Content pitched at a different reader than intended |

**What to check:**
- Prerequisite assumptions — what must the reader already know?
- Explanation depth — does it match the audience's expected background?
- Context gaps — would a new reader understand *why*, not just *what*?
- Leaps — does the doc jump from basic to advanced without transition?
- Condescension — does it over-explain things the audience already knows?

### Dimension 4: Structure & Scannability

Can a reader find what they need without reading linearly?

| Score | Criteria |
|-------|----------|
| 5 | Logical heading hierarchy. Scannable sections. Tables for reference data. Clear entry points |
| 4 | Good structure. Minor issues with heading granularity or section ordering |
| 3 | Adequate structure but some sections are too long or headers don't reflect content |
| 2 | Poor structure. Key information buried in prose. Headings misleading or inconsistent |
| 1 | No useful structure. Single long section with no headings, or headings that don't help navigation |

**What to check:**
- Heading hierarchy — does it create a useful outline?
- Front-loading — are key facts early in each section, or buried at the end?
- Tables vs prose — is reference data in tables or hidden in paragraphs?
- Section length — flag sections over 500 words without a subheading
- TL;DR — do long docs have a summary or overview section?

### Dimension 5: Actionability

Can the reader *do something* after reading? (Weighted differently by doc type.)

| Score | Criteria |
|-------|----------|
| 5 | Clear next steps. Commands are copy-pasteable. Examples are complete and runnable |
| 4 | Mostly actionable. Minor gaps in examples or steps |
| 3 | Partially actionable. Some instructions unclear or missing context |
| 2 | Weakly actionable. Reader knows *about* the topic but not *how* to apply it |
| 1 | Not actionable. Pure description with no path to action |

**What to check:**
- Code examples — do they work if copy-pasted? Are imports included?
- Commands — are they complete with required flags and paths?
- Steps — are they sequential and numbered? Any missing steps?
- Expected output — does the doc show what success looks like?
- Error guidance — if something goes wrong, does the doc say what to do?

### Dimension Weighting by Doc Type

| Dimension | Reference | Tutorial | Guide | Explanation | README |
|-----------|-----------|----------|-------|-------------|--------|
| Readability | 1.0 | 1.2 | 1.2 | 1.3 | 1.2 |
| Consistency | 1.2 | 0.8 | 1.0 | 0.8 | 1.0 |
| Audience Fit | 0.8 | 1.3 | 1.2 | 1.2 | 1.3 |
| Structure | 1.3 | 1.0 | 1.0 | 0.8 | 1.0 |
| Actionability | 1.0 | 1.5 | 1.3 | 0.5 | 1.0 |

---

## Phase 3: Synthesize Findings (orchestrator-side)

After Phase 2's per-docfile sonnet calls return, the orchestrator aggregates
results across the doc set. Synthesis stays orchestrator-side because it
needs the full result set — no individual agent has that view. Look for
patterns:

- **Systemic issues** — same problem across many docs (e.g., inconsistent terminology everywhere)
- **Outliers** — one doc much better or worse than the rest
- **Audience mismatches** — docs in the wrong section for their actual audience
- **Style drift** — sections written at different times with different conventions

Systemic issues are more valuable to fix than individual ones — fixing the pattern fixes
many docs at once.

---

## Phase 4: Produce the Quality Review

### Report Format

```markdown
# Documentation Quality Review

**Review date:** YYYY-MM-DD
**Scope:** [files or sections reviewed]
**Personas evaluated:** [comma-separated list]
**Doc types in scope:** [reference, tutorial, guide, explanation, ADR, runbook, README]

---

## Personas

[Inline the Phase 1 persona blocks — full profile per persona]

---

## Summary

[2-3 sentences: overall quality assessment with explicit persona context]

Per-persona aggregate scores (averaged across in-scope docs of each
type, weighted per the doc-type weighting table):

| Persona | Readability | Consistency | Audience Fit | Structure | Actionability | Weighted Total |
|---------|-------------|-------------|--------------|-----------|---------------|----------------|
| <persona A> | N/5 | N/5 | N/5 | N/5 | N/5 | N/25 |
| <persona B> | N/5 | N/5 | N/5 | N/5 | N/5 | N/25 |

Quality grade per persona: [A (22-25) / B (18-21) / C (14-17) / D (10-13) / F (<10)]

When grades differ between personas, that's a finding — surface in the
"Persona Conflicts" section below. Don't average away the divergence.

---

## Findings

### Critical (must fix before publish)

| # | File | Dimension | Issue | Fix |
|---|------|-----------|-------|-----|
| 1 | [path:line] | [dimension] | [specific problem] | [specific fix] |

### Major (should fix)

| # | File | Dimension | Issue | Fix |
|---|------|-----------|-------|-----|

### Minor (nice to fix)

| # | File | Dimension | Issue | Suggestion |
|---|------|-----------|-------|------------|

---

## Systemic Issues

### [Issue pattern name]
**Affected docs:** [list]
**Dimension:** [which]
**Pattern:** [what's happening across docs]
**Recommended fix:** [one-time fix that addresses all instances]

---

## Persona Conflicts

[For docs serving multiple personas where scoring diverges significantly.
Each entry identifies which persona the current structure favors and what
the cost is for the other persona(s).]

| Doc | Favors | At cost of | Recommendation |
|-----|--------|------------|----------------|
| [path] | [persona] | [other persona] | [split / restructure / accept bias intentionally] |

---

## Per-Document Scores

| Document | Persona | Read. | Cons. | Aud. | Struct. | Action. | Weighted Total |
|----------|---------|-------|-------|------|---------|---------|----------------|
| [path] | [persona A] | N | N | N | N | N | N |
| [path] | [persona B] | N | N | N | N | N | N |

---

## Strengths

[What's working well — cite specific examples worth emulating]
```

---

## Integration with Other Doc Skills

```
doc-maintenance         →  Structural health (links, orphans, folders)
doc-claim-validator     →  Semantic accuracy (do claims match code?)
doc-completeness-audit  →  Topic coverage (is everything documented?)
doc-quality-review      →  Prose quality (is it well-written?)
doc-architecture-review →  Information architecture (is it findable?)
```

---

## Anti-Patterns

- Do not rewrite docs during the review — produce findings, not rewrites
- Do not score without reading the full document — skimming misses context
- Do not apply tutorial standards to reference docs or vice versa — use the weighting table
- Do not penalize technical precision as "jargon" in docs for technical audiences
- Do not flag style preferences as quality issues — "I'd phrase it differently" is not a finding
- Do not review generated API docs (JSDoc, Sphinx auto) — review the source comments instead
- Do not score docs in `docs/archive/` — they are historical

---

## Bundled Resources

### References
- `references/quality-dimensions.md` — Detailed scoring rubrics with examples for each score level
- `references/style-checklist.md` — Concrete style rules for the most common quality issues
