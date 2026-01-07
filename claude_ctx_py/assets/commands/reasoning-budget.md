---
name: "reasoning:budget"
description: "Control internal reasoning token budget for cost and quality optimization"
category: utility
complexity: basic
mcp-servers: []
personas: [cost-optimizer, performance-engineer, architect]
subagents: []
---

# /reasoning:budget — Skill-backed reasoning control

## Use
- Load `skills/reasoning-controls/SKILL.md` (skill `reasoning-controls`) and follow it.
- Then load `skills/reasoning-controls/references/budget.md` for the detailed workflow.

## Usage
```
/reasoning:budget [4000|10000|32000|128000] [--auto-adjust] [--show-usage]
```