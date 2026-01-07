---
name: "cleanup:deps-cleanup"
description: "Clean up project dependencies and package management files"
category: utility
complexity: basic
mcp-servers: []
personas: [developer, security-specialist, devops-engineer, performance-engineer]
subagents: []
---

# /cleanup:deps-cleanup — Skill-backed cleanup

## Use
- Load `skills/repo-cleanup/SKILL.md` (skill `repo-cleanup`) and follow it.
- Then load `skills/repo-cleanup/references/deps-cleanup.md` for the detailed checklist.

## Usage
```
/cleanup:deps-cleanup [path] [--type node|python|go|rust|all] [--remove] [--dry-run]
```