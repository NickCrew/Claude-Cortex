---
name: "ctx:execute-plan"
description: "Plan execution discipline adapted from Superpowers, mapped to cortex Task TUI and orchestrate view"
category: collaboration
complexity: standard
mcp-servers: []
personas: [project-manager, qa-specialist]
subagents: [general-purpose, code-reviewer, test-automator]
---

# /ctx:execute-plan — Skill-backed execution

## Use
- Load `skills/collaboration/executing-plans/SKILL.md` (skill `ctx-plan-execution`) and follow it.
- Only load `skills/collaboration/executing-plans/resources/checklist.md` if you need the checklist.

## Usage
```
/ctx:execute-plan [plan-link] [--sync-tasks] [--verify]
```
