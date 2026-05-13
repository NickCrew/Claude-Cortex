# Additional visual asset types

The skill ships HTML templates for the 5 highest-leverage visual asset types: concept poster, manifesto card, methodology one-pager, README banner, OG image. The asset types below are common in mature brand libraries but not templated — extend the pattern when needed.

## When to extend

Most brand libraries don't need all of these. Add them when the use case is real:

- Carousel — when the product has a deck-format social presence (LinkedIn, IG carousels)
- Story — when the product has a vertical-video / IG Stories presence
- Principle cards — when the manifesto has 2-4 quotable principles worth a dedicated visual
- Promo banners — when launching, running ad campaigns, or marking limited-time states
- Email header — when running newsletters or transactional email with brand chrome
- Square social — when posting to feeds where 1:1 is the primary aspect (IG, LinkedIn)
- Editorial / typographic hero — when the brand benefits from a typography-led variant (in addition to mark-led)

## Pattern guidance

Each type below has:
- Canonical dimensions
- Layout pattern
- When to use / not use
- Pipeline notes (if rendering specifics differ from the standard recipe)

### Carousel (multi-slide deck)

**Dimensions:** 1080×1350 (LinkedIn / IG carousel portrait) per slide. Typically 5–10 slides.

**Layout pattern:** sequential slides, each carrying one beat of the argument. Slide 1 is the cover (tagline + brand mark); intermediate slides each make one structural claim; final slide is the close (locked hero or CTA). Number the slides ("01 / 05") so readers track progress.

**When to use:** brand storytelling on social platforms that support multi-image posts. Compresses the manifesto argument into a swipeable format.

**When not:** if the product has no social-deck channel, skip — carousels only render value on the platform that displays them.

**Pipeline:** add per-slide CSS scoping (each slide is a separate `<div id="carousel-N">` inside the same HTML file). Render each slide as a separate variant via Playwright URL hash. Convert to PNG/WebP per slide.

### Story (vertical mobile)

**Dimensions:** 1080×1920 (IG Stories, Snap, vertical YouTube Shorts thumbnails).

**Layout pattern:** vertical hero composition. Brand mark + tagline at top; locked hero in middle; trust line + URL at bottom. Use ample negative space — story format is consumed full-screen.

**When to use:** brand presence on platforms with story features.

**When not:** if the product audience doesn't use story platforms.

**Pipeline:** standard concept-sheet pattern with portrait dimensions.

### Principle cards (1080×1080 quote cards)

**Dimensions:** 1080×1080 square.

**Layout pattern:** large central quote in display serif italic, brand-color accent on the key word. Attribution / context line below. Brand mark + URL in footer. One quote per card.

**When to use:** when the manifesto has 2-4 phrases that are quotable in their own right and benefit from individual visual treatment. Examples from Facet: "Same diamond · Different face" / "Correction over creation" / "A deep model of you, professionally."

**When not:** if the manifesto doesn't have standalone quotable phrases yet, defer.

**Pipeline:** standard square format. Multiple variants in one HTML file (one card per `<div id="principle-{slug}">`).

### Promo banner

**Dimensions:** 1200×630 (OG-aspect) — same as standard banners but with a launch-state badge.

**Layout pattern:** standard banner layout + a "● LAUNCHING / NOW AVAILABLE / OPEN SOURCE" pill badge. The pill is the differentiator from other banners; everything else is standard.

**When to use:** marketing pushes — launch announcement, public release, milestone marker.

**When not:** during steady-state. Promo banners that say "now available" indefinitely after launch read as stale; either swap the badge text to something durable ("OPEN SOURCE") or retire the variant.

**Pipeline:** subclass of the standard banner template; just adds the badge component.

### Email header masthead

**Dimensions:** 1200×400 (typical newsletter header), display sized at 600×200.

**Layout pattern:** brand mark + wordmark at left, tagline at right. Compact horizontal composition.

**When to use:** running a newsletter, transactional emails with branded chrome, launch announcement emails.

**When not:** if email isn't a brand surface.

**Pipeline:** standard horizontal template, sized to email header dimensions.

### Square social post

**Dimensions:** 1080×1080.

**Layout pattern:** brand mark prominent (top-center or center), locked hero in middle, trust line + URL at bottom. Compositionally similar to OG image but at 1:1 aspect.

**When to use:** IG / LinkedIn / Threads feed posts where 1:1 is the canonical aspect.

**When not:** if the social presence is text-led rather than image-led.

**Pipeline:** standard square template.

### Editorial / typographic hero

**Dimensions:** 1200×630 (banner-aspect).

**Layout pattern:** typography-led — large display serif as the hero element, no gem mark prominently shown. Used as a counterpoint to the mark-led atmospheric / bold heroes. Showcases the brand's typography choice as an identity marker in itself.

**When to use:** when the brand has strong typography (custom or distinctive font) and benefits from a hero variant that leads with type rather than mark.

**When not:** if the brand mark is the strongest identity element and typography is supporting.

**Pipeline:** standard banner format with type-led layout instead of mark-led.

## Pattern for extending the pipeline

When adding a new asset type:

1. Create the HTML sheet at `brand/_source/html/{type}.html` following the patterns in the templated sheets (per-variant CSS scoping, render-mode handler, brand color/typography variables).
2. Add a new `brand-{type}` recipe to the justfile (model on `brand-method` for widescreen, `brand-manifesto` for portrait, etc.).
3. Add a matching `brand-clean-{type}` recipe that enumerates exactly the files that recipe produces (do **not** use `rm -rf` on the category directory — Adobe Illustrator exports may share that directory and the same `{{PRODUCT_SLUG}}-*` prefix).
4. Add the new render recipe to the `brand` umbrella; chain the cleanup recipe from `brand-webp-clean`.
5. Create `brand/exports/{type}/` directory.
6. Optionally add a composite reference sheet section showing all variants together (model on existing composite sections).
7. Update `brand/BRAND.md` inventory tree to reflect the new asset type.
8. Log the new asset type in `brand/CHANGELOG.md`.

## Anti-pattern: too many asset types

A brand library with 50 asset types is *worse* than one with 10. Each type costs maintenance:

- Render pipeline sheet to keep up to date
- Asset variants to re-render when brand changes
- Composite reference sheet to track
- Documentation to maintain

Add asset types when there's a clear use case, not because they exist as a category. The 5 templated types cover the vast majority of needs; the additional types above are extensions, not requirements.
