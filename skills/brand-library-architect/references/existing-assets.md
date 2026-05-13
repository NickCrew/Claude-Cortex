# Discovery — search, infer, confirm, request

The first real phase of the workflow. The output is a `brand/discovery.md` doc capturing what was found, what was inferred, what the user confirmed, and what additional sources the user is providing. Every later phase reads this doc.

Discovery is **bidirectional**: the agent searches and infers (one direction), then surfaces findings and uncertainties to the user (other direction). The user confirms, corrects, and contributes sources the agent can't grep for. Don't skip the conversation — discovery without user input is just file scanning, and file scanning gets the easy 60% but misses what matters most (the designer's Figma file, the unwritten tagline still floating in the founder's head, the past marketing piece that defined the voice).

Four steps, in order: **Search → Infer → Confirm → Request.**

---

## Step 1 — Search

Run the inventory commands in priority order. Higher tiers usually answer questions for lower tiers.

### Tier 1 — Direct authoritative brand assets

Treat as source of truth if found.

```bash
# Brand directory
ls -la brand/ 2>/dev/null
ls -la brand/icons/ brand/exports/ brand/_source/ brand/press/ 2>/dev/null
# (older brand libraries may have brand/sheets/ instead of brand/_source/html/)
ls -la brand/sheets/ 2>/dev/null
ls brand/*.md 2>/dev/null

# Prior discovery output (this skill has run before)
cat brand/discovery.md 2>/dev/null
cat brand/decisions.md 2>/dev/null

# Repo-root convention files
ls -la README.md CONTRIBUTING.md SECURITY.md CODE_OF_CONDUCT.md LICENSE 2>/dev/null
```

### Tier 2 — Implicit brand sources (most common)

These usually contain brand decisions but in non-canonical locations. Extract values; propose moving the canonical sources later.

```bash
# CSS color tokens — primary leverage point
grep -rEho '#[0-9a-fA-F]{3,8}' src/**/*.css src/**/*.scss 2>/dev/null | sort -u | head -30
grep -rEho '--[a-z-]+:\s*#[0-9a-fA-F]+' src/ 2>/dev/null | sort -u | head -30

# CSS custom property definitions in :root
grep -A 100 ':root' src/index.css src/**/*.css 2>/dev/null | head -100
grep -A 100 ':root' src/styles/**/*.css 2>/dev/null | head -100

# Tailwind / styled-components / CSS-in-JS color/font config
cat tailwind.config.* 2>/dev/null | head -100
cat theme.config.* 2>/dev/null | head -50
grep -rEh "primary|brand|accent" tailwind.config.* 2>/dev/null

# Typography
grep -rEho 'font-family:[^;]+' src/ 2>/dev/null | sort -u | head -10
grep -rEho 'font-family:[^"]+' tailwind.config.* 2>/dev/null

# Logo / mark / wordmark assets — anywhere in the repo
find . -type f \( -name "logo*" -o -name "*-logo*" -o -name "wordmark*" -o -name "*-mark.*" -o -name "favicon*" -o -name "*-lockup*" \) 2>/dev/null | grep -v node_modules | head -30

# OG / banner / hero images
find . -type f \( -name "og-image*" -o -name "*banner*" -o -name "*-hero.*" -o -name "*-hero-*" \) 2>/dev/null | grep -v node_modules | head -20

# Brand-flavored copy in unexpected locations
grep -rEl 'tagline|hero|manifesto|positioning' docs/ public/ 2>/dev/null | head -10
grep -rEl 'pricing|subscription|pass' docs/ 2>/dev/null | head -10

# Product metadata
cat package.json 2>/dev/null | head -40
cat pyproject.toml 2>/dev/null | head -40
cat Cargo.toml 2>/dev/null | head -40
```

### Tier 3 — Adjacent constraints

These don't directly contain brand content but constrain what brand can claim. Surface to the user; don't silently override.

