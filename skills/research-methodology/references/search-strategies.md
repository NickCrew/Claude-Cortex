# Search Strategies Reference

Techniques for query design, source vetting, fact verification, and research synthesis.

## Query Design Techniques

### Boolean Operators

| Operator | Purpose | Example |
|----------|---------|---------|
| `"exact phrase"` | Match exact wording | `"dependency injection" python` |
| `AND` / space | Require both terms | `kubernetes AND "service mesh"` |
| `OR` | Match either term | `"React" OR "Vue" performance` |
| `-term` | Exclude results containing term | `python testing -selenium` |
| `()` | Group operators | `(React OR Vue) AND performance` |

### Faceted Search

Layer constraints to progressively narrow results:

```
Base query:     "state management"
+ Domain:       "state management" site:github.com
+ Recency:      "state management" after:2025-01-01
+ File type:    "state management" filetype:md
+ Exclusion:    "state management" -tutorial -beginner
```

### Query Expansion

When initial queries return poor results, expand systematically:

1. **Synonym expansion** -- replace key terms with alternatives
   - "microservices" → "micro-services", "service-oriented architecture", "distributed services"
2. **Hypernym expansion** -- broaden to parent concepts
   - "Redis caching" → "in-memory caching", "key-value store caching"
3. **Related concept expansion** -- search adjacent topics
   - "rate limiting" → "throttling", "backpressure", "circuit breaker"
4. **Jargon translation** -- use both formal and informal terms
   - "eventual consistency" → "data sync delay", "replication lag"

### Domain-Specific Queries

| Domain | Strategy | Example operators |
|--------|----------|-------------------|
| Academic | Target scholar databases, use citation count as signal | `site:arxiv.org`, `site:scholar.google.com` |
| Open source | Search repos, issues, discussions | `site:github.com`, `is:issue`, `in:readme` |
| Industry | Target company blogs, conference talks | `site:engineering.*.com`, `inurl:blog` |
| Standards | Target spec organizations | `site:ietf.org`, `site:w3.org`, `site:openapis.org` |

---

## Source Vetting

### Authority Assessment

Evaluate the credibility of each source:

| Signal | Strong authority | Weak authority |
|--------|-----------------|----------------|
| **Author** | Named expert with track record | Anonymous or unknown |
| **Publisher** | Peer-reviewed, reputable org | Personal blog, content farm |
| **Citations** | Cited by other credible sources | No external references |
| **Methodology** | Transparent data and methods | Claims without evidence |
| **Updates** | Regularly maintained | Stale, no revision history |

### Recency Assessment

| Content type | Acceptable age | Why |
|-------------|---------------|-----|
| API documentation | < 6 months | APIs change frequently |
| Best practices | < 2 years | Practices evolve with tooling |
| Foundational concepts | Any | Core CS concepts are stable |
| Market data | < 1 year | Markets shift quickly |
| Security advisories | < 3 months | Threat landscape moves fast |

### Bias Detection

Common bias types to watch for:

| Bias type | Indicator | Mitigation |
|-----------|-----------|------------|
| **Commercial** | Source sells a competing product | Seek independent benchmarks |
| **Survivorship** | Only successful cases discussed | Search for failure cases explicitly |
| **Recency** | Favors new over proven approaches | Include established sources |
| **Confirmation** | Matches your hypothesis too neatly | Actively search for counterarguments |
| **Authority** | Big name said it, so it must be true | Verify the claim, not the speaker |

---

## Fact Verification

### Triangulation Method

For any important claim, require three independent paths to confirmation:

```
Claim: "Library X handles 10K concurrent connections"

Path 1 (primary source):   Official benchmark in library docs
Path 2 (independent test):  Third-party benchmark blog post
Path 3 (community signal):  GitHub issues/discussions confirming at scale
```

If paths disagree, investigate why. Common reasons:
- Different test conditions (hardware, configuration, workload)
- Different versions of the software
- Different definitions of the metric

### Primary Source Tracing

Follow the citation chain to the original data:

```
Blog post claims "X is 10x faster" →
  cites a conference talk →
    which references a benchmark paper →
      which contains the actual test methodology and data
```

Evaluate the primary source, not the downstream claim. Downstream sources often:
- Oversimplify or exaggerate findings
- Omit important caveats
- Cite outdated versions of the research

### Contradiction Handling

When credible sources disagree:

1. **Document both positions** with full citations
2. **Identify the variable** -- what differs between the sources?
3. **Assess which context applies** to your research question
4. **Rate confidence as "Contested"** and explain why
5. **Recommend resolution** -- what additional evidence would settle it?

---

## Competitive Analysis Frameworks

### Feature Matrix

```markdown
| Capability | Product A | Product B | Product C |
|-----------|-----------|-----------|-----------|
| Feature 1 | Yes (v2+) | Partial   | No        |
| Feature 2 | No        | Yes       | Yes       |
| Pricing   | $X/mo     | $Y/mo     | Free tier |
| License   | MIT       | Apache-2  | AGPL      |
```

### SWOT per Competitor

```markdown
## [Competitor Name]

**Strengths**: What they do well
**Weaknesses**: Where they fall short
**Opportunities**: Gaps they haven't addressed
**Threats**: Risks they pose to our position
```

### Trend Analysis

Track how a topic evolves over time:

1. Search with date-restricted queries (yearly or quarterly windows)
2. Note when key terms first appear and peak
3. Identify inflection points (new releases, incidents, standards changes)
4. Plot adoption signals (GitHub stars, npm downloads, job postings)

---

## Market Research Patterns

### TAM/SAM/SOM Estimation

When sizing a market opportunity:

1. **Total Addressable Market** -- search for industry reports, analyst estimates
2. **Serviceable Available Market** -- narrow by geography, segment, constraints
3. **Serviceable Obtainable Market** -- factor in competition and realistic capture

Always cite the source of market size numbers and note the methodology used.

### User/Customer Research Signals

Where to find real user sentiment:

| Source | Signal quality | Access |
|--------|---------------|--------|
| GitHub Issues | High (specific, technical) | Public |
| Stack Overflow | High (real problems) | Public |
| Reddit/HN | Medium (anecdotal but candid) | Public |
| G2/Capterra reviews | Medium (structured, some bias) | Public |
| Conference talks | High (curated, expert) | Often public recordings |

---

## Synthesis and Reporting

### Organizing Findings

Choose organization by what serves the reader:

| Structure | Best for |
|-----------|----------|
| **By theme** | Research with cross-cutting findings |
| **By question** | Research with distinct, independent questions |
| **By source** | When source credibility comparison matters |
| **Chronological** | Historical investigations and trend analysis |
| **By confidence** | When reliability varies widely across findings |

### Evidence Strength Indicators

Use consistent markers in reports:

```
[CONFIRMED] — 3+ independent authoritative sources agree
[LIKELY]    — 2 sources agree, no contradictions
[UNCERTAIN] — single source or limited evidence
[CONTESTED] — credible sources disagree
[ESTIMATED] — derived from available data, not directly measured
```

### Gap Documentation

Always explicitly state what you could NOT determine:

```markdown
## Research Gaps

- **[Topic]**: No credible sources found for [specific question]
  - Searched: [queries attempted]
  - Possible next step: [how to resolve]
```

This prevents readers from assuming silence means "not relevant" when it really means "not found."
