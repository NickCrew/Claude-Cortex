# HTML SEO Review Checklist

Comprehensive rubric for auditing static HTML files. Every check below maps to a specific path in the JSON output of `scripts/extract_seo_signals.py`.

## Severity tiers

- **P0 — Blocks search visibility.** Page won't index, will be deindexed, or critical metadata is absent.
- **P1 — Harms ranking or click-through.** Real-world SEO impact, but page still indexes.
- **P2 — Best-practice gap.** Likely no immediate ranking impact, but missing recommended signal.
- **P3 — Polish.** Minor improvement; bring up only if everything else is clean.

---

## 1. Document fundamentals

### 1.1 `<html lang="…">` set — P1
- **Signal path:** `lang`
- **Pass:** non-empty string (e.g., `"en"`, `"en-US"`)
- **Fail:** `null` or empty
- **Why:** Helps search engines and assistive tech determine language for the page; affects regional ranking and accessibility.

### 1.2 `<meta charset>` declared — P2
- **Signal path:** `meta.charset`
- **Pass:** present, ideally `"utf-8"`
- **Why:** Without an explicit charset, browsers may misrender characters before the parser figures it out.

### 1.3 Viewport meta — P1
- **Signal path:** `meta.viewport`
- **Pass:** present and contains `width=device-width`
- **Why:** Mobile-first indexing. Pages without a viewport meta are flagged as not mobile-friendly and lose ranking on mobile results.

---

## 2. Title and description

### 2.1 Title present — P0
- **Signal path:** `title.text`
- **Pass:** non-empty
- **Fail:** missing or empty
- **Why:** Title is the single most important on-page SEO signal. Missing titles cause Google to synthesize one (poorly) or skip indexing entirely.

### 2.2 Title length 30–60 characters — P1
- **Signal path:** `title.length`
- **Pass:** 30 ≤ length ≤ 60
- **Soft warn:** 25–29 (too short, low keyword surface) or 61–70 (will likely truncate)
- **Fail:** <25 or >70
- **Why:** Google truncates titles around 580px in SERPs, which works out to roughly 60 chars depending on glyph width. Too short signals thin content.

### 2.3 Meta description present — P1
- **Signal path:** `meta.description`
- **Pass:** present
- **Why:** Not a direct ranking factor since 2009, but heavily influences click-through rate. Google often uses it as the SERP snippet when it matches the query.

### 2.4 Meta description length 70–160 characters — P2
- **Signal path:** `meta.description.length`
- **Pass:** 70 ≤ length ≤ 160
- **Why:** Truncation cutoff is ~160 characters on desktop, ~120 on mobile. Below 70 wastes the slot.

---

## 3. Heading structure

### 3.1 Exactly one `<h1>` — P1
- **Signal path:** `headings.h1_count`
- **Pass:** `== 1`
- **Fail:** `0` (P1 — no primary heading) or `> 1` (P2 — competing primary headings; HTML5 technically allows multiple but search engines still prefer one)
- **Why:** Search engines weigh the H1 heavily as a topical signal. Zero H1s leaves the topic implicit; multiple dilute it.

### 3.2 No skipped heading levels — P2
- **Signal path:** `headings.outline`
- **Pass:** levels increase by at most 1 at a time when descending (e.g., H1 → H2 → H3 OK; H1 → H3 not OK)
- **Why:** Document outline algorithms (and screen readers) rely on sequential nesting to build the page structure. Skipping levels confuses both.

### 3.3 H1 not duplicating title verbatim — P3
- **Signal paths:** `title.text`, `headings.outline[0]`
- **Why:** Some duplication is fine and even expected, but a page where every heading is identical to the title is a weak topical signal.

---

## 4. Indexability and canonicalization

### 4.1 Robots meta does not block indexing — P0
- **Signal path:** `meta.robots.content`
- **Fail:** contains `noindex` (page won't appear in search) or `nofollow` (links won't pass authority)
- **Why:** Easiest way to silently disappear from search. Always confirm intent — `noindex` may be deliberate on staging/auth pages.

### 4.2 Canonical URL declared — P1
- **Signal path:** `links.canonical`
- **Pass:** present and a valid absolute URL
- **Fail:** missing on a page that may have query-string or trailing-slash variants
- **Why:** Without canonical, duplicate-content variants compete for the same ranking slot, splitting authority.

### 4.3 Canonical points to itself or a single source-of-truth — P1
- **Signal path:** `links.canonical.href`
- **Manual check:** confirm the canonical URL matches the page's actual public URL (or intentionally points to a parent/aggregate page).
- **Why:** Wrong canonical (e.g., copy-paste from a template) can deindex a page entirely.

### 4.4 hreflang alternates if multilingual — P2
- **Signal path:** `links.alternates`
- **Why:** Without hreflang, Google may serve the wrong language version in the wrong region.

---

## 5. Open Graph and Twitter Card

### 5.1 og:title — P2
- **Signal path:** `meta.og['og:title']`
- **Why:** Drives the preview when the URL is shared on Facebook, LinkedIn, Slack, etc. Falls back to `<title>` but a tailored OG title performs better.

### 5.2 og:description — P2
- **Signal path:** `meta.og['og:description']`

