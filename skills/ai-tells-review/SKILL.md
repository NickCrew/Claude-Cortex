---
name: ai-tells-review
description: "Use when public prose still sounds machine-written after ai-tells-scan. Complements ai-tells-scan's mechanical pass with structural judgment: rhythm, hedging, rhetorical reflexes, and performative emphasis. Trigger on 'review for AI tells,' 'does this read AI,' 'strip the AI smell,' or 'make this less AI.'"
tags:
  - writing
  - editing
  - prose
  - documentation
  - ai-tells
  - review
triggers:
  - review for AI tells
  - does this read AI
  - strip the AI smell
  - still reads AI after scan
  - structural prose review
  - rewrite AI-sounding prose
keywords:
  - AI smell
  - structural review
  - prose rhythm
  - rhetorical reflexes
  - hedging
---

# AI Tells — Structural Review

A judgment-based pass that catches the subtle tells the surface scan misses. Cite each finding, name the family, suggest a fix-direction. Then offer to rewrite.

## When To Use

- Public-facing artifacts: READMEs, shipped docs, blog posts, release notes
- Technical writing where the prose itself is the deliverable
- After `ai-tells-scan` has already stripped the obvious tokens
- When a draft "reads AI" but you can't articulate why
- Before publishing anything Nick wouldn't want attributed to a machine

Skip when: the artifact is internal-only and nobody cares, or the user only wants the mechanical pass (`ai-tells-scan` is enough).

## Workflow

1. **Read the artifact end to end.** Don't pattern-match line by line yet. Get the rhythm and shape first.
2. **Run the four-family rubric** below. For each tell found, note: line(s), family, why it reads as a tell, fix-direction.
3. **Produce the findings report** in the structure under "Output Shape."
4. **Offer the rewrite** explicitly: "Want me to do a pass that fixes these?"
5. **If yes, rewrite preserving structure and content.** Don't change what the doc is saying — change how it's saying it.

The user can stop at the report. Don't rewrite without explicit consent.

## The Four-Family Rubric

### 1. Structural Reflexes

Default shapes the model reaches for regardless of fit.

- **Aphoristic closer.** Sentence trying to land like a punchline at the end of a section. Examples: "Premature alerts produce numbness." / "the auditor is always ahead." / "No artefact, no promotion." _Fix-direction:_ end on the substantive point, not the epigram.
- **Definitional opener.** Every section starts "X is a Y that…" even when X was already established. _Fix-direction:_ start with the action or the question instead.
- **Echo paragraph.** Paragraph N+1 restates paragraph N with synonyms. _Fix-direction:_ delete one. Usually the second.
- **Summary-of-summary closer.** "In essence…" / "Ultimately…" wrapping up what was just said. _Fix-direction:_ delete the closer; the section already ended.
- **Over-signposting.** "There are three things to consider. First…" when headers already do this. _Fix-direction:_ delete the meta-narration.
- **Self-narration.** Prose commenting on what the doc is doing: "That's the dashboard's reason for existing." / "(this is where we start)" inside a diagram. _Fix-direction:_ let the doc do the thing instead of describing itself.
- **Decision-stamp formality.** `**Decided 2026-05-18:**` court-ruling style in personal notes. _Fix-direction:_ drop the stamp; state the decision in prose.
- **Labeled callback scheme.** Q1–Q6, Layer 1/2/3, deliberately numbered cross-refs in a doc that didn't need them. _Fix-direction:_ use names, not numbers; let prose carry the references.

### 2. Tonal Hedging

The model softens and balances by default, regardless of whether the topic warrants it.

- **Manufactured both-sidesing.** "However" / "That said" inserted to fake balance the topic doesn't need. _Fix-direction:_ state the position; delete the hedge.
- **"Worth noting" filler.** Hedge phrases delaying the actual claim. _Fix-direction:_ delete and lead with the claim.
- **Reassuring middle.** "This is normal / expected / fine" inserted where no one was worried. _Fix-direction:_ delete unless the reader is genuinely likely to be alarmed.
- **Equivocation-as-wisdom.** "It depends" expanded into a fake decision framework. _Fix-direction:_ if there's a real answer, give it. If it depends, name the _one or two_ axes that actually matter.
- **Earnest-explainer parentheticals.** "(verified 2026-05-18)" / "(modulo any drift)" / "(per CLAUDE.md)" cross-refs everywhere. _Fix-direction:_ trust the reader; integrate critical context into the sentence or delete the parenthetical.

### 3. Performative Emphasis

Signaling importance instead of being clear.

