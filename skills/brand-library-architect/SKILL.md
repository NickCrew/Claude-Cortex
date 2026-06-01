---
name: brand-library-architect
description: Build a complete brand library for a product — visual asset render pipeline, brand documentation set (BRAND, COPY, MANIFESTO, BIOS, FAQ, GLOSSARY, TONE, PRICING), open-source convention files (README, CONTRIBUTING, SECURITY, CODE_OF_CONDUCT), and a self-contained press kit. This skill should be used when the user asks to "build a brand library / brand kit / press kit / brand assets" for a product, "set up a brand library workflow," "create a positioning manifesto plus visual identity," or any combination of brand documentation + visual asset pipeline. Apply phase-by-phase or run end-to-end. Templates are product-agnostic and use {{TOKEN}} placeholders the skill prompts the user to fill.
keywords:
  - brand library
  - brand kit
  - press kit
  - brand assets
  - positioning manifesto
  - visual identity
  - brand documentation
---

# Brand Library Architect

## Overview

This skill captures a phased workflow for building a complete brand library for a product. It produces a coherent set of artifacts: a render pipeline for visual assets (HTML sheets → Playwright → WebP), a documentation set rooted in locked vocabulary and voice rules, repo conventions for open-source projects, and a press kit. The phases reference each other (e.g., the press kit pulls bios from `BIOS.md`, the README banner cites the visual pipeline output) so cross-references work even when phases are run independently.

Every template uses `{{TOKEN}}` placeholders for product-specific content. Prompt the user for the relevant tokens at the start of each phase rather than guessing, so the resulting library is voice-true to the product and not generically branded.

## When to use this skill

Apply when the user asks for any of:

- "Build a brand library / brand kit / brand assets for product X"
- "Set up the brand library workflow for this repo"
- "Create a positioning manifesto + visual identity"
- "Author a press kit / FAQ / glossary / tone guide / pricing doc / founder bio"
- "Add CONTRIBUTING / SECURITY / CODE_OF_CONDUCT to this repo with brand voice"
- "I have visual assets — help me write the brand documentation that anchors them" (or vice versa)
- "Audit the brand assets in this repo" / "What brand assets do we have?" / "Discover existing brand surface" → run **Phase 0 only** as a standalone audit

Apply selectively when only one or two phases are needed. The phases are independent enough to mix and match.

Do not apply this skill when the user wants:
- Product feature documentation (use `documentation-production`)
- Generic copywriting unrelated to brand library structure (use `copywriter`)
- Visual UI components or design systems (use `ui-design-aesthetics` or `frontend-design`)
- Internal-only docs (this skill is public-facing brand surface)

## Phases

The workflow is seven phases (0-6). Run sequentially for a new product, or jump to a specific phase for incremental work. Phases 0 and 1 are required before any other phase.

### Phase 0 — Discovery

Read `references/existing-assets.md` and run the four-step Discovery workflow:

1. **Search** the repo for existing brand assets, CSS color tokens, typography, logo files, OG/banner images, package metadata, internal pricing/entitlement docs that may constrain brand claims, and adjacent docs (CLAUDE.md, backlog tasks).
2. **Infer** what each finding implies about brand decisions (e.g., `--primary: #2d6a96` in `src/index.css` → primary brand color; existing README subtitle → pre-locked-vocabulary version of the locked hero; package.json `author.email` → canonical contact email).
3. **Confirm** with the user. Surface the inventory and proposed dispositions; surface any inference uncertainties or detected conflicts. Default to **preserve and surface** rather than overwrite — never silently rewrite existing brand assets.
4. **Request** sources the agent can't grep for: designer Figma files, brand guideline PDFs, past marketing materials, external blog/podcast voice samples, logo files in shared drives or other repos. The highest-value brand inputs almost always live outside the repo.

The output is `brand/discovery.md` — a permanent record of what was found, what was inferred, what the user confirmed, and what additional sources the user provided. Subsequent phases read this doc.

Discovery can also run as a standalone capability (e.g., "audit the brand assets in this repo") — produce `brand/discovery.md` and stop. The discovery doc on its own is a useful audit deliverable.

### Phase 1 — Decision rubric

Read `references/decision-rubric.md` and walk the user through any decisions Discovery didn't already answer. Don't re-elicit values that exist in `brand/discovery.md` — that's the whole point of running Discovery first. The output is `brand/decisions.md` capturing:

- Product name, domain, repo URL, contact email
- Brand verb (the owned action), durable noun (the substrate term), tagline, locked hero, trust line
- Color palette (primary brand color minimum; full palette preferred)
- Typography choices (body, mono, wordmark, display)
- License (AGPL-3.0 / MIT / Apache-2.0 / proprietary)
- Pricing model (episodic-pass / subscription / freemium / free / open-source-only)
- Pre-launch state (yes/no — affects deferral language throughout)
- Distribution domain for public docs (when public site lands)

