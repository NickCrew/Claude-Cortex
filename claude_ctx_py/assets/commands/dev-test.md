---
name: "dev:test"
description: "Execute tests with coverage analysis and automated quality reporting"
category: utility
complexity: enhanced
mcp-servers: [playwright]
personas: [qa-specialist, developer]
subagents: [general-purpose, test-automator]
---

# /dev:test — Skill-backed dev workflow

## Use
- Load `skills/dev-workflows/SKILL.md` (skill `dev-workflows`) and follow it.
- Then load `skills/dev-workflows/references/test.md` for the detailed workflow.

## Usage
```
/dev:test [target] [--type unit|integration|e2e|all] [--coverage] [--watch] [--fix]
```