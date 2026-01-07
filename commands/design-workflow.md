---
name: "design:workflow"
description: "Generate structured implementation workflows from PRDs and feature requirements"
category: orchestration
complexity: advanced
mcp-servers: [sequential, context7, magic, playwright, morphllm, codanna]
personas: [architect, analyzer, frontend, backend, security, devops, project-manager]
subagents: [Explore, general-purpose, code-reviewer]
---

# /design:workflow — Skill-backed workflow planning

## Use
- Load `skills/implementation-workflow/SKILL.md` (skill `implementation-workflow`) and follow it.
- Then load `skills/implementation-workflow/references/workflow.md` for the detailed workflow.

## Usage
```
/design:workflow [prd-file|feature-description] [--strategy systematic|agile|enterprise] [--depth shallow|normal|deep] [--parallel]
```