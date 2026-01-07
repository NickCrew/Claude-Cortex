---
name: "cleanup:archive-sprint"
description: "Archive all artifacts from a completed sprint, including plans, summaries, reports, and temporary files."
category: utility
complexity: basic
mcp-servers: []
personas: [project-manager, documentation-specialist, devops-engineer]
subagents: []
---

# /cleanup:archive-sprint — Skill-backed sprint archive

## Use
- Load `skills/repo-cleanup/SKILL.md` (skill `repo-cleanup`) and follow it.
- Then load `skills/repo-cleanup/references/archive-sprint.md` for the detailed checklist.

## Usage
```
/cleanup:archive-sprint [sprint-name] [--branch] [--docs-only]
```