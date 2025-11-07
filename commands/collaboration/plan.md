---
name: plan
description: "Plan-writing flow linking borrowed Superpowers skill to claude-ctx workflows and Task TUI"
category: collaboration
complexity: standard
mcp-servers: []
personas: [architect, project-manager]
---

# /ctx:plan – Plan Writing

## Trigger Pattern
```
/ctx:plan [summary] [--streams n] [--save]
```

## Behavior
1. Restate objective + constraints from `/ctx:brainstorm`.
2. Break work into streams; map each to modes, rules, and agents.
3. For every task bullet:
   - Include Definition of Done + verification (tests, Supersaiyan visual, MCP check).
   - Create/update Task TUI entries (press `T` → `A`/`E`).
4. Document risks/mitigations + checkpoints.
5. Store plan in `docs/plans/<date>-<slug>.md` when `--save` is provided.

## Output
- Markdown plan table following `skills/collaboration/writing-plans/SKILL.md` template.
- Tasks synced to `tasks/current/active_agents.json`.

## Follow-up
- Run `/ctx:execute-plan` to enforce orchestration + verification.
