---
name: "orchestrate:task"
description: "Execute complex tasks with intelligent workflow management and delegation"
category: special
complexity: advanced
mcp-servers: [sequential, context7, magic, playwright, morphllm, codanna]
personas: [architect, analyzer, frontend, backend, security, devops, project-manager]
subagents: [general-purpose, code-reviewer, test-automator, Explore]
---

# /orchestrate:task — Skill-backed orchestration

## Use
- Load `skills/task-orchestration/SKILL.md` (skill `task-orchestration`) and follow it.
- Then load `skills/task-orchestration/references/task.md` for the detailed workflow.

## Usage
```
/orchestrate:task [action] [target] [--strategy systematic|agile|enterprise] [--parallel] [--delegate]
```