---
name: "cleanup:code-cleanup"
description: "Clean up source code directories by removing build artifacts, dead code, and organizing files"
category: utility
complexity: basic
mcp-servers: []
personas: [developer, quality-engineer, devops-engineer]
subagents: []
---

# /cleanup:code-cleanup — Skill-backed cleanup

## Use
- Load `skills/repo-cleanup/SKILL.md` (skill `repo-cleanup`) and follow it.
- Then load `skills/repo-cleanup/references/code-cleanup.md` for the detailed checklist.

## Usage
```
/cleanup:code-cleanup [path] [--mode safe|aggressive] [--archive] [--dry-run]
```