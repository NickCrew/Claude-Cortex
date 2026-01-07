---
name: "cleanup:docs-cleanup"
description: "Clean up documentation directory by archiving completed tasks and organizing active files"
category: utility
complexity: basic
mcp-servers: []
personas: [documentation-specialist, information-architect, developer]
subagents: []
---

# /cleanup:docs-cleanup — Skill-backed cleanup

## Use
- Load `skills/repo-cleanup/SKILL.md` (skill `repo-cleanup`) and follow it.
- Then load `skills/repo-cleanup/references/docs-cleanup.md` for the detailed checklist.

## Usage
```
/cleanup:docs-cleanup [path] [--mode prune|restructure|refresh] [--dry-run]
```