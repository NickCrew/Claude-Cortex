# Pre-launch deferrals

Things to defer when the product is pre-launch. Note them explicitly in the brand docs ("What's not here yet" sections) so absent material is understood as intentional, not missing.

## What to defer pre-launch

| Item | Where it would otherwise live | Reason for deferral |
|---|---|---|
| Customer testimonials | press kit, landing page, BIOS | No customers yet; can't fabricate |
| Case studies | press kit, blog | Same |
| Press quotes / coverage clips | press kit | No coverage yet |
| Hosted-product screenshots | README, press kit, marketing | UI may shift before launch; screenshots go stale |
| Specific public-URL references | brand assets (footers, links) | Domain may not be live; baking URLs creates 404 traps |
| "Trusted by 10,000+ users" / scale claims | landing page, pitch deck | Not true yet; don't fabricate |
| Discount codes / promo programs | PRICING.md, FAQ | Not real yet |
| Enterprise / team plans | PRICING.md | Not real yet |
| Founder photo / team photo | press kit | Optional; defer until photo session happens |
| API documentation | docs/ | Defer until API is stable enough that docs won't drift each week |

## Pre-launch language patterns

Use these phrasings to convey "real but not yet shipped":

- "Currently preparing for public launch."
- "When the public site lands, this will mirror to {{DOMAIN}}/{{path}}."
- "Public URL pending."
- "(Available on request before launch; will be in this kit once the first version ships.)"

Avoid these phrasings (they confuse readers about what's real):

- ❌ "Coming soon!" (vague; sounds marketing-y)
- ❌ "Beta access available" (unless it actually is)
- ❌ "Sign up for early access" (unless that signup actually exists)

## Press-kit "What's not here yet" pattern

Include in `brand/press/README.md`:

```markdown
## What's not here yet

This is a pre-launch press kit. Some standard press-kit content is
deliberately absent until it exists:

- **Customer testimonials, case studies, coverage clips** — no users
  yet. Will populate after public launch.
- **Hosted-product screenshots** — UI may shift before launch.
  Available on request for context, but not packaged here until
  stable.
- **Specific pricing detail beyond the headline** — see [`PRICING.md`](../PRICING.md)
  for the full argument; specific tier breakdowns wait on launch.
- **Public press contact form** — `{{DOMAIN}}` doesn't yet have a
  `/press` page. When it does, the canonical URL for this material
  will be `{{DOMAIN}}/press`.
```

This signals deliberate absence; a journalist reading it understands the gap is intentional rather than missing.

## When to update post-launch

Once the product launches:

1. Remove "currently preparing for public launch" language across BIOS, press kit, README.
2. Replace public-URL "pending" notes with live links.
3. Add a "What's not here yet" → "What's not here" sweep, removing items that no longer apply.
4. Begin populating customer testimonials / coverage clips as they accrue.
5. Audit screenshots; replace pre-launch placeholders with current production UI.

This is a separate small task to file when launch happens.
