---
name: market-researcher
description: 'Use this skill when sizing a market, analyzing competitors, designing customer surveys, segmenting audiences, or synthesizing research into market insights. Trigger phrases: ''size the market for'', ''analyze our competitors'', ''who is our target customer'', ''design a survey to understand'', ''TAM/SAM/SOM for''. Not for building financial models, writing pitch decks, or conducting UX usability research.'
version: 1.0.0
author: community
tags:
  - business
  - market-research
  - analysis
  - competitive
license: MIT
keywords:
  - market sizing
  - TAM SAM
  - customer survey
  - competitive
  - market
  - researcher
  - market researcher
---

# Market Researcher

## Overview
This skill guides structured market research—from estimating market size using TAM/SAM/SOM through primary and secondary research design, customer segmentation, survey construction, and competitive landscape analysis. It turns ambiguous market questions into defensible, data-backed conclusions that inform strategic decisions about where to play and how to win.

## When to Use
- Sizing a new market opportunity before investing in product development
- Analyzing competitor strengths, weaknesses, and positioning
- Designing a customer survey to understand needs or validate assumptions
- Segmenting a customer base to find the most valuable groups
- Preparing market analysis for a pitch deck, board presentation, or strategic plan
- Understanding why customers choose or leave a product

## When NOT to Use
- Conducting usability testing or user interviews about product UX (use ux-researcher skill)
- Building detailed financial models or revenue projections (use a finance skill)
- Writing the full pitch deck (use pitch-deck-writer skill)
- Real-time social media monitoring or sentiment analysis

## Quick Reference
| Research Task | Method | Time Required |
|--------------|--------|---------------|
| Market sizing | TAM/SAM/SOM (top-down + bottom-up) | 2–8 hours |
| Competitor analysis | Framework + web research | 4–12 hours |
| Customer needs | 8–12 in-depth interviews | 2–3 weeks |
| Hypothesis validation | Survey (n=200+) | 1–2 weeks |
| Customer segmentation | Survey + cluster analysis | 2–4 weeks |
| Positioning map | Perception survey or desk research | 1–3 days |
| Secondary research | Reports, databases, news | 2–8 hours |

## Instructions

### Step 1: Define the Research Question
Before gathering data, write a single crisp research question:
- "What is the addressable market for AI-powered legal contract review in the US?"
- "Why do users cancel within 30 days of signing up for our product?"
- "How does our product compare to competitors on features and pricing?"

Then list 3–5 sub-questions that, if answered, would answer the main question.

### Step 2: Market Sizing — TAM / SAM / SOM

**Definitions:**
- **TAM** (Total Addressable Market): Total revenue available if you captured 100% of the market
- **SAM** (Serviceable Addressable Market): The portion you can realistically target given your business model, geography, and product
- **SOM** (Serviceable Obtainable Market): What you can realistically capture in 3–5 years

**Two approaches to triangulate:**

**Top-Down (use industry reports):**
```
TAM: Find total industry revenue from analyst reports (Gartner, IDC, Statista)
     Example: "Global legal tech market: $29B (2024)" → TAM = $29B

SAM: Apply your segment filters
     "AI-specific legal tech, US only, mid-to-large law firms" = 15% of global market
     SAM = $29B × 15% = $4.4B

SOM: Apply your achievable market share
     "Realistic 3% capture in 5 years" → SOM = $4.4B × 3% = $132M
```

**Bottom-Up (use unit economics):**
```
# Count the buyers × their spend

Target customers: US law firms with 50+ attorneys = 8,000 firms
Average annual contract value (ACV): $25,000
Total SAM = 8,000 × $25,000 = $200M/year

SOM: Win 500 firms in 5 years → 500 × $25,000 = $12.5M ARR
```

> **Best practice**: Use both approaches; if they're within 2× of each other, your estimate is credible. If they diverge more, investigate why.

**Data sources for market sizing:**
- Gartner, Forrester, IDC, Grand View Research (paid)
- Statista, IBISWorld (paid, often available via library)
- Census Bureau, BLS, SEC filings (free)
- LinkedIn Sales Navigator (estimate company counts)
- Crunchbase, PitchBook (funding and revenue signals)
- Job posting counts (proxy for company growth in a segment)

