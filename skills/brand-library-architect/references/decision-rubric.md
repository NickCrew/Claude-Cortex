# Phase 0 — Decision rubric

The upfront questionnaire that gates every other phase. Output: `brand/decisions.md` capturing all answers. Do not start subsequent phases until the user has answered these (or explicitly recorded a gap).

## How to elicit decisions

Ask in clusters, not all at once. Most users have ready answers for some clusters and need to think about others. The clusters below are ordered roughly easiest → hardest.

### Cluster 1: Product identity (usually fast)

1. **Product name** — exactly as it should appear in the wordmark
2. **Product domain** — primary URL (e.g. `myfacets.cv`)
3. **Repo URL** — GitHub / GitLab / etc. URL for source
4. **Contact email** — canonical brand contact (used in SECURITY, press kit, README)

### Cluster 2: Voice anchors (the hardest, most important)

5. **Brand verb** — the *owned* action word. Examples: Facet's "recut," not "tailor." Stripe's "build," not "implement." Vercel's "deploy," not "publish." Should be:
   - Categorically distinct from competitor vocabulary
   - Structurally tied to product metaphor
   - Single syllable / short / verb-able
   
   If the user can't name one yet, this is the most-important blocker — work with them to find it. A brand without an owned verb has no voice.

6. **Durable noun** — the *thing* the user builds / has / does with the product. Facet's "model" (not profile / data / story). Stripe's "integration" (not setup / config). Should be the noun that pairs naturally with the brand verb.

7. **Tagline** — short structural claim. Facet: "Same diamond · Different face." Should be 5–8 words, declarative, captures the product thesis. If absent, prompt for it now; if user is stuck, defer until manifesto-writing surfaces the right phrase.

8. **Locked hero copy** — the 1–2 sentence positioning statement. Facet: "A deep model of you, professionally. *Recut for every opportunity.*" Should:
   - Use the brand verb
   - Use the durable noun
   - Be declarative (not a question, not a feature list)
   - Have a noun-then-verb-claim structure that survives compression

9. **Trust line** — the credibility-promise pair. Facet: "Open-source · Your data, never ours." Should pair a structural credential (open-source / SOC2 / etc.) with a direct promise. Often skippable for non-OSS products that don't have strong data-promise differentiation.

### Cluster 3: Visual identity

10. **Primary brand color** — single hex. The "when in doubt" color. Facet: `#2d6a96`.

11. **Color palette extension** — secondary brands, accents, status colors (success/warning/error). Optional at Phase 0; can defer to Phase 1 BRAND.md authoring.

12. **Typography choices**:
    - Body: usually a system or web font (Inter / DM Sans / Source Sans / etc.)
    - Mono: for code / technical metadata (DM Mono / IBM Plex Mono / etc.)
    - Wordmark: the lockup font (Instrument Serif / serif display / custom)
    - Display: hero text on marketing surfaces (Outfit / Geist / etc.)

13. **Logo / mark concept** — describe the visual idea. Facet: "two-tone shield-cut gem with diagonal split." If the user has SVGs already, point at those. If not, defer to a separate design pass — the brand library can be built around placeholder marks and the marks can be designed in parallel.

### Cluster 4: License and pricing

14. **License**:
    - **AGPL-3.0** — most aggressive copyleft; network-use clause means SaaS modifications must be open. Good when the product wants to be the canonical hosted version.
    - **GPL-3.0** — strong copyleft without the network-use clause.
    - **Apache-2.0** — permissive with patent grant. Good for commercial-friendly OSS.
    - **MIT** — most permissive. Good when adoption matters more than reciprocity.
    - **BSD** variants — similar to MIT.
    - **Source-available / proprietary** — not OSS; skip CONTRIBUTING / CODE_OF_CONDUCT.
    
    See `license-considerations.md` for which conventions ship per license.

15. **Pricing model**:
    - **Episodic pass** — one-time purchase, fixed-duration window, no subscription. Used by Facet ($299 / 90-day pass / 12-month consumption window / 7-day refund).
    - **Subscription** — monthly / annual recurring. Standard SaaS. Specify: monthly price, annual discount (if any), free tier scope.
    - **Freemium** — free baseline + paid tier. Specify: what's free, what's paid, paid pricing.
    - **Free / OSS-only** — no paid product. Skip PRICING.md; adapt FAQ pricing answer.
    - **Open-core** — OSS core + commercial extensions. Specify which features are commercial.
    
    See `pricing-models.md` for the PRICING.md template variants per model.

### Cluster 5: State and distribution

16. **Pre-launch state** — yes / no. Affects:
    - "Currently preparing for public launch" language in BIOS / press kit
    - Deferral of customer testimonials, coverage clips, hosted screenshots
    - Whether public-URL references work or need "coming soon" annotations
    
    See `pre-launch-deferrals.md` for the full list.

17. **Distribution domain for public docs** — where MANIFESTO / PRICING / press will eventually live as URLs (`{{DOMAIN}}/manifesto`, `{{DOMAIN}}/pricing`, `{{DOMAIN}}/press`). Even if the URLs don't exist yet, commit to the convention so brand assets can reference them post-launch.

## Recording the decisions

Output `brand/decisions.md`:

```markdown
# Brand decisions

## Identity
- Product name: {{PRODUCT_NAME}}
- Domain: {{DOMAIN}}
- Repo: {{REPO_URL}}
- Contact: {{CONTACT_EMAIL}}

## Voice anchors
- Brand verb: {{BRAND_VERB}}
- Durable noun: {{DURABLE_NOUN}}
- Tagline: {{TAGLINE}}
- Locked hero: {{LOCKED_HERO}}
- Trust line: {{TRUST_LINE}}

## Visual identity
- Primary color: {{PRIMARY_HEX}}
- Color palette: {{PALETTE_SUMMARY}}
- Typography: body {{BODY_FONT}}, mono {{MONO_FONT}}, wordmark {{WORDMARK_FONT}}, display {{DISPLAY_FONT}}
- Mark concept: {{MARK_CONCEPT}}

## License & pricing
- License: {{LICENSE}}
- Pricing model: {{PRICING_MODEL}}
- Pricing detail: {{PRICING_SPECIFICS}}

## State
- Pre-launch: {{YES_NO}}
- Public domain: {{PUBLIC_DOMAIN}}

## Gaps (decisions deferred)
- {{LIST_DEFERRED_DECISIONS}}
```

Subsequent phases reference `decisions.md` rather than re-prompting the user. If a gap blocks a specific deliverable, surface it at that point ("FAQ pricing answer needs the price — Phase 0 left it as TBD; what's the number?").
