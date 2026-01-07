---
name: "docs:tutorials"
description: "Create hands-on tutorials with progressive steps and exercises"
category: utility
complexity: standard
mcp-servers: []
personas: [technical-writer, educator]
subagents: [tutorial-engineer]
---

# /docs:tutorials — Skill-backed docs

## Use
- Load `skills/documentation-production/SKILL.md` (skill `documentation-production`) and follow it.
- Then load `skills/documentation-production/references/tutorials.md` for the detailed workflow.

## Usage
```
/docs:tutorials [topic] [--format quickstart|deep-dive|workshop|cookbook] [--level beginner|intermediate|advanced]
```