Do not skip this. Subsequent phases reference these decisions. If the user resists upfront commitment on any token (e.g., "I don't have a tagline yet"), record the gap and proceed; later phases will surface where the gap blocks specific deliverables.

### Phase 2 — Bootstrap

Read `references/directory-structure.md` first — it documents the canonical layout (where files live, naming conventions, what goes in `icons/svg/` vs `icons/png/`, what goes in `_source/html/` vs `exports/`, etc.) and the rationale behind each choice.

Create the directory structure and seed the canonical brand docs with placeholders:

```
brand/
├── README.md         # library navigator (start here)
├── CHEATSHEET.md     # 30-second locked-values lookup
├── CHANGELOG.md      # chronological log of brand changes
├── CLAUDE.md         # directory-local AI agent rules
├── RECIPES.md        # common-task playbook
├── BRAND.md          # visual brand reference (marks, colors, typography, asset library)
├── COPY.md           # language reference (locked vocabulary, voice, asset → phrase index)
├── MANIFESTO.md      # long-form positioning argument
├── decisions.md      # the upfront commitments from Phase 1
└── (later phases populate the rest)
```

Anchor doc templates: `assets/brand-docs/BRAND.md.template`, `assets/brand-docs/COPY.md.template`, `assets/brand-docs/MANIFESTO.md.template`.

Quick-reference doc templates (one-line landing page for each common task):
- `assets/brand-docs/README.md.template` — library navigator with "what lives where" tables and quick paths
- `assets/brand-docs/CHEATSHEET.md.template` — 30-second locked phrases / colors / fonts / pricing card
- `assets/brand-docs/CLAUDE.md.template` — directory-local rules for AI agents editing brand files
- `assets/brand-docs/CHANGELOG.md.template` — audit log seed with bootstrap entry, examples for common change types
- `assets/brand-docs/RECIPES.md.template` — common-task playbook (add a sheet, refresh press kit, run vocab check, etc.)

Walk the user through filling each section. The MANIFESTO is the highest-leverage; it's where the positioning argument actually lives, and the FAQ / TONE / PRICING / BIOS docs reference it for long-form. Do not skim it — spend real time here. A weak manifesto produces weak everything else.

The quick-ref docs are templated specifically — fill the `{{TOKEN}}` placeholders from `decisions.md` (CHEATSHEET) or genericize based on Phase 0 inventory (README, RECIPES). The CHANGELOG seeds with the bootstrap entry; future entries get appended as substantive changes happen. CLAUDE.md is mostly product-agnostic — only the `{{PRODUCT_SLUG}}` and `{{BRAND_VERB}}` placeholders need filling.

### Phase 3 — Visual asset pipeline

Set up the render pipeline that produces brand exports from HTML source sheets. Templates:

- `assets/pipeline/brand.justfile.template` — parameterized just recipes for rendering, WebP conversion, and composite reference sheets
- `assets/sheets/concept-1200x630.html.template` — concept poster (system / identity / methodology / etc)
- `assets/sheets/manifesto-1080x1350.html.template` — portrait anti-positioning card
- `assets/sheets/method-1600x900.html.template` — widescreen methodology one-pager
- `assets/sheets/readme-1280x640.html.template` — 2:1 GitHub README banner
- `assets/sheets/og-1200x630.html.template` — Open Graph image
- `assets/sheets/poster-1224x1584.html.template` — letter-portrait designer-handoff brand summary (dark + light)
- `assets/sheets/swatch-1584x1224.html.template` — letter-landscape designer-kit reference (lockups / colors / type, light only)

Each HTML sheet is self-contained, uses brand color/typography variables from Phase 0, and has a render-mode handler so Playwright can isolate variants by URL hash. The justfile recipes wire Playwright + cwebp into a `just brand` umbrella command.

**Designer-facing artifacts** — the poster + swatch templates produce print-ready letter-sized handoff materials:

- **Poster** (1224×1584 letter portrait, dark + light): single-page brand summary for external designer onboarding. Wordmark hero, color palette, typography, locked-phrases card, footer.
- **Swatch** (1584×1224 letter landscape, light only): standard designer-kit reference card. Lockup specimens, color swatches with hex codes, typography specimens with weights and roles. Living artifact for `press/swatch/` so journalists/designers grab it via the press URL — output as PNG (not WebP) since designers print and import to slides/Figma.

