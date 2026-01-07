---
name: "session:save"
description: "Session lifecycle management with Codanna MCP integration for session context persistence"
category: session
complexity: standard
mcp-servers: [codanna]
personas: [project-manager, documentation-specialist, knowledge-engineer]
subagents: []
---

# /session:save — Skill-backed session management

## Use
- Load `skills/session-management/SKILL.md` (skill `session-management`) and follow it.
- Then load `skills/session-management/references/save.md` for the detailed workflow.

## Usage
```
/session:save [label] [--type checkpoint|summary|full] [--include-memories]
```