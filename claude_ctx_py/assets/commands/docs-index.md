---
name: "docs:index"
description: "Generate comprehensive project documentation and knowledge base with intelligent organization"
category: special
complexity: standard
mcp-servers: [sequential, context7]
personas: [architect, technical-writer, quality-engineer]
subagents: [Explore, technical-writer, api-documenter]
---

# /docs:index — Skill-backed docs

## Use
- Load `skills/documentation-production/SKILL.md` (skill `documentation-production`) and follow it.
- Then load `skills/documentation-production/references/index.md` for the detailed workflow.

## Usage
```
/docs:index [target] [--type docs|api|structure|readme] [--format md|json|yaml]
```