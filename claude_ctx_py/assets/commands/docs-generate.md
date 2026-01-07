---
name: "docs:generate"
description: "Generate focused documentation for components, functions, APIs, and features"
category: utility
complexity: basic
mcp-servers: []
personas: [technical-writer, developer]
subagents: [technical-writer, api-documenter]
---

# /docs:generate — Skill-backed docs

## Use
- Load `skills/documentation-production/SKILL.md` (skill `documentation-production`) and follow it.
- Then load `skills/documentation-production/references/generate.md` for the detailed workflow.

## Usage
```
/docs:generate [target] [--type inline|external|api|guide] [--style brief|detailed]
```