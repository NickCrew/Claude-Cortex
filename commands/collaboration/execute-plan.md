---
name: execute-plan
description: "Plan execution discipline adapted from Superpowers, mapped to claude-ctx Task TUI and orchestrate view"
category: collaboration
complexity: standard
mcp-servers: []
personas: [project-manager, qa-specialist]
subagents: [general-purpose, code-reviewer, test-automator]
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

## Personas (Thinking Modes)
- **project-manager**: Coordination, planning, status tracking, stakeholder communication
- **qa-specialist**: Quality standards, testing requirements, verification protocols

## Delegation Protocol

**When to delegate** (use Task tool):
- ✅ Plan with >3 independent tasks
- ✅ Tasks spanning multiple domains (implementation + tests + docs)
- ✅ Complex features requiring >5 steps
- ✅ Parallel workstreams possible

**Available subagents**:
- **general-purpose**: Implementation tasks from plan
- **code-reviewer**: Quality verification per task (when --verify)
- **test-automator**: Test generation/execution per task (when --verify)

**Delegation strategy for plan execution**:
```xml
<!-- Launch parallel workstreams for independent plan tasks -->
<function_calls>
<invoke name="Task">
  <subagent_type>general-purpose</subagent_type>
  <description>Execute plan task 1: [description]</description>
  <prompt>Implement task from plan with project-manager coordination...</prompt>
</invoke>
<invoke name="Task">
  <subagent_type>general-purpose</subagent_type>
  <description>Execute plan task 2: [description]</description>
  <prompt>Implement task from plan...</prompt>
</invoke>
<!-- Quality verification if --verify flag -->
<invoke name="Task">
  <subagent_type>code-reviewer</subagent_type>
  <description>Verify completed tasks</description>
  <prompt>Review all completed plan tasks for quality...</prompt>
</invoke>
</function_calls>
```

**When NOT to delegate** (use direct tools):
- ❌ Simple plan with 1-2 trivial tasks
- ❌ Plan coordination only (no actual implementation)

## Tool Coordination
- **Task tool**: Executes plan tasks via subagents for complex plans
- **TodoWrite**: Syncs plan items to Task TUI (--sync-tasks)
- **Read/Write**: Updates task status and active_agents.json
- **Direct tools**: Simple plan tasks

## Output
- Updated `tasks/current/active_agents.json`.
- Status update block referencing verification evidence.
- Optional follow-up issues for remaining work.
