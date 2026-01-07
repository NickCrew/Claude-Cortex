---
name: "cleanup:test-cleanup"
description: "Clean up test directories by removing generated reports and organizing test files"
category: utility
complexity: basic
mcp-servers: []
personas: [test-engineer, quality-engineer, developer]
subagents: []
---

# /cleanup:test-cleanup — Skill-backed cleanup

## Use
- Load `skills/repo-cleanup/SKILL.md` (skill `repo-cleanup`) and follow it.
- Then load `skills/repo-cleanup/references/test-cleanup.md` for the detailed checklist.

## Usage
```
/cleanup:test-cleanup [path] [--type unit|integration|e2e|all] [--mode prune|refactor] [--dry-run]
```