```bash
# Internal pricing / entitlement docs (may conflict with brand pricing claims)
find docs/ -iname "*pricing*" -o -iname "*entitlement*" -o -iname "*billing*" 2>/dev/null

# Existing CLAUDE.md / AGENTS.md — project conventions to respect
ls -la CLAUDE.md AGENTS.md 2>/dev/null
cat CLAUDE.md 2>/dev/null | head -100

# Backlog tasks related to brand work
grep -rli "brand\|copy\|tagline\|manifesto\|press kit" backlog/tasks/ 2>/dev/null | head

# Past blog posts, marketing pages, landing copy
find docs/ public/ site/ marketing/ -type f -name "*.md" -o -name "*.mdx" 2>/dev/null | head -20
```

---

## Step 2 — Infer

For each Tier 1/2/3 finding, infer what brand decision it implies. Inference heuristics:

### From CSS color tokens

| Pattern | Infer |
|---|---|
| `--primary: #2d6a96` or similar | Primary brand color |
| Multiple shade tokens (`--brand-50`, `--brand-100`, …, `--brand-900`) | Full color scale; brand commits to a palette family |
| `--gem-light`, `--gem-dark` (named) | Brand-specific token names — the brand has a metaphor (gem); record it |
| `--bg-primary`, `--text-primary`, `--surface-*` | Theming convention; matches brand-doc dark/light theme tables |
| Status colors (`--success`, `--warning`, `--error`) in two themes | Theming maturity; copy directly into BRAND.md |

### From typography

| Pattern | Infer |
|---|---|
| `font-family: 'Inter'` or similar | Body font choice |
| `font-family: 'IBM Plex Mono'` etc. | Mono font choice |
| Display font with `font-style: italic` and brand-color use | Likely a wordmark or brand-display font; flag for confirmation |
| Multiple weight ranges loaded | Brand commits to a weight system |

### From logo / mark assets

| Pattern | Infer |
|---|---|
| `assets/logo.svg`, `public/logo.svg` | Wordmark or mark exists in non-canonical location; propose moving to `brand/icons/svg/` |
| Multiple variants (`logo-dark`, `logo-light`, `logo-active`) | Mark has theme variants — extract the pattern |
| SVG paths with two colors | Likely a two-tone mark (one of the most common patterns); confirm with user |
| Filename includes "wordmark" or "lockup" | The user already distinguishes mark / wordmark / lockup — preserve their vocabulary |

### From existing README / docs

| Pattern | Infer |
|---|---|
| README headline / subtitle | Existing locked hero (or pre-locked-vocabulary version of it) |
| README badge labels (e.g., "PRs Welcome") | OSS conventions already in place |
| Existing CONTRIBUTING with project-specific commit conventions | Preserve those conventions in the new CONTRIBUTING |
| LICENSE file | Confirms license choice for Phase 1 decision rubric |

### From package metadata

| Pattern | Infer |
|---|---|
| `package.json` `license` field | License choice (likely matches LICENSE file) |
| `author.email` | Canonical contact email — use across SECURITY, press kit, README |
| `repository.url` | Repo URL for README / press-kit links |
| `description` | Existing one-line product description; may need updating to locked vocabulary but the structure is there |

### Per-asset disposition (after inference)

For each found asset, determine one of four dispositions:

| Disposition | When to apply |
|---|---|
| **Preserve** | Asset is fresh, well-crafted, voice-correct. Don't modify. Still *read* during later phases for cross-reference. |
| **Merge** | Asset is partial — has good bones, missing sections. Augment, don't rewrite. Most common for README / BRAND.md / COPY.md when partial. |
| **Replace** | Asset is severely out of date and user explicitly requests refresh. Show diff before write. |
| **Archive** | Asset is retired but worth keeping for reference. Move to `_archive/` with a note explaining retirement. |

The default is **preserve and surface** — when in doubt, preserve the existing work and surface to the user, rather than overwriting.

---

## Step 3 — Confirm

Surface the findings to the user. Don't act on inferences silently. Use this conversation pattern:

### Pattern A: Inventory summary first

