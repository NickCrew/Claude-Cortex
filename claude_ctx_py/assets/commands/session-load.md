---
name: "session:load"
description: "Session lifecycle management with Codanna MCP integration for project context loading"
category: session
complexity: standard
mcp-servers: [codanna]
personas: [project-manager, developer, knowledge-engineer]
subagents: []
---

# /session:load — Skill-backed session management

## Use
- Load `skills/session-management/SKILL.md` (skill `session-management`) and follow it.
- Then load `skills/session-management/references/load.md` for the detailed workflow.

## Usage
```
/session:load [target] [--type project|config|deps|checkpoint] [--refresh] [--analyze]
```