---
name: assumption-buster
description: "Inverts, removes, or exaggerates assumptions to reveal novel solution angles"
category: collaboration
complexity: standard
mcp-servers: []
personas: [architect, analyzer, product-manager]
subagents: []
---

# /collaboration:assumption-buster — Reframe Through Inversion

## Trigger Pattern
```
/collaboration:assumption-buster [topic] [--opposite|--zero|--10x] [--constraints ...]
```

## Behavior
1. List core assumptions (facts, beliefs, constraints) about the topic.
2. Apply operator per flag:
   - `--opposite`: Flip the assumption.
   - `--zero`: Remove the assumption entirely.
   - `--10x`: Exaggerate the assumption tenfold.
3. For each transformed assumption, generate 1–2 reframed ideas.
4. Capture **Evidence to collect** and **Fast test** for each idea.
5. Summarize **Most compelling 2–3** ideas with risks/unknowns.

## Output
- Sections: Assumptions, Transforms, Reframed Ideas, Evidence & Tests, Top Picks.
- Optional save to `docs/plans/<date>-assumption-buster.md`.

## Personas
- **architect**: technical feasibility check
- **analyzer**: logic gaps, critical thinking
- **product-manager**: user and business impact

## Delegation
- Use Task tool when assumption list depends on repo/state discovery.
- Otherwise run inline.

## Follow-up
- Feed top picks into `/ctx:plan` or create Tasks for fast tests.
