# Word count and character bounds

Verification rubric for FAQ, bios, and social profile bios. Use these bounds when authoring; verify mechanically before closing each doc.

## FAQ.md answers

**Bound: 50–150 words per answer.**

Why these bounds:
- Below 50: the answer is too thin to carry context or reference MANIFESTO sections.
- Above 150: the answer is over-explaining; reader is reading FAQ for a quick reference, not a long-form essay.
- 100 words is the sweet spot for most answers.

Verify with `scripts/word_count.py brand/FAQ.md`.

## BIOS.md — founder bio

**Bound: 50w / 100w / 250w (±5 words).**

| Length | Tolerance | Use for |
|---|---|---|
| 50w | 45–55 | Conference program bios, panel intros, social profile short-bios |
| 100w | 95–105 | Podcast episode descriptions, partnership emails, "about the founder" page sections |
| 250w | 245–255 | Long-form press requests, founder pages, investor decks, deeper podcast intros |

Each version must be independently usable — no "see longer version for context" dependencies.

## BIOS.md — company boilerplate

**Bound: 50w / 100w / 250w (±5 words).**

Same lengths and tolerances as founder bio. Pairs naturally with founder bio at matching lengths (50w founder + 50w company; 250w founder + 250w company). Mismatched pairs (250w founder + 50w company) make one feel padded.

## BIOS.md — social profile bios

| Platform | Char cap | Notes |
|---|---|---|
| Twitter / X bio | ≤ 160 | Standard cap as of writing |
| LinkedIn company tagline | ≤ 120 | Tagline field, not About section |
| LinkedIn personal headline | ≤ 220 | Personal headline (different field) |
| GitHub bio (user / org) | ≤ 160 | User bio cap; org bio may be longer |
| BlueSky bio | ≤ 256 | |
| Mastodon bio | ≤ 500 | Generally lenient |
| Discord status | ≤ 128 | |
| Threads bio | ≤ 160 | |

When in doubt about a current cap, check the platform's documentation. The bound is set conservatively in the templates so a 5–10 char buffer protects against caps tightening.

## Verification script

`scripts/word_count.py` walks a markdown file's headed sections and reports word/char counts:

```bash
python3 scripts/word_count.py brand/FAQ.md
# Output:
#   "What is the product?" — 95 words ✓ (50-150)
#   "Is this auto-apply?" — 162 words ✗ (50-150)  ← over by 12
```

Run before closing FAQ.md / BIOS.md authoring.
