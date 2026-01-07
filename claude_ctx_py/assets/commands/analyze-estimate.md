---
name: "analyze:estimate"
description: "Provide development estimates for tasks, features, or projects with intelligent analysis"
category: special
complexity: standard
mcp-servers: [sequential, context7]
personas: [architect, performance-engineer, project-manager]
subagents: [Explore, general-purpose]
---

# /analyze:estimate — Skill-backed estimation

## Use
- Load `skills/development-estimation/SKILL.md` (skill `development-estimation`) and follow it.
- Then load `skills/development-estimation/references/estimate.md` for the detailed workflow.

## Usage
```
/analyze:estimate [target] [--type time|effort|complexity] [--unit hours|days|weeks] [--breakdown]
```