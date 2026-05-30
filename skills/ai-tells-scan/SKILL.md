---
name: ai-tells-scan
description: "Use when writing tasks produce prose artifacts (READMEs, docs, PR text, tutorials, guides, posts, release notes) and need a fast surface scan for AI tells. Auto-engages on prose writing tasks; checks banned punctuation, stock vocabulary, and mechanical patterns. For the structural judgment pass on rhythm and rhetorical reflexes, use ai-tells-review. Not a replacement for voice skills like nick-voice; this removes machine fingerprints, it does not add a target voice."
tags:
  - writing
  - editing
  - prose
  - documentation
  - ai-tells
triggers:
  - scan for AI tells
  - remove AI tells
  - check prose for AI fingerprints
  - clean generated prose
  - quick AI tell scan
keywords:
  - AI fingerprints
  - generated prose
  - prose scan
  - banned vocabulary
  - punctuation
---

# AI Tells — Surface Scan

A near-mechanical pass that strips the obvious AI fingerprints from prose. Runs before any prose artifact is presented as final.

## When This Runs

Auto-engages whenever the task produces prose-as-artifact:

- READMEs, CONTRIBUTING, CHANGELOG
- Technical documentation under `docs/`
- PR descriptions, PR comments, commit message bodies
- Tutorials, guides, blog posts, release notes
- Any markdown intended for human readers

Skip for: code comments (different rules), inline chat replies, structured data (YAML/JSON), or anything pure-config.

## How To Use

After drafting prose, scan it once against each list below. Every match is a rewrite, not a debate. The lists are deliberately short and high-leverage — if a tell isn't here, it belongs in `ai-tells-review`.

---

## Banned Punctuation

- **Em dashes connecting clauses.** Replace with period, comma, colon, or parentheses depending on the relationship. The em dash is the single most diagnostic AI tell in prose.
- **Smart quotes when the source is plain ASCII.** Mixing curly and straight quotes in a doc is a copy-paste fingerprint.
- **Ellipses for dramatic pause** in technical writing (`it's...complicated`). Reads as performance.

## Banned Sentence Openers

- "Importantly," "Notably," "Crucially," "Interestingly"
- "Furthermore," "Moreover," "Additionally"
- "It's worth noting that…" / "It bears mentioning…"
- "In essence," "Ultimately," "At its core"
- "In conclusion," "To summarize," "In summary"
- "Great question!" or any sycophantic acknowledgement

If the sentence after the opener stands on its own, delete the opener. It almost always does.

## Banned Vocabulary

These words appear far more often in machine-generated prose than human prose. Each has a fix-direction.

| Word / Phrase | Why it's a tell | Fix direction |
|---|---|---|
| `delve` | Diagnostic on its own | use `look at`, `examine`, or just delete |
| `leverage` (verb) | Corporate-AI fingerprint | use `use` |
| `robust`, `comprehensive`, `seamless`, `streamlined` | Empty positive adjectives | name the specific property |
| `cutting-edge`, `innovative`, `state-of-the-art` | Marketing puff | describe what it actually does |
| `elegantly`, `seamlessly`, `gracefully` | Empty positive adverbs | delete the adverb |
| `modulo` (in non-math prose) | Claude tic | use `except for` or `aside from` |
| `stakeholders` | Generic abstraction | name the people or roles |
| `passionate about`, `excited to`, `thrilled to` | Performative enthusiasm | state what was done |
| `it's worth noting` | Throat-clearing | delete; state the thing |
| `at the end of the day` | Verbal filler | delete |
| `move the needle`, `circle back`, `align on` | Corporate cliche | name the actual action |

## Banned Structural Reflexes (Surface Layer)

These are mechanical enough to catch on a scan; deeper rhythm/structure tells live in `ai-tells-review`.

- **Tricolon reflex.** Three-item lists by default ("fast, reliable, and scalable"). If two items would do, use two. If five, use five.
- **"This is not X — it's Y" contrastive bold.** The mirrored "Why not pure JSON: / Why not pure scriptblocks:" pattern. Delete the contrast or merge into a single sentence.
- **Decision-stamp formality.** `**Decided 2026-05-18:**` style headers in personal notes. Real humans rarely formalize their own decisions like a court ruling.
- **Self-narration.** Sentences that comment on what the doc is doing: "That's the dashboard's reason for existing." / "(this is where we start)". Delete and let the doc do the thing instead of describing itself.
- **Compliment sandwich.** Soften → criticize → soften. State the criticism directly.
- **Three consecutive sentences saying the same thing in different words.** Delete two of them.

## Banned Visual Reflexes

- **ASCII art boxes for layered diagrams.** When the diagram is more than two boxes, use mermaid or just describe the layers in prose.
- **Italicized rhetorical emphasis.** *missing*, *separately*, *on this dashboard*. Italics are for terms-of-art and titles, not tone. One per long doc, max.
- **Bold for emphasis on every paragraph.** Bold should mark scannable structure (headers, key terms), not feeling.

## Coined-Phrase Tic Check

Before submitting, scan for any minted phrase repeated 3+ times across the doc. Examples seen in real artifacts: "proves the framework," "earns its place," "5-second glance." Humans usually rephrase the second or third use; models don't. Rephrase all but the first occurrence.

---

## What This Skill Does Not Do

- Catch rhythm patterns (uniform sentence length, paragraph-level parallelism, gerund cascade)
- Catch hedging cadence and manufactured both-sidesing
- Catch aphoristic closers and summary-of-summary endings
- Replace voice skills like `nick-voice` — this subtracts machine fingerprints, it doesn't add personality

For all of the above, use `ai-tells-review`.

## Output Shape

The scan is invisible by default — it runs before the prose is presented and the prose comes out clean. If a tell can't be cleanly fixed (e.g. the contrastive-bold pattern is load-bearing for the argument), flag it inline:

> NOTE: kept "X — Y" construction at line 42; the contrast carries the argument and rewriting flattens it.

This gives the user one place to check whether to push back on a specific judgment.