> **Discovery summary**
>
> Found in this repo:
> - 3 logo SVGs at `assets/logos/` (gem dark, gem light, wordmark lockup)
> - CSS color tokens in `src/index.css` — extracted 8 brand colors (`#2d6a96` primary, `#6cb8e8` accent, etc.)
> - Existing README.md with positioning copy ("Strategic resume assembly for senior engineers")
> - LICENSE: AGPL-3.0; package.json author email: nick@atlascrew.dev
> - No MANIFESTO.md, BIOS.md, FAQ.md, GLOSSARY.md, TONE.md, or PRICING.md
> - One pre-rebrand banner image at `docs/assets/facet-banner.png` (no active references)
>
> Proposed dispositions:
> - **Move**: `assets/logos/*.svg` → `brand/icons/svg/`
> - **Extract**: CSS color tokens into `brand/decisions.md` and `brand/BRAND.md` color tables
> - **Merge**: README.md (preserve install/run/structure; replace pre-locked-vocabulary subtitle and intro)
> - **Archive**: `docs/assets/facet-banner.png` → `_archive/` (no active references; superseded by upcoming brand/exports/readme/)
> - **Create new**: MANIFESTO.md, BIOS.md, FAQ.md, GLOSSARY.md, TONE.md, PRICING.md
>
> Confirm? Adjust any of these?

### Pattern B: Surface uncertainties explicitly

When inference is ambiguous, ask rather than guess:

