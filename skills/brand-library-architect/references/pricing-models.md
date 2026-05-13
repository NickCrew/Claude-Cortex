# Pricing models

Guidance for which `PRICING.md` sections to keep / cut based on the user's pricing model. The PRICING.md template supports all four models below via `{{PRICING_MODEL}}` switching.

## Episodic pass

**Pattern:** one-time purchase, fixed-duration window, no recurring charge. Used by Facet ($299 / 90-day pass / 12-month consumption window / 7-day refund).

**Why this model fits:** when usage is bursty rather than continuous. Career-search, tax season, project-bound work, seasonal businesses. The pass duration matches the actual work; subscription would charge during off-time.

**PRICING.md sections to keep:**
- Quick facts (price, pass duration, usage window, refund)
- Why episodic passes (the misalignment-of-incentives argument vs subscription)
- Why not subscription (alignment, not price)
- What stays mine after the pass closes
- Comparison to subscription competitors (alignment axis)
- Refund and pause mechanics

**PRICING.md sections to cut:**
- "Cancel subscription anytime" (no subscription to cancel)
- "Annual discount" (no annual)
- Tier comparison tables (typically one tier in pass model)

## Subscription (monthly / annual)

**Pattern:** recurring charge, ongoing access, cancellable. Standard SaaS.

**Why this model fits:** when usage is continuous and the product compounds value over time. Most B2B SaaS, productivity tools, communication platforms.

**PRICING.md sections to keep:**
- Quick facts (monthly / annual price, free trial if any, refund policy)
- Tier comparison (Free / Pro / Enterprise) if multi-tier
- "Cancel anytime" with what stays mine after cancel
- Annual discount (if any)
- Refund policy

**PRICING.md sections to cut:**
- "Why episodic passes" (use a different "why subscription" argument)
- "Why not subscription" (irrelevant)

**Customize:** the "alignment of incentives" argument inverts — subscription is honest *if* the product is used continuously and the team commits to building features that prevent churn (rather than features that punish leaving).

## Freemium

**Pattern:** free baseline + paid upgrade tier(s).

**Why this model fits:** when the product has a viral / network-effect dynamic where free users create value for paid users (or for the platform); when adoption matters more than revenue per user.

**PRICING.md sections to keep:**
- Free tier scope (what's included, what's not)
- Paid tier(s) — tier comparison table
- Why these specific gating choices (the pricing argument is "what's worth paying for vs what's the table-stakes free experience")
- Upgrade path (when does a free user benefit from upgrading)

**PRICING.md sections to cut:**
- "Why episodic" / "why not subscription" — rephrase the argument around free-vs-paid gating

## Free / OSS-only

**Pattern:** no paid product. Optional donation links / sponsorship.

**Why this model fits:** developer tools, libraries, projects funded by other revenue (employer / consulting / grants).

**PRICING.md sections to keep:**
- Statement that the product is free and OSS
- License (link to LICENSE)
- Optional: sponsorship / donation links (GitHub Sponsors, OpenCollective)
- Optional: commercial-support pricing (if the maintainer offers paid support / consulting)

**PRICING.md sections to cut:**
- Most of the doc. Free OSS rarely needs a long PRICING.md; the FAQ pricing answer (1 line) plus the LICENSE may be enough. Skip PRICING.md entirely if there's no story to tell.

**FAQ pricing answer (free / OSS):**

> What does it cost?
>
> Nothing. Facet is free, open-source under {{LICENSE}}. Self-host on
> your own infrastructure or use the hosted version (where applicable)
> for free.

## Open-core

**Pattern:** OSS core + commercial extensions / hosted enterprise tier.

**Why this model fits:** developer infrastructure (databases, CI/CD, observability) where the OSS core drives adoption and the commercial tier captures enterprise budget.

**PRICING.md sections to keep:**
- What's OSS (free, the core)
- What's commercial (the enterprise tier — features, support, SLA)
- Pricing for the commercial tier (or "Contact sales")
- Cross-link to the LICENSE for the OSS core, and the commercial license for the paid tier

**PRICING.md sections to cut:**
- Single-tier framing (this model has two)

## Hybrid pricing notes

**Internal vs public.** If the product has internal billing/entitlement docs (Stripe integration, Wave 1 entitlement spec, etc.), check those before committing PRICING.md. A public-facing PRICING.md that contradicts the internal billing implementation creates downstream confusion. Surface the conflict to the user; don't silently pick one side.

**Brand-led-product is fine.** It's reasonable for brand to commit to a pricing argument before the implementation switches (e.g., the brand decides "we sell passes" before Stripe is reconfigured from subscription products to one-time-payment products). Document the gap in `decisions.md` and file a small follow-up task to update the implementation doc.

**Don't write pricing copy that goes stale fast.** Avoid "currently $299" without a "as of {{DATE}}" or version annotation. Avoid quoting competitor prices unless paired with a date — competitor prices change.
