---
name: html-seo-review
description: Audit static HTML files for on-page SEO, content quality, easy-win performance signals, and crawlability. This skill should be used when the user asks to review, audit, or check the SEO of one or more static HTML files — e.g., "review the HTML for SEO issues", "audit this landing page", "check SEO on these pages before I publish". Static HTML only — does not cover Jekyll/Hugo/Astro/Next.js source, off-page factors, or live-rendered Core Web Vitals.
---

# HTML SEO Review

## Overview

Produce an actionable, severity-ranked findings list for one or more static HTML files. The skill bundles a stdlib-only HTML parser that extracts every SEO-relevant signal into a single JSON document, a comprehensive rubric, and a findings report template — together they let an audit run with predictable output every time.

## When to use

Use when the input is one or more static `.html` files (or a directory of them) and the user wants on-page SEO findings they can act on. Triggers include "SEO review", "SEO audit", "check SEO on this HTML", "review meta tags on this page", "audit on-page SEO".

Do **not** use when:
- The artifact is source for a static-site generator (Jekyll/Hugo/Astro/Eleventy/Next.js). Those need source-aware review; defer to a future `ssg-seo-review` skill.
- The user wants live performance metrics (LCP, CLS, INP). HTML alone cannot produce these; recommend Lighthouse or PageSpeed Insights.
- The user wants backlink, domain authority, or other off-page analysis. That requires third-party tools (Ahrefs, SEMrush, etc.).

## Workflow

### 1. Extract signals

Run the parser against the target. It accepts a single file or a directory (recursive `*.html`):

```bash
python3 scripts/extract_seo_signals.py <path> --pretty
```

Output is a JSON document with the following top-level keys: `lang`, `title`, `meta`, `links`, `scripts`, `headings`, `images`, `links_audit`, `body_word_count`. Each element carries a `line` number for citing in findings.

For a directory, the output is `{"files": [<per-file object>]}`.

The script uses only Python's standard library — no `pip install` required. If parsing fails on a specific file, the result for that file contains an `error` field and the audit continues for the rest.

### 2. Map signals to the rubric

Load `references/seo-checklist.md`. Walk each section in order and check the corresponding JSON path. The rubric explicitly lists the path to inspect for every check (e.g., `images.missing_alt`, `meta.description.length`, `scripts.render_blocking_candidates`).

For each failed check, record:
- The **severity** (P0/P1/P2/P3) from the rubric.
- The **line number** from the JSON output.
- The **exact quoted markup or attribute value** from the file (re-read the file with the line number to quote verbatim — never paraphrase).
- The **fix**, written as a concrete before/after diff when the change is mechanical.

### 3. Verify each finding before reporting

Before writing a finding, confirm the issue mechanically:
- A claim that an attribute is "missing" must come from the parser's structured output, not from skimming the HTML.
- A claim that a value is "too short/long" must cite the actual character count from the JSON.
- Quoted markup must be exact; if a quote can't be reproduced character-for-character from the file, drop it.

This protects against the most common review failure: fabricating a problem that isn't actually there.

### 4. Produce the findings report

Use `assets/findings-template.md` as the structure. Fill in:
- Summary paragraph with overall verdict and severity counts.
- One block per finding, sorted by severity (P0 → P3) then by file order.
- An optional "Quick wins" section when the finding count exceeds ~10 — pick the 3-5 highest-leverage fixes.
- An "Out-of-scope items noted" section listing anything the user should follow up with external tools (Lighthouse for real CWV, curl for canonical resolution, etc.).

If the audit covers multiple files, produce one report covering all of them, with findings grouped by file under each severity tier — not one report per file.

### 5. Skip gracefully

If a check requires information the parser cannot produce (e.g., "is this canonical URL serving a 200?"), **do not guess**. Note it in the "Out-of-scope items" section of the report and move on.

## Reference

- `scripts/extract_seo_signals.py` — HTML parser. Stdlib-only. Outputs structured JSON with line numbers.
- `references/seo-checklist.md` — Full rubric, organized by category, with severity tiers and JSON paths for every check.
- `assets/findings-template.md` — Output format for the audit report.
