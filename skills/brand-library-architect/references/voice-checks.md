# Voice checks — don't-use vocabulary

Generic vocabulary that flattens any brand into the SaaS-startup category. The product-specific don't-use list goes into `COPY.md` "What NOT to use" table during Phase 1.

## Default don't-use list (seed for COPY.md)

These are flagged for almost any product. Adapt and extend per product.

| Don't use | Use instead | Why |
|---|---|---|
| Tailor (the X) | {{BRAND_VERB}} | "Tailor" is shared across the entire SaaS-resume / SaaS-content category |
| Generate (a / the X) | {{BRAND_VERB}} / Build / Refine | "Generate" implies one-shot AI; products that *refine* should reject this verb |
| Optimize | (often unnecessary) | Empty utility verb; remove or be specific |
| Customize | {{BRAND_VERB}} | Customize is generic; the brand verb is structural |
| Profile | {{DURABLE_NOUN}} | "Profile" suggests presentation layer; products with substrate should claim the noun |
| Career platform / Customer platform / etc. | (concept name) | "Platform" is generic; brand-defined OS / system concept claims more |
| Coach / coaching | (don't use unless coaching is the actual product) | Avoid the consultant register if the product is a tool, not a service |
| Job seeker / customer base / user persona / etc. | (rephrase) | These center the user on a transient activity / pigeonhole; rephrase in the user's own terms |
| Career journey / customer journey / X journey | (rephrase) | Cliché. Use specific structural language ("the search loop", "the recut cycle") |
| Stand out | (rephrase) | Empty competitive framing; the brand should claim a different category, not "stand out" within an existing one |
| Game-changing | (avoid) | Hyperbolic; fails the "would a competitor's landing page say this?" check |
| Revolutionary | (avoid) | Same as game-changing |
| Next-generation | (avoid) | Same |
| AI-powered (as label) | Describe what the system DOES | Don't lead with the underlying tech; describe extracts / refines / recuts / etc. |
| Unleash your X | (avoid) | Aspirational fluff |
| Take your X to the next level | (avoid) | Empty progression framing |
| Not just X, but Y | (avoid) | Empty contrast pattern |
| {{COMPETITOR_VERB}} | {{BRAND_VERB}} | Whatever the dominant verb in the user's category is — claim a different one |

## Vocabulary check workflow

1. After authoring any brand doc, grep for the don't-use words:

```bash
grep -i -n -E "tailor|generate|optimize|customize|profile|career platform|coach|stand out" brand/*.md
```

2. Inspect each hit:
   - In a "Don't use X" callout? → fine, expected
   - In an "Avoid example" / TONE.md don't-use block? → fine, expected
   - In a positive use describing the product? → flag for rewrite

3. Use the `scripts/vocab_check.sh` helper for the full list.

## Voice register defaults

These apply unless the product has a specific reason to deviate. Document deviations in COPY.md "Voice and register."

- **Declarative, not aspirational.** State the claim directly. "X is Y" beats "What if X could be Y?"
- **Senior register.** The reader is a peer, not a prospect.
- **Italic accent on display titles.** The italic word is the brand-claim noun, set in display-serif italic (Instrument Serif / Playfair) in brand color.
- **Mono uppercase for system metadata.** `v3 · public`, `01 / 02 / 03`. The register that says "this is a spec, not a marketing promise."
- **Owned verbs over generic.** Brand verb consistently. Don't alternate with synonyms.
- **Em-dash policy.** Display copy may use connective em dashes for rhythm; long-form prose avoids them. Document the carve-out in COPY.md "Voice and register."

## Tonal moves to avoid

- Hyperbolic claims, especially in adjective-heavy copy.
- Empty rhetorical questions ("Have you ever wondered...?").
- "AI-powered" as a marketing label.
- Stack-of-emoji decoration in social copy.
- "We're excited to announce..." in release notes.
- Pleasantry-padding before the answer in support replies.
- Marketing-speak that could appear on any B2B SaaS landing page.

## Product-specific extensions

The default list is a seed. The product likely has a small number of *additional* don't-use words specific to its category:

- A career-search product avoids "auto-apply," "career platform," "stand out from the crowd."
- A finance product might avoid "fintech," "disrupting banking," "financial wellness."
- A developer product might avoid "developer experience" (everyone says this).

Ask the user: "What 3–5 phrases do you hear competitors say that you specifically don't want to use?" Add those to the COPY.md don't-use table.