> Found `font-family: 'Instrument Serif'` in `src/components/Logo.tsx`. This looks like a wordmark font choice, but it's also referenced in body text under `.hero-tagline`. Two possibilities:
> - Wordmark-only font (most common; Instrument Serif is unusual for body)
> - Wordmark + display font (Instrument Serif used as the brand's display register on hero surfaces)
>
> Which fits your intent?

### Pattern C: Conflict detection

When existing assets contradict each other or contradict an external source:

> Found a pricing conflict:
> - `brand/MANIFESTO.md` (last touched yesterday) commits to "$299 per 90-day pass, no subscription"
> - `docs/development/platform/wave-1-pricing-and-entitlements.md` (last touched 4 weeks ago) defines the paid plan as "one paid monthly Stripe plan"
>
> The brand surface and internal entitlement spec disagree on whether the model is episodic or subscription. Before I write PRICING.md, which is canonical?

---

## Step 4 — Request

Ask the user for sources you can't grep for. The repo only has what's been committed; brand decisions often live elsewhere.

### Standard request prompts

> I've inventoried this repo. Before we move to decisions, are there sources I can't see from here?
>
> Common ones to consider:
> - **Designer artifacts.** Figma / Sketch / Adobe XD files; brand guideline PDFs from a designer; mood boards
> - **Logo files in another location.** A shared drive, an old repo, a vendor's deliverables folder
> - **Past marketing materials.** Old landing pages, deck templates, conference one-pagers, press releases — these often have brand voice that should inform the new docs
> - **External references.** A blog, podcast, or interview where you've articulated positioning that hasn't yet made it into the repo
> - **Adjacent products.** Other repos in the same brand family (e.g., a marketing site repo separate from the product repo)
> - **Founder voice samples.** Tweets, blog posts, conference talks — useful for seeding voice register if BIOS or MANIFESTO authoring needs it
>
> If any exist, share file paths or URLs and I'll incorporate them.

### When the user provides URLs

If the user shares URLs (Figma, Notion, Google Doc, blog post):

- **Fetch** the content if possible (WebFetch or similar tool).
- **Extract** brand-relevant content: color hex values, font names, taglines, positioning paragraphs.
- **Update** `brand/discovery.md` with the extraction.
- **Surface** any conflicts between extracted content and what's in the repo.

If the user shares file paths to local files outside the repo:

- **Read** the files (Read tool).
- **Same extract / update / surface flow.**

If the user has files but in a format the agent can't read (Figma, Sketch, .ai):

- **Ask the user to summarize** the relevant content. "Can you tell me the color palette and font choices from the Figma file?"
- **Or ask for a different format**. "Can you export the brand guideline page as a PDF or screenshots?"
- **Don't fabricate**. Don't claim to have read a Figma file you can't read.

---

## Output: brand/discovery.md

After the four steps, capture everything in `brand/discovery.md`. This becomes a permanent record subsequent phases reference. Format:

```markdown
# Brand library discovery

Run on {{DATE}}.

## Inventory found

### Tier 1 — Direct brand assets
- [list]

### Tier 2 — Implicit brand sources
- CSS color tokens in `src/index.css`:
  - `--primary: #2d6a96`
  - `--accent: #6cb8e8`
  - …
- Logo files at `assets/logos/`:
  - `gem-dark.svg`
  - `gem-light.svg`
  - `wordmark-lockup.svg`
- Typography in `src/index.css`:
  - Body: Inter
  - Mono: IBM Plex Mono

### Tier 3 — Adjacent constraints
- `docs/development/platform/wave-1-pricing-and-entitlements.md` — internal entitlement spec; may conflict with brand pricing

## Inferences

| Asset | Inferred decision |
|---|---|
| `--primary: #2d6a96` | Primary brand color is `#2d6a96` |
| `--accent: #6cb8e8` | Accent / highlight is `#6cb8e8` |
| `gem-dark.svg` + `gem-light.svg` | Two-tone mark with theme variants |
| Inter body + IBM Plex Mono | Typography system |
| AGPL-3.0 in LICENSE | License is AGPL-3.0 |
| `nick@atlascrew.dev` in package.json | Canonical contact email |

## Dispositions confirmed

- **Move**: `assets/logos/*.svg` → `brand/icons/svg/`
- **Extract**: CSS tokens → BRAND.md color tables
- **Merge**: README.md
- **Archive**: `docs/assets/facet-banner.png`
- **Create new**: MANIFESTO.md, BIOS.md, FAQ.md, GLOSSARY.md, TONE.md, PRICING.md

## User-provided sources

- Figma file: [URL] — designer's brand guideline; reviewed, extracted color palette and mark variants
- Past blog post: [URL] — voice register reference
- Founder bio in personal notes: shared inline; used to seed BIOS.md 250w version

## Conflicts surfaced

- Pricing model: brand MANIFESTO commits to passes; internal Wave 1 doc commits to monthly Stripe. User confirmed: passes are canonical; internal doc to be updated separately.

## Resolved

- Brand verb: extracted "recut" from existing FAQ stub. Confirmed.
- Color palette: extracted from CSS. Confirmed.
- License: confirmed AGPL-3.0.
- Pricing: confirmed $299 / 90-day pass / 12-month window / 7-day refund.

## Still open (Phase 1 will resolve)

- Tagline: not yet committed in any source
- Manifesto sections beyond stub: needs Phase 1 authoring
- FAQ answer 10: depends on Live mode framing decision
```

This doc carries forward to all subsequent phases. Treat it as a Phase 0 commitment — if a later phase contradicts it, surface the conflict; don't silently overwrite.

---

## Workflow notes

**Don't skip Step 4.** The temptation is to scan, infer, confirm, and start writing. But the highest-value brand inputs almost always live outside the repo (designer Figma file, founder's tweet thread, an old marketing one-pager). Asking for them upfront takes 30 seconds and routinely surfaces material that prevents weeks of voice drift.

**Run discovery on every fresh invocation.** Even if the skill ran once before, the project state has evolved. CSS may have changed; the founder may have renamed something; new sources may exist. Don't trust an old `brand/discovery.md` blindly — re-run the search and reconcile.

**Discovery as a standalone capability.** The user may invoke the skill *just* for discovery ("audit the brand assets in this repo") without committing to the full library build. In that case, run all four steps and produce `brand/discovery.md`, but stop before Phase 1. The discovery doc on its own is useful — it's the audit deliverable.

**Conflict surfacing is the highest-value output.** Discovery's most useful moments aren't "here's a tidy inventory" — they're "the internal pricing doc and the brand pricing claim disagree" or "the existing README subtitle uses retired vocabulary." These are the things the user can't see at a glance and most need to know.
