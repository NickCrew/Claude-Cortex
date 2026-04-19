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
| `references/quality-dimensions.md` | Scoring rubrics for each dimension | Always (Phase 1) |
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

## Phase 1: Scope the Review

Before reviewing, establish context:

1. **Identify the docs** — which files or sections are in scope?
2. **Identify the audience** — who reads these docs? (new user, experienced developer,
   operator, contributor)
3. **Identify the doc type** — reference, tutorial, guide, explanation, or README?
4. **Load the rubrics** — read `references/quality-dimensions.md` to calibrate scoring

The audience and doc type determine which dimensions matter most. A reference page
has different quality criteria than a tutorial.

---

## Phase 2: Review Each Document

Score each document across five dimensions. Read the full document before scoring.

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

## Phase 3: Synthesize Findings

After scoring individual docs, look for patterns:

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
**Target audience:** [who these docs serve]
**Doc type:** [reference / tutorial / guide / explanation / mixed]

---

## Summary

[2-3 sentences: overall quality assessment]

Overall scores (weighted):
| Dimension | Raw Score | Weight | Weighted |
|-----------|-----------|--------|----------|
| Readability | N/5 | Nx | N |
| Consistency | N/5 | Nx | N |
| Audience Fit | N/5 | Nx | N |
| Structure | N/5 | Nx | N |
| Actionability | N/5 | Nx | N |
| **Total** | | | **N / 25** |

Quality grade: [A (22-25) / B (18-21) / C (14-17) / D (10-13) / F (<10)]

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

## Per-Document Scores

| Document | Read. | Cons. | Aud. | Struct. | Action. | Weighted Total |
|----------|-------|-------|------|---------|---------|----------------|
| [path] | N | N | N | N | N | N |

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
