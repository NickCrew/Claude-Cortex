---
name: "quality:cleanup"
description: "Systematically clean up code, remove dead code, and optimize project structure"
category: workflow
complexity: standard
mcp-servers: [sequential, context7]
personas: [architect, quality, security]
subagents: [general-purpose, code-reviewer, Explore]
---

# /quality:cleanup — Skill-backed cleanup

## Use
- Load `skills/repo-cleanup/SKILL.md` (skill `repo-cleanup`) and follow it.
- Then load `skills/repo-cleanup/references/code-cleanup.md` for the detailed checklist.

## Usage
```
/quality:cleanup [target] [--type code|imports|files|all] [--safe|--aggressive] [--interactive]
```