These differ from the screen-friendly `reference.html` (if your bootstrap includes one): poster + swatch are letter-sized, print-ready, and copy-light. The brand library's screen reference is for internal-team use; the poster + swatch are for external-designer handoff.

Additional asset types not templated but worth knowing about: carousel (multi-slide deck), story (1080×1920 vertical), principle cards (1080×1080 quote cards), promo banners (launch-state), email headers, social square posts. See `references/additional-asset-types.md` for descriptions and when to extend the pipeline.

After scaffolding the pipeline, run `just brand` to confirm the render chain works end-to-end. The first run will produce empty/placeholder assets that the user iterates on.

### Phase 4 — Brand docs

Author the documentation set that extends BRAND/COPY/MANIFESTO with applied content:

- `BIOS.md` — three-size founder bio, three-size company boilerplate, social profile bios. Use `assets/brand-docs/BIOS.md.template`. Word counts: 50w / 100w / 250w (±5). Char caps for social: Twitter ≤160, LinkedIn ≤120, GitHub ≤160, BlueSky ≤256.
- `FAQ.md` — 10 canonical Q&A entries, each 50–150 words. Use `assets/brand-docs/FAQ.md.template`. Each answer references MANIFESTO sections; doesn't duplicate them.
- `GLOSSARY.md` — defines 6–10 brand-vocabulary terms with cross-references and don't-substitute callouts. Use `assets/brand-docs/GLOSSARY.md.template`.
- `TONE.md` — register-by-surface guide for support reply, release note, tweet, blog post intro, email subject. Use `assets/brand-docs/TONE.md.template`. Each surface gets register pressure + 2 good examples + 2 avoid examples.
- `PRICING.md` (only if user has a paid product) — public-facing pricing argument. Use `assets/brand-docs/PRICING.md.template`. Templates support both episodic-pass and subscription pricing models; see `references/pricing-models.md`.

After authoring, mechanically verify word/char counts:

```bash
# Word counts on FAQ answers (must be 50-150)
python3 scripts/word_count.py brand/FAQ.md
# Vocabulary check against don't-use list
bash scripts/vocab_check.sh brand/
```

### Phase 5 — Repo conventions

Refresh `README.md` and add open-source convention files. Templates:

- `assets/repo-conventions/README.md.template` — theme-aware `<picture>` banner, locked positioning intro, install/run, cross-links to brand docs
- `assets/repo-conventions/CONTRIBUTING.md.template` — license-aware contribution stance, dev setup, code style, brand voice rules linked to COPY.md
- `assets/repo-conventions/SECURITY.md.template` — vulnerability disclosure flow, response targets, scope, safe-harbor
- `assets/repo-conventions/CODE_OF_CONDUCT.md.template` — Contributor Covenant 2.1 **adopted by reference, not embedded**. Embedding the verbatim text triggers content-filtering on output (the Covenant explicitly enumerates harassment types). Adopt-by-reference is a documented pattern used by Kubernetes, React, Vue, Rails, etc.

License sensitivity: if the user chose a non-OSS license at Phase 0, skip CONTRIBUTING / SECURITY / CODE_OF_CONDUCT (or adapt — see `references/license-considerations.md`).

### Phase 6 — Press kit

Compile a self-contained `brand/press/` folder. Pulls from already-built artifacts:

- `brand/press/README.md` — quick facts, file inventory, bios inlined from BIOS.md, brand colors from BRAND.md, AGPL attribution policy, contact. Use `assets/press/press-README.md.template`.
- `brand/press/logos/` — copies of canonical logo SVGs from `brand/icons/svg/`, plus high-res raster equivalents (≥1200px wide) rendered via `rsvg-convert`.
- `brand/press/hero/` — copies of the README hero WebP variants from `brand/exports/readme/`.

No customer testimonials, case studies, or coverage clips if pre-launch; explicitly note their deferral in the press-kit README so journalists understand they're absent intentionally.

Distribution: until a public site exists, the press kit ships via the GitHub URL of the folder. Document in the press-kit README that the canonical URL will mirror to the public site when it lands.

## Decision rubric and quality checks

Read these references files as needed during the phases:

- `references/decision-rubric.md` — Phase 0 questionnaire and how to elicit each decision from the user
- `references/existing-assets.md` — Phase 0 detection sweep + per-asset disposition (preserve/merge/replace/archive); how to handle non-greenfield projects
- `references/directory-structure.md` — canonical brand library layout, naming conventions, what goes where
- `references/voice-checks.md` — don't-use vocabulary patterns; vocabulary table for the product gets seeded into COPY.md
- `references/word-count-bounds.md` — verification rubric for FAQ (50–150 words), bios (50/100/250 ±5), social caps
- `references/cross-link-map.md` — what should reference what; verifies cross-link integrity at end of each phase
- `references/pre-launch-deferrals.md` — what to defer in pre-launch state vs post-launch
- `references/additional-asset-types.md` — extended visual asset types (carousel, story, principle cards, promo) — descriptions and pattern guidance for extending the pipeline
- `references/pricing-models.md` — episodic-pass / subscription / freemium / free guidance and which PRICING.md sections to keep / cut
- `references/license-considerations.md` — AGPL / MIT / Apache / proprietary affects which conventions ship and how CONTRIBUTING reads

