---
name: "dev:build"
description: "Build, compile, and package projects with intelligent error handling and optimization"
category: utility
complexity: enhanced
mcp-servers: [playwright]
personas: [devops-engineer, performance-engineer]
subagents: [general-purpose]
---

# /dev:build — Skill-backed dev workflow

## Use
- Load `skills/dev-workflows/SKILL.md` (skill `dev-workflows`) and follow it.
- Then load `skills/dev-workflows/references/build.md` for the detailed workflow.

## Usage
```
/dev:build [target] [--type dev|prod|test] [--clean] [--optimize] [--verbose]
```