---
name: "docs:teacher"
description: "Explain concepts and design learning paths with exercises"
category: utility
complexity: standard
mcp-servers: []
personas: [technical-writer, educator]
subagents: [learning-guide]
---

# /docs:teacher — Skill-backed docs

## Use
- Load `skills/documentation-production/SKILL.md` (skill `documentation-production`) and follow it.
- Then load `skills/documentation-production/references/teacher.md` for the detailed workflow.

## Usage
```
/docs:teacher [topic] [--level beginner|intermediate|advanced] [--format lesson|path|exercise]
```