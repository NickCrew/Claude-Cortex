---
name: web-researcher
description: 'Use this skill when you need to research a topic online, gather information from multiple sources, or evaluate source credibility. Trigger phrases: ''research'', ''find information about'', ''look up'', ''investigate''. Not for academic systematic reviews (use literature-reviewer) or fact-checking specific claims (use fact-checker).'
version: 1.0.0
author: community
tags:
  - research
  - web
  - search
  - information-gathering
license: MIT
keywords:
  - research online
  - gather information
  - web research
  - web
  - researcher
  - web researcher
---

# Web Researcher

## Overview
The Web Researcher skill provides a structured methodology for conducting effective online research. It covers advanced search strategies, source credibility evaluation using the CRAAP test, synthesis of findings across multiple sources, and organized note-taking. Whether exploring a new market, investigating a technical topic, or gathering competitive intelligence, this skill ensures thorough and reliable results.

## When to Use
- Researching a market landscape or competitive environment
- Finding technical documentation or tutorials on a specific topic
- Gathering background information before writing or presenting
- Investigating current events or recent developments
- Compiling information from multiple web sources into a coherent summary

## When NOT to Use
- When you need a systematic academic literature review (use literature-reviewer)
- When verifying a specific factual claim (use fact-checker)
- When searching only within a single database or proprietary system
- When real-time or live data is required (stock prices, live scores)

## Quick Reference
| Task | Approach |
|------|----------|
| Broad topic overview | Start with Wikipedia, then follow cited sources |
| Find recent news | Use `site:reuters.com` or `after:2024-01-01` filter |
| Academic sources | Google Scholar, PubMed, SSRN |
| Government data | `site:.gov` or `site:.edu` operators |
| Exclude noise | Use `-` operator: `python tutorial -w3schools` |
| Exact phrase | Wrap in quotes: `"machine learning fairness"` |
| Evaluate credibility | Apply CRAAP test (Currency, Relevance, Authority, Accuracy, Purpose) |

## Instructions

1. **Define your research question clearly**
   - Write a 1-2 sentence research question before searching
   - Identify key concepts and synonyms for each concept
   - Example: "What are the current market leaders in B2B SaaS CRM software and their pricing models?"

2. **Construct effective search queries using Boolean operators**
   - AND: narrows results — `CRM software AND pricing AND B2B`
   - OR: broadens results — `CRM OR "customer relationship management"`
   - NOT/minus: excludes terms — `CRM pricing -Salesforce`
   - Quotes for exact phrases: `"market share" "CRM software"`
   - Wildcard (*): `"best * for small business"`

3. **Use site-specific and advanced search filters**
   - `site:domain.com` — search within a specific site
   - `filetype:pdf` — find PDFs (reports, whitepapers)
   - `intitle:keyword` — keyword must appear in page title
   - `after:YYYY-MM-DD` / `before:YYYY-MM-DD` — date range filtering
   - Example: `CRM market share filetype:pdf after:2023-01-01`

4. **Evaluate sources using the CRAAP test**
   - **Currency**: When was it published? Is it recent enough for your topic?
   - **Relevance**: Does it directly address your research question?
   - **Authority**: Who wrote it? What are their credentials? Is the domain reputable (.gov, .edu, peer-reviewed)?
   - **Accuracy**: Is it supported by evidence? Are claims cited? Can you verify facts elsewhere?
   - **Purpose**: Why was it written? Is there bias (commercial, political, ideological)?

5. **Diversify your sources**
   - Aim for at least 5–7 independent sources
   - Include: primary sources (original research, official data), secondary sources (analysis, journalism), and expert commentary
   - Cross-reference key claims across multiple sources

6. **Take structured notes**
   Use this template for each source:
   ```
   Source: [Title, Author, URL, Date]
   Credibility: [CRAAP score: High/Medium/Low]
   Key Finding 1: [quote or paraphrase]
   Key Finding 2: [quote or paraphrase]
   Relevance to question: [1-2 sentences]
   ```

7. **Synthesize findings**
   - Group notes by theme, not by source
   - Identify areas of consensus across sources
   - Note contradictions and explain possible reasons
   - Highlight gaps where information is missing or unclear