### Step 3: Primary vs Secondary Research

**Secondary research** (desk research — start here):
- Industry analyst reports (Gartner Magic Quadrant, Forrester Wave)
- Competitor websites, pricing pages, job postings, press releases
- App store reviews of competitor products
- Reddit, Twitter, G2, Capterra, Trustpilot — customer voice
- Government databases (Census, USPTO, SEC EDGAR)
- Academic papers, conference proceedings

**Primary research** (you collect — for validation and nuance):
| Method | Best For | Sample Size |
|--------|----------|-------------|
| In-depth interviews | Deep understanding of motivations | 8–15 |
| Online surveys | Quantifying preferences, segmentation | 200–1,000+ |
| Focus groups | Concept testing, early ideation | 2 groups of 6–8 |
| Observational/ethnography | Understanding actual behavior | 5–10 sessions |
| A/B tests | Validating specific hypotheses | 1,000+ per variant |

### Step 4: Survey Design
A good survey:
1. Takes < 10 minutes (15 questions max)
2. Asks one thing per question
3. Progresses from general to specific
4. Uses consistent rating scales (always 1–5 or always 1–7; never mix)
5. Ends with demographics and open-ended "anything else?"

**Question type guide:**
- **Multiple choice (single)**: When answers are mutually exclusive ("Which best describes your role?")
- **Multiple choice (multi-select)**: "Which of these tools do you use?" (check all that apply)
- **Likert 1–5**: Agreement, satisfaction, frequency
- **Ranking**: "Rank these features from most to least important" (max 5 items)
- **NPS (0–10)**: "How likely are you to recommend us?"
- **Open-ended**: "What is the biggest challenge you face with X?" (use sparingly, 1–2 max)

**Sample survey structure:**
```
Section 1: Screener (1–2 questions to qualify respondents)
Section 2: Current behavior and pain (3–4 questions)
Section 3: Product/solution fit (3–4 questions)
Section 4: Competitive usage and preferences (2–3 questions)
Section 5: Willingness to pay / pricing (1–2 questions)
Section 6: Demographics (2–3 questions)
```

### Step 5: Customer Segmentation
Segment your market on dimensions that predict purchase behavior:

**B2B segmentation dimensions:**
- Company size (employees, revenue)
- Industry vertical
- Geography
- Tech stack / sophistication
- Buying process (self-serve vs sales-led)
- Use case (primary job to be done)

**B2C segmentation dimensions:**
- Demographics (age, income, education)
- Psychographics (values, lifestyle, attitudes)
- Behavioral (usage frequency, purchase history, NPS)
- Geography

**Segmentation output template:**
| Segment | Size | Description | Primary Need | Channel | ACV |
|---------|------|-------------|-------------|---------|-----|
| Enterprise Legal | 2,000 firms | 500+ attorneys, dedicated IT | Compliance automation | Sales-led | $80K |
| Mid-Market Legal | 6,000 firms | 50–500 attorneys, cost-sensitive | Time savings | PLG + inside sales | $20K |
| Solo/Small Firm | 50,000 firms | <50 attorneys, price-sensitive | Affordable AI assistance | Self-serve | $2K |

### Step 6: Competitive Landscape Analysis
Analyze 5–8 direct and indirect competitors across:

**Feature matrix:**
| Feature | Your Product | Competitor A | Competitor B | Competitor C |
|---------|-------------|-------------|-------------|-------------|
| Feature 1 | ✅ | ✅ | ❌ | ✅ |
| Feature 2 | ✅ | ❌ | ✅ | ❌ |
| Pricing | $X/mo | $Y/mo | $Z/mo | $W/mo |
| Target segment | Mid-market | Enterprise | SMB | Mid-market |

**Positioning map** (2×2 matrix with two dimensions):
- X-axis: Price (budget → premium)
- Y-axis: Ease of use (complex → simple)
- Plot each competitor as a dot; find whitespace = your opportunity

**SWOT analysis per competitor:**
- S: What do they do best? (customer reviews, investor narratives)
- W: Where do they fall short? (negative reviews, high churn signals)
- O: What market trends help them?
- T: What could hurt them (you, regulation, substitutes)?

## Examples

### Example 1: Size the US Online Education Market

