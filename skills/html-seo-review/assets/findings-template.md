# SEO Review — `<file or directory>`

**Reviewed:** `<path>` &nbsp;·&nbsp; **Date:** `<YYYY-MM-DD>` &nbsp;·&nbsp; **Body word count:** `<n>`

## Summary

`<one-paragraph verdict: overall health, key strengths, top risks>`

| Severity | Count |
|---|---|
| P0 — Blocks indexing | `<n>` |
| P1 — Harms ranking/CTR | `<n>` |
| P2 — Best-practice gap | `<n>` |
| P3 — Polish | `<n>` |

---

## Findings

> Each finding follows: **[Severity] Title** &nbsp; `path:line` &nbsp; — &nbsp; problem, then fix.

### [P0] `<short title>`

- **Location:** `<file>:<line>`
- **Evidence:** ` ``<exact quoted attribute or element>`` `
- **Problem:** `<what's wrong and why it matters — reference the rubric section>`
- **Fix:** `<concrete, copy-pastable change>`

```html
<!-- before -->
<existing markup>

<!-- after -->
<corrected markup>
```

---

### [P1] `<short title>`

- **Location:** `<file>:<line>`
- **Evidence:** ` ``<quoted code>`` `
- **Problem:** `<…>`
- **Fix:** `<…>`

---

### [P2] `<short title>`

- **Location:** `<file>:<line>`
- **Evidence:** ` ``<quoted code>`` `
- **Problem:** `<…>`
- **Fix:** `<…>`

---

## Out-of-scope items noted

`<List anything that requires live fetches, rendering, or external tools — e.g., "Verify canonical resolves to a 200 with curl", "Run Lighthouse for real LCP/CLS numbers". Skip this section if nothing applies.>`

## Quick wins (do these first)

`<Optional ordered list of the highest-leverage fixes — usually 3–5 items selected from the findings above. Useful when there are >10 findings and the user needs a starting point.>`
