---
name: "orchestrate:spawn"
description: "Meta-system task orchestration with intelligent breakdown and delegation"
category: special
complexity: high
mcp-servers: []
personas: [architect, analyzer]
subagents: [general-purpose, Explore, code-reviewer, test-automator]
---

# /orchestrate:spawn — Skill-backed orchestration

## Use
- Load `skills/task-orchestration/SKILL.md` (skill `task-orchestration`) and follow it.
- Then load `skills/task-orchestration/references/spawn.md` for the detailed workflow.

## Usage
```
/orchestrate:spawn [agent-type] [--count n] [--task "..."] [--parallel]
```