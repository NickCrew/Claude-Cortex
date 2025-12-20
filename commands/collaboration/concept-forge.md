---
name: concept-forge
description: "Ranked concept cards with quick cost/benefit math and a 1-day spike suggestion"
category: collaboration
complexity: standard
mcp-servers: []
personas: [product-manager, architect, analyzer]
subagents: []
---

# /collaboration:concept-forge — Scored Concept Cards

## Trigger Pattern
```
/collaboration:concept-forge [problem] [--score impact|delight|effort] [--constraints ...]
```

## Behavior
1. Capture **Problem**, **Success Signals**, **Constraints**.
2. Generate 4–6 solution cards; each includes: **Concept**, **Impact (1–5)**, **Delight (1–5)**, **Effort (S/M/L)**, **Risks**, **1-day Spike**.
3. Rank by chosen `--score` axis (default impact) with ties broken by lowest effort.
4. Recommend top card + spike to run immediately; list verification steps.
5. Seed Task view for the spike or hand off to `/ctx:plan`.

## Output
- Sections: Problem, Success Signals, Constraints, Concept Cards (ranked), Recommended Spike, Verification Checklist.
- Optional save: `docs/plans/<date>-concept-forge.md`.

## Personas
- **product-manager**: impact/delight framing
- **architect**: effort and feasibility
- **analyzer**: risk and validation logic

## Delegation
- Delegate via Task tool if data/constraints need discovery; otherwise inline.

## Follow-up
- Execute spike via Tasks; formalize plan with `/ctx:plan` if approved.
