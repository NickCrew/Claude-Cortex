---
name: idea-lab
description: "Rapid divergent ideation sprint that produces sharply different options and auto-seeds immediate tasks"
category: collaboration
complexity: standard
mcp-servers: []
personas: [product-manager, architect, frontend]
subagents: []
---

# /collaboration:idea-lab — Divergent Sprint

## Trigger Pattern
```
/collaboration:idea-lab [topic] [--time 10|15|25] [--constraints ...]
```

## Behavior
1. Timebox the session (default 15m); state the timebox aloud in the transcript.
2. Capture **Goals**, **Success Signals**, **Constraints**, **Existing Assets**.
3. Generate 5–7 distinct solution concepts; for each add **Wow-Factor**, **Feasibility (S/M/L)**, **Dependency to check**.
4. Surface **Top 3 to test today** and assign a 1-day experiment for each.
5. Seed Task view (`T` → `A`) with the three experiments or hand off to `/ctx:plan`.

## Output
- Markdown block with sections: Problem/Goal, Success Signals, Constraints, Existing Assets, Options (table), Top 3 Experiments, Next Steps.
- Optional file drop under `docs/plans/<date>-idea-lab.md`.

## Personas
- **product-manager**: user value, success metrics
- **architect**: feasibility and dependency mapping
- **frontend**: UX/interaction angles to differentiate concepts

## Delegation
- Use Task tool when repo/asset discovery is needed before ideating.
- Skip delegation for quick idea-only sessions.

## Follow-up
- Immediately run `/ctx:plan` with the chosen top experiment or open Tasks seeded in step 5.
