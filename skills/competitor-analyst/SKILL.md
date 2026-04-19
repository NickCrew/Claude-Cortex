---
name: competitor-analyst
description: 'Use this skill when analyzing competitors, building competitive positioning, creating feature comparison matrices, or applying strategic frameworks like SWOT or Porter''s Five Forces. Trigger phrases: ''analyze our competitors'', ''competitive analysis for'', ''how do we compare to'', ''create a feature matrix'', ''SWOT analysis of''. Not for sizing the total market (use market-researcher), writing pitch decks (use pitch-deck-writer), or pricing strategy modeling.'
version: 1.0.0
author: community
tags:
  - business
  - competitive-analysis
  - strategy
  - market
license: MIT
keywords:
  - competitive analysis
  - SWOT
  - feature matrix
  - positioning
  - competitor
  - analyst
  - competitor analyst
---

# Competitor Analyst

## Overview
This skill provides structured frameworks for competitive intelligence—from gathering information on competitors through applying analytical frameworks (SWOT, Porter's Five Forces, positioning maps, feature matrices) to synthesizing insights into strategic recommendations. Good competitive analysis reveals where to attack, where to defend, and how to position your product to win.

## When to Use
- Building a competitive landscape analysis for investors, board, or internal strategy
- Creating a feature comparison matrix for sales or product teams
- Developing a competitive positioning strategy
- Tracking and monitoring competitor moves over time
- Preparing a competitive battle card for sales
- Identifying whitespace opportunities in the market

## When NOT to Use
- Sizing total market opportunity (use market-researcher skill)
- Writing a full pitch deck (use pitch-deck-writer skill)
- Conducting primary research interviews with competitor customers (use ux-researcher skill)
- Financial modeling or pricing analysis (use a finance skill)

## Quick Reference
| Framework | Use Case | Output |
|-----------|----------|--------|
| SWOT Analysis | Internal + external audit per competitor | 2×2 matrix |
| Porter's Five Forces | Industry-level threat assessment | Force ratings + strategy |
| Feature Matrix | Product comparison for sales/product | Comparison table |
| Positioning Map | Visual differentiation | 2×2 or 2-axis plot |
| Battle Card | Sales competitive enablement | 1-page quick reference |
| Win/Loss Analysis | Understanding why deals are won or lost | Pattern report |
| Competitive monitoring | Ongoing intel tracking | Change log |

## Instructions

### Step 1: Define the Scope
Before researching, clarify:
1. **Who are the direct competitors?** (Same product category, same customer)
2. **Who are the indirect competitors?** (Different product, same job-to-be-done)
3. **Who are the potential entrants?** (Not yet competing but could)
4. **What decisions will this analysis inform?** (Positioning, product roadmap, pricing, sales training)

**Competitor tiers:**
| Tier | Description | Example |
|------|-------------|---------|
| Tier 1 (Primary) | Direct, head-to-head competition for same buyer | Feature-for-feature match |
| Tier 2 (Secondary) | Adjacent solutions solving same problem differently | Different approach/category |
| Tier 3 (Indirect) | Status quo / manual alternatives | Spreadsheets, custom-built tools |

### Step 2: Information Gathering
Never rely on competitor websites alone—they only show strengths.

**Primary sources (no login required):**
- Competitor website: positioning, messaging, pricing page, case studies
- Job postings: hiring signals reveal engineering investment, new products, geographic expansion
- Blog and content: what problems they're addressing, thought leadership positioning
- Press releases and news: funding, partnerships, product launches, executive changes
- SEC filings (public companies): actual revenue, customer counts, churn rates

**Review sites (customer voice — most valuable):**
- G2, Capterra, Trustpilot, App Store, Google Play
- Reddit (r/[industry], r/[product category])
- LinkedIn recommendations and testimonials
- Twitter/X: search "[competitor name] sucks" or "[competitor name] alternatives"

**Social signals:**
- LinkedIn company page: growth rate, recent posts, employee count trend
- LinkedIn job postings: volume and department signal investment areas
- GitHub (if relevant): open source activity, developer engagement

**Paid research (optional):**
- SimilarWeb: web traffic estimates and traffic sources
- Crunchbase/PitchBook: funding, investors, valuation signals
- Gartner Peer Insights, Forrester Wave: analyst positioning

**Information to collect per competitor:**
```
Company overview: Founded, HQ, employees, funding, estimated revenue
Target customer: Segment, ICP, use case
Product: Core features, differentiators, recent launches
Pricing: Model (per seat, usage, flat), tiers, pricing page public?
Go-to-market: Sales motion (PLG, inside sales, enterprise sales), channels
Positioning: Tagline, key messages, what they claim to do best
Weaknesses: Negative reviews, common complaints, gaps
Recent moves: Last 3 major announcements or product launches
```

### Step 3: SWOT Analysis
Conduct a SWOT for each major competitor and for your own company.

**Template:**
```
Competitor: [Name]
Date: [Quarter/Year]

STRENGTHS (internal, positive)
- What do they do better than anyone?
- Why do customers choose them?
- What resources/assets give them an advantage?

WEAKNESSES (internal, negative)
- Where do customers complain the most? (G2, Capterra)
- What features are they missing?
- What business model or technical constraints limit them?

OPPORTUNITIES (external, positive)
- What market trends benefit them?
- What adjacent markets could they expand into?
- What partnerships could amplify them?

THREATS (external, negative)
- What could disrupt their current advantage?
- New entrants, regulatory changes, technology shifts?
- How could you attack them?
```

### Step 4: Porter's Five Forces
Apply at the industry level to understand structural attractiveness and competitive intensity.

**Force 1: Threat of New Entrants** (How easy is it to enter this market?)
- High threat: Low barriers to entry, no switching costs, open source alternatives
- Low threat: High R&D cost, regulatory approval needed, strong network effects, data moats

**Force 2: Bargaining Power of Buyers** (How much leverage do customers have?)
- High power: Many alternatives, low switching cost, price-sensitive buyers
- Low power: Switching costs high, product deeply embedded, few alternatives

**Force 3: Bargaining Power of Suppliers** (How dependent are you on key vendors?)
- High power: Few cloud providers, API dependency (OpenAI, Stripe), regulatory monopolies
- Low power: Multiple alternatives, open standards, commoditized inputs

**Force 4: Threat of Substitutes** (Can buyers solve the problem a completely different way?)
- High threat: Problem can be solved with Excel, custom code, manual process
- Low threat: No reasonable substitute; unique technology

**Force 5: Rivalry Among Existing Competitors** (How intense is competition?)
- High rivalry: Commoditized product, price wars, slow market growth
- Low rivalry: Differentiated, fast-growing market, not yet zero-sum

**Strategic implications by force rating:**
```
If buyers have high power → compete on switching costs, contracts, integrations
If new entrants threat is high → build moats (network effects, data, brand, distribution)
If rivalry is intense → differentiate aggressively; avoid head-to-head on price
```

### Step 5: Feature Comparison Matrix
Used by product teams to spot gaps and by sales teams to win deals.

**Matrix template:**
| Feature | Your Product | Competitor A | Competitor B | Competitor C |
|---------|-------------|-------------|-------------|-------------|
| **Core features** | | | | |
| Feature 1 | ✅ Full | ✅ Full | ⚠️ Partial | ❌ No |
| Feature 2 | ✅ Full | ❌ No | ✅ Full | ✅ Full |
| **Differentiating features** | | | | |
| Your key differentiator | ✅ | ❌ | ❌ | ❌ |
| **Integrations** | | | | |
| Salesforce | ✅ | ✅ | ❌ | ✅ |
| Slack | ✅ | ⚠️ Beta | ✅ | ❌ |
| **Commercial** | | | | |
| Pricing (per seat/mo) | $15 | $20 | $12 | $18 |
| Free plan | ✅ | ❌ | ✅ | ❌ |
| Enterprise tier | ✅ | ✅ | ❌ | ✅ |
| SOC 2 Type II | ✅ | ✅ | ❌ | ✅ |

Legend: ✅ Full support | ⚠️ Partial/Beta | ❌ Not available

### Step 6: Positioning Map
A 2-axis map reveals whitespace and where you're differentiated.

**Process:**
1. Choose two dimensions that matter most to buyers (not two where you win automatically)
2. Common axis pairs:
   - Price (budget → premium) × Ease of use (complex → simple)
   - Target user (SMB → Enterprise) × Feature breadth (focused → all-in-one)
   - Deployment (cloud → on-prem) × Customization (out-of-box → highly custom)
3. Plot each competitor as a point; plot yourself
4. Find the whitespace (empty quadrant) = positioning opportunity

**Interpretation:**
- Top-right quadrant occupied = premium segment is crowded
- Bottom-left gap = opportunity for a simple, affordable solution
- Your position should be in a quadrant competitors can't easily enter

### Step 7: Build a Battle Card (Sales Enablement)
A battle card is a 1-page cheat sheet for sales reps facing a specific competitor.

**Battle card structure:**
```
COMPETITOR: [Name]
When you encounter them: [Trigger signals — what they say, what buyer says]

WHY WE WIN
- [Differentiator 1 in customer language]
- [Differentiator 2 in customer language]
- [Differentiator 3 in customer language]

THEIR STRENGTHS (acknowledge honestly)
- [Strength 1] — our response: "That's true, and..."
- [Strength 2] — our response: ...

LANDMINES (questions to ask that expose competitor weaknesses)
- "How does [Competitor] handle [scenario where they're weak]?"
- "What happens when your team grows past [their scaling limit]?"
- "Have you tried to export your data? How long did that take?"

TRAPS (what they'll say about us — and our counter)
- They say: "You're more expensive." Counter: "Our LTV:CAC data from customers shows..."
- They say: "You're a startup." Counter: "[Customer logos] trusted us with mission-critical work"

PROOF POINTS
- Win against this competitor: [Customer name/industry] chose us because [reason]
- G2 rating: Ours [X.X] vs theirs [Y.Y]
```

## Examples

### Example 1: Analyze 3 Competitors for a Project Management Tool

**Context:** New project management tool targeting engineering + product teams. Analyzing Jira, Linear, and Asana.

**Research sources used:** G2 reviews (50 per competitor), pricing pages, job postings, Twitter, Reddit r/projectmanagement.

**Summary findings:**

| Dimension | Jira | Linear | Asana |
|-----------|------|--------|-------|
| **Target user** | Enterprise engineering | Engineering-forward teams | Any team (marketing, ops, eng) |
| **Core strength** | Deep customization, Atlassian ecosystem | Speed, developer UX, GitHub integration | Workflow automation, breadth |
| **Pricing** | $8.15/user/mo (Standard) | $8/user/mo | $13.49/user/mo |
| **Key weakness (from reviews)** | "Too complex for smaller teams", "setup takes months" | "Not suitable for non-eng teams", "limited reporting" | "Expensive at scale", "too many features = complexity" |
| **Recent move** | AI features in Jira (2024) | Launched Cycles (sprint-like) | Acquired Asana AI assistant |

**Positioning gap identified:** No tool strongly serves *mixed teams* (engineering + product) with fast UX AND non-developer accessibility. Jira is too heavy; Linear is too dev-focused; Asana is too generic.

**Recommended positioning:** "The project management tool for product teams that ship software — fast like Linear, accessible like Asana."

---

### Example 2: Feature Comparison Matrix for a Project Management Tool

| Feature | Our Tool | Jira | Linear | Asana |
|---------|----------|------|--------|-------|
| GitHub integration (2-way) | ✅ | ✅ | ✅ | ⚠️ 1-way |
| AI standup summary | ✅ | ⚠️ Beta | ❌ | ⚠️ Limited |
| Non-eng team support | ✅ | ⚠️ | ❌ | ✅ |
| Sprint planning | ✅ | ✅ | ✅ | ⚠️ |
| Setup time | < 30 min | Days–weeks | < 1 hour | 1–2 hours |
| Free plan | ✅ | ✅ | ❌ | ✅ |
| Pricing (team) | $12/user | $8.15/user | $8/user | $13.49/user |
| SOC 2 Type II | ✅ | ✅ | ✅ | ✅ |
| Mobile app | ✅ | ✅ | ✅ | ✅ |
| Advanced reporting | ⚠️ | ✅ | ⚠️ | ✅ |

**Analysis:** Our key differentiators are AI-native standup summaries and mixed-team support. Our gap: advanced reporting needs investment before pursuing enterprise deals.

## Best Practices
- Update competitive analysis quarterly — markets move fast; a stale battle card hurts sales
- Focus on customers' words in reviews, not your interpretation — use direct quotes
- Acknowledge competitor strengths honestly; dismissing them makes you look naive
- Differentiate on outcomes for customers, not features ("you'll ship 2× faster" not "we have better sprints")
- Win/loss analysis is the most valuable input to competitive analysis — run it after every deal
- Track competitor job postings monthly — what they're hiring reveals where they're investing

## Common Mistakes
- Defining competitors too narrowly (forgetting indirect competitors and status quo)
- Only researching competitor websites — they only show strengths; reviews show weaknesses
- Building a feature matrix where you win every row — it signals you designed the matrix, not reality
- Ignoring new entrants with different business models (Figma didn't beat Sketch on features; it beat it on collaboration)
- Making competitive claims you can't substantiate (legal risk + credibility risk)
- Analysis without recommendation — "here's what competitors do" is not useful; "here's how we win" is

## Tips & Tricks
- Read 3-star G2 reviews for the most balanced perspective on competitors (1-star = angry outliers, 5-star = superfans)
- Track competitor job postings monthly in a spreadsheet — volume and role type predict product direction
- "Alternatives to [competitor]" search queries surface what problems buyers have with competitors
- Ask your own churned customers "what did you evaluate before choosing us?" and "what would make you switch?" — this is primary competitive intel
- A "competitive kill sheet" with 3 landmine questions per competitor is often more valuable to sales than a 20-page analysis

## Related Skills
- [market-researcher](../../business/market-researcher/SKILL.md)
- [pitch-deck-writer](../../business/pitch-deck-writer/SKILL.md)
- [business-analyst](../../business/business-analyst/SKILL.md)
- [product-manager](../../business/product-manager/SKILL.md)