**Research question:** What is the market size for AI-powered corporate learning platforms in the US?

**Top-down approach:**
```
Global corporate e-learning market (2024): $50B (Grand View Research)
US share: ~35% → $17.5B US market
AI-enhanced segment: ~20% of corporate e-learning → $3.5B SAM
Target: Mid-to-large enterprises (1,000+ employees) = 40% of market → $1.4B

Realistic 4-year market capture at 2% = $28M ARR
```

**Bottom-up approach:**
```
US companies with 1,000+ employees: ~19,000 (BLS data)
Estimated 25% currently buying L&D platforms: 4,750 companies
Average L&D platform spend: $80K/year
Total SAM: 4,750 × $80K = $380M (conservative; AI premium not modeled)
SOM at 1.5% capture: ~70 companies → $5.6M ARR in Year 3
```

**Synthesis:** Top-down gives $28M, bottom-up gives $5.6M—roughly a 5× gap. Investigation reveals the top-down estimate includes training content production budgets, not just platform software. Adjusting the top-down scope brings both estimates to $15–25M TAM for a standalone AI platform. Credible SOM: $5–10M ARR by Year 4.

---

### Example 2: Analyze Competitor Positioning for a Project Management Tool

**Research question:** How does our new project management tool compare to Asana, Monday.com, and Linear?

**Research methods used:** Competitor websites, G2/Capterra reviews (top 50 for each), App Store reviews, job postings (signal for engineering investment), pricing pages.

**Findings summary:**

| Dimension | Our Tool | Asana | Monday.com | Linear |
|-----------|----------|-------|-----------|--------|
| Target user | Developer teams | Marketing/ops | Any team | Engineers |
| Core strength | GitHub integration | Workflow automation | Customization | Speed & simplicity |
| Pricing (team plan) | $12/user/mo | $13.49/user/mo | $12/user/mo | $8/user/mo |
| Key complaint (G2) | "Missing Gantt view" | "Too complex" | "Expensive at scale" | "Too dev-focused" |
| AI features | ✅ native | ⚠️ limited | ⚠️ limited | ❌ |

**Positioning gap identified:** No competitor strongly serves *mixed teams* (engineering + product + design) with deep GitHub integration + non-developer accessibility. This is the whitespace.

**Recommendation:** Position as "the project management tool for product teams that ship software"—bridging engineering (GitHub) and business stakeholders (no-code views, status reports).

## Best Practices
- Triangulate market size with two methods (top-down + bottom-up) and explain any large gaps
- Primary research validates secondary research; never rely on one source alone
- For surveys, pilot test with 5 people before full launch; fix confusing questions
- When analyzing competitors, focus on customer reviews for weaknesses—competitor websites only show strengths
- Segment by behavior, not just demographics; two people with the same age can have very different buying behavior
- Make assumptions explicit: "We assume 15% of the market is addressable given our current integrations"
- Research findings should lead to a recommendation, not just a data dump

## Common Mistakes
- Reporting TAM as the investment opportunity (it's not; SOM is)
- Conflating total industry spending with the addressable software market
- Survey bias: leading questions, or surveying only existing happy customers
- Treating competitor feature lists at face value without talking to their customers
- Doing only secondary research for important decisions (desk research has survivorship bias)
- Forgetting to validate willingness to pay—a large market of people who won't pay is worthless
- Confusing market size with market demand (a market can be large but already saturated)

## Tips & Tricks
- G2 and Capterra reviews are gold mines—read the 3-star reviews for honest trade-offs
- LinkedIn company search filters (industry + size) let you count companies in a segment for free
- App store reviews sorted by "most recent, 1–2 stars" shows a competitor's current problems
- The "jobs to be done" (JTBD) framework is the best mental model for understanding why customers buy
- Always ask survey respondents "why?" after a rating—open text explains the number
- Job postings reveal where competitors are investing: 10 new ML engineer listings signals an AI product push

## Related Skills
- [competitor-analyst](../../business/competitor-analyst/SKILL.md)
- [pitch-deck-writer](../../business/pitch-deck-writer/SKILL.md)
- [ux-researcher](../../business/ux-researcher/SKILL.md)
- [business-analyst](../../business/business-analyst/SKILL.md)
