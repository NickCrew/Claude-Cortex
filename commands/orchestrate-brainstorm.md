---
name: "orchestrate:brainstorm"
description: "Interactive requirements discovery through Socratic dialogue and systematic exploration"
category: orchestration
complexity: advanced
mcp-servers: [sequential, context7, magic, playwright, morphllm, codanna]
personas: [architect, analyzer, frontend, backend, security, devops, project-manager]
---

# /orchestrate:brainstorm — Skill-backed orchestration

## Use
- Load `skills/task-orchestration/SKILL.md` (skill `task-orchestration`) and follow it.
- Then load `skills/task-orchestration/references/brainstorm.md` for the detailed workflow.

## Usage
```
/orchestrate:brainstorm [topic/idea] [--strategy systematic|agile|enterprise] [--depth shallow|normal|deep] [--parallel]
```