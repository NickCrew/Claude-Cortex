---
name: "collaboration:concept-forge"
description: "Ranked concept cards with quick cost/benefit math and a 1-day spike suggestion"
category: collaboration
complexity: standard
mcp-servers: []
personas: [product-manager, architect, analyzer]
subagents: []
---

# /collaboration:concept-forge — Skill-backed concept scoring

## Use
- Load `skills/collaboration/concept_forge/SKILL.md` (skill `concept-forge`) and follow it.
- Keep the ranked concept card format from the skill.

## Usage
```
/collaboration:concept-forge [problem] [--score impact|delight|effort] [--constraints ...]
```