### 5.3 og:image — P2
- **Signal path:** `meta.og['og:image']`
- **Why:** Without an OG image, social shares fall back to a default crop or a logo, drastically reducing click-through.

### 5.4 og:url and og:type — P3
- **Signal paths:** `meta.og['og:url']`, `meta.og['og:type']`

### 5.5 twitter:card — P3
- **Signal path:** `meta.twitter['twitter:card']`
- **Why:** Twitter falls back to OG tags if absent, so this is polish unless the page heavily targets Twitter previews.

---

## 6. Structured data (JSON-LD)

### 6.1 At least one valid JSON-LD block — P2 (P1 for content pages)
- **Signal path:** `scripts.jsonld`
- **Pass:** `valid: true` and `data['@type']` is appropriate (`Article`, `Product`, `FAQPage`, `Recipe`, etc.)
- **Why:** Required for rich results (review stars, FAQ accordion, breadcrumbs in SERP). Schema matters more on content/commerce pages than on static landing pages.

### 6.2 No JSON-LD parse errors — P1
- **Signal path:** `scripts.jsonld[*].valid`
- **Fail:** any `valid: false`
- **Why:** Invalid JSON-LD is ignored entirely by Google — silent failure of intended rich-result eligibility.

---

## 7. Images

### 7.1 No images missing alt attribute — P1
- **Signal path:** `images.missing_alt`
- **Pass:** empty array
- **Why:** Direct accessibility regression and a soft SEO signal — alt text is one of the few things Google can use to understand image content.

### 7.2 Empty alt only on decorative images — P2
- **Signal path:** `images.empty_alt`
- **Manual check:** review each — `alt=""` is *correct* for purely decorative images (icons, dividers) but wrong for content images.
- **Why:** Empty alt explicitly signals "skip me" to screen readers; using it on content images is worse than omitting alt entirely.

### 7.3 Width and height attributes set — P2
- **Signal path:** `images.missing_dimensions`
- **Why:** Reserves layout space, prevents Cumulative Layout Shift (CLS), which is a Core Web Vital and a ranking factor.

### 7.4 `loading="lazy"` on below-the-fold images — P3
- **Signal path:** `images.no_lazy_loading`
- **Manual check:** the *first* image (often the hero / LCP candidate) should NOT be lazy-loaded; everything below the fold should be.
- **Why:** Lazy-loading hero images delays Largest Contentful Paint, which is the opposite of what you want.

---

## 8. Performance signals (easy wins only)

### 8.1 No render-blocking sync scripts in `<head>` — P1
- **Signal path:** `scripts.render_blocking_candidates`
- **Pass:** empty, or scripts are inline-only / placed at end of `<body>`
- **Why:** Each blocking script delays First Contentful Paint by its download + parse time. Trivial fix: add `defer` (preserves order, runs after parse) or `async` (no order guarantee).

### 8.2 Stylesheets minimized — P3
- **Signal path:** `links.stylesheets`
- **Manual check:** small number of stylesheet `<link>` tags, ideally one or two. Many small stylesheets = many roundtrips.

### 8.3 Use of preload for critical resources — P3
- **Signal path:** `links.preloads`
- **Why:** Preloading critical fonts/hero images can move LCP earlier, but only worth flagging on pages already otherwise clean.

---

## 9. Links

### 9.1 No empty or hash-only anchor hrefs — P2
- **Signal path:** `links_audit.empty_or_hash`
- **Pass:** empty array (or all entries are clearly buttons/dropdowns implemented as anchors — judge case-by-case)
- **Why:** Google ignores empty hrefs; on multiple pages, they accumulate as crawl waste.

### 9.2 External links use `rel="noopener"` (and usually `nofollow` or `ugc`) — P3
- **Signal path:** `links_audit.external[*].rel`
- **Why:** Security (`noopener`), and ranking-control (`nofollow`/`ugc` for user-submitted/sponsored links). Not always required.

### 9.3 Anchor text is descriptive — P2
- **Signal path:** `links_audit.internal[*].text`, `links_audit.external[*].text`
- **Manual check:** flag anchors with text like "click here," "read more," "this," or empty — they pass no topical signal to the destination.

---

## 10. Content depth

### 10.1 Body word count appropriate to page type — P2
- **Signal path:** `body_word_count`
- **Heuristics:** Landing/home: 100+ usually fine. Article/blog: 300+ as a minimum, 600+ for competitive topics. Product page: 150+ of unique copy beyond spec sheets.
- **Why:** Thin content underperforms. But word count is a coarse proxy — a 200-word answer that perfectly matches intent beats a 2000-word ramble.

---

## Checks intentionally NOT in this rubric (out of scope)

The skill is HTML-only. The following require live fetches, rendering, or external services and are explicitly out of scope:
- Real Core Web Vitals (LCP/CLS/INP) — needs a rendering engine.
- Backlink profile, domain authority — needs third-party data.
- robots.txt, sitemap.xml — site-level, not page-level.
- HTTP status codes, redirect chains — needs network access.
- JavaScript-rendered content audit — needs a headless browser.

If a finding requires any of these, note it as "out of scope for HTML review; recommend follow-up with [tool]" rather than guessing.