- **Concept-puffing.** Capitalizing ordinary words to make them feel like Concepts. _Fix-direction:_ lowercase unless it's a proper noun or term-of-art.
- **Empty positive adverbs.** "elegantly," "seamlessly," "gracefully" attached to verbs. _Fix-direction:_ delete the adverb. If the property matters, name it.
- **Performative TL;DR.** "Short answer:" decorating a response that wasn't long. _Fix-direction:_ delete the label; the answer is the answer.
- **Aspirational close.** Ending on what _could_ / _might_ be done — forward-looking platitude. _Fix-direction:_ end on what was done, or on the next concrete step.
- **Contrastive bold.** "This is not X — it's Y" / mirrored "Why not pure JSON: / Why not pure scriptblocks:" sections. _Fix-direction:_ state the position directly. Delete the foil unless someone actually argued for it.
- **Italicized rhetorical emphasis.** Italics on ordinary words for tone, not for terms. _Fix-direction:_ delete italics; if emphasis is essential, restructure the sentence.

### 4. Rhythm Patterns

The cadence itself is the tell.

- **Uniform sentence length.** Paragraphs where every sentence lands at ~15 words. _Fix-direction:_ combine two short sentences into one long one, or break a long one into two short ones. Vary deliberately.
- **Gerund cascade.** "Building on this… Taking this further… Considering these factors…" _Fix-direction:_ rewrite as concrete actions with subjects.
- **Paragraph-level parallelism.** Every paragraph opens with the same grammatical shape. _Fix-direction:_ vary the openers — start one with a question, one with the subject, one with the verb.
- **Coined-phrase tic.** A minted phrase repeated 3+ times across the doc ("proves the framework" / "earns its place" / "5-second glance"). _Fix-direction:_ keep the first use; rephrase the rest.
- **Tricolon cadence at scale.** Not just one three-item list — every list is three items, every emphasized sentence has three clauses. _Fix-direction:_ break the pattern. Use twos and fours when they fit.

---

## Output Shape

Produce the report in this structure. Cite line numbers when feasible.

```markdown
# AI Tells Review: <doc-name>

**Verdict:** <reads-clean | minor-tells | reads-AI | reads-very-AI>

## Findings

### Family 1: Structural Reflexes

- **Line 42** — Aphoristic closer: "Premature alerts produce numbness."
  _Fix-direction:_ end the section on the substantive point about alert volume, not the epigram.
- **Line 88** — Self-narration: "That's the dashboard's reason for existing."
  _Fix-direction:_ delete; the preceding paragraph already established this.

### Family 2: Tonal Hedging

- **Line 17, 34, 61** — Earnest-explainer parentheticals: "(per CLAUDE.md)", "(modulo any drift)", "(verified 2026-05-18)"
  _Fix-direction:_ drop all three. If timestamps matter, put them in a footer; otherwise delete.

### Family 3: Performative Emphasis

- **Line 12** — Contrastive bold: "This is not a generic 'service health' dashboard — every panel earns its place..."
  _Fix-direction:_ lead with what the dashboard is, not what it isn't.

### Family 4: Rhythm Patterns

- **Throughout** — Coined-phrase tic: "proves the framework" appears 3 times in rows 1, 2, and 5.
  _Fix-direction:_ keep the first; rephrase the second and third.

## Summary

<2-3 sentence assessment of which families dominate and what kind of pass would help most>

## Offer

Want me to do a rewrite pass that addresses these? I'll preserve structure
and content; only the prose changes.
```

## Rewrite Constraints

If the user accepts the rewrite offer:

- **Preserve all structural elements.** Headings, code blocks, tables, lists — leave the skeleton alone.
- **Preserve all factual claims.** Don't add new content; don't drop content. Only rephrase.
- **Preserve technical precision.** Don't soften "FIPS 140-2 compliant" into "secure"; don't turn "Postgres 14" into "the database."
- **Vary cadence deliberately.** If the original was uniform, mix sentence lengths. If parallel, vary openers.
- **Show the diff at the end.** Brief summary of what changed and why, organized by family. Not a line-by-line; a 3-5 bullet summary.

## What This Skill Does Not Do

- Replace `ai-tells-scan` for the surface pass (run that first, or accept that obvious tells will appear in the report).
- Add a target voice. For voice work (Nick's voice, brand voice), use `nick-voice` or the brand's voice skill after this pass.
- Verify factual claims. Use `doc-claim-validator` for that.
- Critique information architecture or completeness. Use `doc-architecture-review` or `doc-completeness-audit`.

This skill subtracts machine fingerprints. That's the whole job.