## Workflow notes

**Pricing-model conflicts surface late.** If the product has internal billing/entitlement docs (e.g., for a hosted version), check those *before* writing PRICING.md — a public-facing PRICING.md that contradicts the internal entitlement spec creates real downstream confusion. Surface the conflict to the user; do not paper over it.

**Memory vs canonical doc.** When agent memory and a brand doc disagree on a fact (price, positioning, naming), prefer the doc and update the memory. The `decisions.md` from Phase 0 is the source of truth for product-specific facts; if memory drifts, fix the memory.

**Brand-led-product is fine.** It is reasonable for brand to commit to naming or pricing ahead of the product reflecting it (e.g., the brand decides "Track" replaces "Pipeline" before the product nav renames). Document the gap in `decisions.md` so the brand-vs-product divergence is visible.

**Do not fabricate.** If the user can't supply a token (no tagline, no MANIFESTO content, no hex codes), record the gap rather than inventing. The skill produces an honest skeleton that prompts the user for what's missing, not a plausible-looking but ungrounded brand library.

**Do not clobber existing work.** When the detection sweep at Phase 0 finds existing brand assets, default to **preserve and surface** rather than overwrite. The user can always ask for more aggressive replacement; they can't easily un-overwrite hand-crafted content. See `references/existing-assets.md` for per-scenario guidance.

**Cross-link integrity.** At the end of each phase, run a grep to confirm every cross-link target exists. The pre-launch state often means `PRICING.md` or `MANIFESTO.md` may not exist yet when other docs are being authored — handle this by either omitting the link or annotating "*coming soon*", never by linking to a 404.

**Content filtering on the Covenant.** The Contributor Covenant 2.1 verbatim text triggers output content-filtering due to its explicit enumeration of harassment types. The CODE_OF_CONDUCT template adopts the Covenant by reference (state version, link to canonical text, provide enforcement contact, summarize informationally). This is the same pattern used by Kubernetes, React, Vue, and Rails.

## Resources reference

Templates (in `assets/`):

| Path | Use in phase |
|---|---|
| `brand-docs/BRAND.md.template` | 2 |
| `brand-docs/COPY.md.template` | 2 |
| `brand-docs/MANIFESTO.md.template` | 2 |
| `brand-docs/README.md.template` | 2 |
| `brand-docs/CHEATSHEET.md.template` | 2 |
| `brand-docs/CLAUDE.md.template` | 2 |
| `brand-docs/CHANGELOG.md.template` | 2 |
| `brand-docs/RECIPES.md.template` | 2 |
| `brand-docs/BIOS.md.template` | 4 |
| `brand-docs/FAQ.md.template` | 4 |
| `brand-docs/GLOSSARY.md.template` | 4 |
| `brand-docs/TONE.md.template` | 4 |
| `brand-docs/PRICING.md.template` | 4 |
| `repo-conventions/README.md.template` | 5 |
| `repo-conventions/CONTRIBUTING.md.template` | 5 |
| `repo-conventions/SECURITY.md.template` | 5 |
| `repo-conventions/CODE_OF_CONDUCT.md.template` | 5 |
| `press/press-README.md.template` | 6 |
| `sheets/concept-1200x630.html.template` | 3 |
| `sheets/manifesto-1080x1350.html.template` | 3 |
| `sheets/method-1600x900.html.template` | 3 |
| `sheets/readme-1280x640.html.template` | 3 |
| `sheets/og-1200x630.html.template` | 3 |
| `sheets/poster-1224x1584.html.template` | 3 |
| `sheets/swatch-1584x1224.html.template` | 3 |
| `pipeline/brand.justfile.template` | 3 |

Helper scripts (in `scripts/`):

- `vocab_check.sh` — grep for don't-use vocabulary across brand docs
- `word_count.py` — verify FAQ / bios word counts against bounds

References (in `references/`, loaded as needed):

- `decision-rubric.md`
- `existing-assets.md`
- `directory-structure.md`
- `voice-checks.md`
- `word-count-bounds.md`
- `cross-link-map.md`
- `pre-launch-deferrals.md`
- `additional-asset-types.md`
- `pricing-models.md`
- `license-considerations.md`