## Examples

### Example 1: Research a Market Landscape
**Input:** "Research the current landscape of AI-powered writing tools — key players, pricing, and differentiators."

**Output:**
```
Research Question: Who are the leading AI writing tools, what do they cost, and how do they differentiate?

Search queries used:
- "AI writing tools" market share 2024
- site:g2.com "AI writing" comparison
- "Jasper" OR "Copy.ai" OR "Writesonic" pricing filetype:pdf

Key Findings (synthesized by theme):

MARKET LEADERS:
- Jasper AI: Enterprise focus, starts at $49/mo, strong brand voice features (Source: Jasper.ai, G2 Reviews 2024)
- Copy.ai: Freemium model, $36/mo pro, workflow automation focus (Source: Copy.ai website)
- Writesonic: $16/mo starter, SEO integration via SurferSEO (Source: Writesonic.com)

DIFFERENTIATORS:
- Jasper: Brand voice training, team collaboration
- Copy.ai: Go-to-market workflows, CRM integrations
- Writesonic: Cost efficiency, built-in SEO tools

PRICING TREND: Most tools moving to seat-based + usage-credit hybrid model (multiple sources, 2024)

GAPS: Limited independent data on enterprise contract pricing; most pricing pages hide volume discounts.

Sources rated: 6/7 High credibility (1 Medium — blog post with no cited data)
```

### Example 2: Find Information on a Technical Topic
**Input:** "Find information on WebAssembly performance compared to JavaScript for compute-intensive tasks."

**Output:**
```
Research Question: How does WebAssembly performance compare to JavaScript for compute-intensive workloads?

Search queries used:
- "WebAssembly" vs JavaScript performance benchmark
- site:v8.dev WebAssembly
- "WASM" performance "compute intensive" filetype:pdf after:2022-01-01

Key Findings:

PERFORMANCE BENCHMARKS:
- WASM is typically 10–40% faster than JS for CPU-bound tasks (Mozilla Hacks, 2023)
- For memory-intensive tasks, WASM's linear memory model offers predictability (V8 Blog, 2023)
- JS remains faster for DOM manipulation due to JIT optimization (Surma, web.dev, 2022)

USE CASES WHERE WASM WINS:
- Image/video processing, cryptography, physics simulations, codecs
- Example: Figma uses WASM for its rendering engine (Figma Engineering Blog)

USE CASES WHERE JS IS SUFFICIENT:
- Business logic, UI interactions, API calls, form handling

CREDIBILITY NOTES:
- v8.dev and mozilla.org = High authority (engine developers)
- Personal blogs cross-checked against official benchmarks
```

## Best Practices
- Always start with a written research question — don't just start Googling
- Use at least 3 different search engines or databases for comprehensive coverage
- Screenshot or archive pages in case content changes (use web.archive.org)
- Date-stamp your research sessions — web content changes frequently
- For controversial topics, seek sources from multiple ideological or institutional perspectives
- Build a personal library of trusted source domains by topic area

## Common Mistakes
- Using only the first page of Google results (try different queries and go deeper)
- Accepting information without checking the original primary source
- Trusting a source based on professional appearance alone (design ≠ credibility)
- Failing to note the date of information (outdated data can mislead)
- Confusing correlation with causation in statistics found online
- Not recording URLs at time of research (links go dead)

## Tips & Tricks
- Use Google's "Tools" filter to set a custom date range for recent content
- Append `site:reddit.com` to find candid user opinions and practitioner discussions
- `cache:url` in Google shows the cached version of a page if it's down
- Use `related:domain.com` to find websites similar to a trusted source
- For news, use AllSides.com to see coverage across left/center/right perspectives
- Browser extensions like Web of Science Unpaywall unlock paywalled academic PDFs

## Related Skills
- [literature-reviewer](../../research/literature-reviewer/SKILL.md)
- [fact-checker](../../research/fact-checker/SKILL.md)
- [summarizer](../../research/summarizer/SKILL.md)
- [citation-formatter](../../research/citation-formatter/SKILL.md)
