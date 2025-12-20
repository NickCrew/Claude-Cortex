---
name: mashup
description: "Cross-pollinate domains to force novel UX/GT/MVP angles"
category: collaboration
complexity: standard
mcp-servers: []
personas: [frontend, product-manager, architect]
subagents: []
---

# /collaboration:mashup — Domain Crossovers

## Trigger Pattern
```
/collaboration:mashup [topic] [--domains fintech|gaming|health|education|commerce|media|gov|b2b|b2c|--random] [--constraints ...]
```

## Behavior
1. Pick 2–3 domains (from flags or random) with orthogonal patterns (e.g., loyalty loops, streaks, rituals, marketplace dynamics).
2. For each domain, map 1–2 patterns onto the topic.
3. Produce 3 mashup concepts including **User journey sketch**, **Differentiator**, **Risk**, **First experiment**.
4. Highlight **1 bold bet** and **1 safe bet**.
5. Seed Tasks for experiments if requested.

## Output
- Sections: Selected Domains, Patterns Applied, Mashup Concepts (3), Bold vs Safe, Next Experiments.
- Optional save: `docs/plans/<date>-mashup.md`.

## Personas
- **frontend**: interaction ideas inspired by other domains
- **product-manager**: market/positioning implications
- **architect**: feasibility and data/dependency mapping

## Delegation
- Use Task tool if domain research is needed; otherwise inline.

## Follow-up
- Run `/ctx:plan` with the bold or safe bet; open Tasks for experiments.
