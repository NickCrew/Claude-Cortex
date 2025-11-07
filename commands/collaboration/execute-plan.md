---
name: execute-plan
description: "Plan execution discipline adapted from Superpowers, mapped to claude-ctx Task TUI and orchestrate view"
category: collaboration
complexity: standard
mcp-servers: []
personas: [project-manager, qa-specialist]
---

# /ctx:execute-plan – Drive the Plan

## Trigger Pattern
```
/ctx:execute-plan [plan-link] [--sync-tasks] [--verify]
```

## Behavior
1. **Sync Tasks**
   - When `--sync-tasks`, confirm each plan bullet exists in Task view (`T`).
   - Otherwise prompt the user to add missing entries.
2. **Activate Context**
   - Toggle required modes and rules; ensure orchestrate view (7) reflects running tasks.
3. **Run Workstream Loop**
   - Pick task → implement → update status/progress.
   - If `--verify`, enforce `/ctx:verify` or relevant testing skill per task.
4. **Status Update**
   - Summarize completed work, blockers, and next steps.
5. **Close Tasks**
   - Mark finished items complete in the Task TUI; remove or park deferred ones.

## Output
- Updated `tasks/current/active_agents.json`.
- Status update block referencing verification evidence.
- Optional follow-up issues for remaining work.
