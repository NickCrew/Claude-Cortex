---
name: "reasoning:adjust"
description: "Dynamically adjust reasoning depth during task execution"
category: utility
complexity: basic
mcp-servers: []
personas: [performance-engineer, architect, cost-optimizer]
subagents: []
---

# /reasoning:adjust — Skill-backed reasoning control

## Use
- Load `skills/reasoning-controls/SKILL.md` (skill `reasoning-controls`) and follow it.
- Then load `skills/reasoning-controls/references/adjust.md` for the detailed workflow.

## Usage
```
/reasoning:adjust [low|medium|high|ultra] [--auto-adjust]
```