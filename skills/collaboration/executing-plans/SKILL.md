---
name: executing-plans
description: Execution discipline that translates plans into tracked tasks with orchestration and verification loops. Use when driving a plan through cortex’s task system, coordinating workstreams across agents, or ensuring every plan item is tracked, executed, and verified.
keywords:
  - execute plan
  - follow plan
  - start implementing
file_patterns:
  - '**/TODO.md'
  - '**/docs/plans/**'
  - '**/notes/**'
  - '**/planning/**'
  - '**/scenarios/**'
  - '**/todo.md'
confidence: 0.82
license: MIT (obra/superpowers)
tags:
  - collaboration
  - execution
  - task-management
  - orchestration
---

# Executing Plans

Locks in an approved plan and drives it through cortex’s orchestration and verification stack, ensuring every item becomes a tracked task that is executed, verified, and reported.

## When to Use This Skill

- A plan from `writing-plans` or `/ctx:plan` is ready for execution
- Coordinating multiple workstreams or agents against a shared plan
- Ensuring plan items are tracked as tasks with status updates
- Running verification loops (tests, lint, visual checks) before marking tasks done
- Avoid using before a plan exists — use `writing-plans` first

## Prerequisites

- Plan output available in the thread (from `writing-plans` or `/ctx:plan`)
- Access to Task view (`T`) in cortex TUI
- Relevant modes and agents activated for the workstreams

## Workflow

### Step 1: Create and Sync Tasks

For each plan item, create or update a task in the Task view:

```
Task view (T) → Add (A) or Edit (E)
```

- Set **category** and **workstream** to mirror the plan’s stream names
- Ensure every plan item has a corresponding task — no orphan items
- Link tasks to the originating plan document

### Step 2: Activate Modes and Rules

Toggle the required configuration to match the plan:

- **Modes** (view `3`): Activate modes needed for current workstreams
- **Rules** (view `4`): Enable rules that apply (e.g., testing requirements, style enforcement)

### Step 3: Execute Workstream Loops

For each task in priority order:

1. **Pick** the next task from the active workstream
2. **Execute** the work (implementation, writing, configuration, etc.)
3. **Verify** before marking complete:
   - Run tests: `pytest`, `vitest`, or project-specific test command
   - Run linting: `just lint` or equivalent
   - Visual check via Supersaiyan if UI changes are involved
4. **Update** task status and progress notes

```bash
# Example verification sequence
just test && just lint && echo "Verification passed"
```

### Step 4: Update Stakeholders

For each completed workstream:

- Summarize progress and what’s next
- Attach relevant screenshots, logs, or test output
- Flag any blockers or scope changes discovered during execution

### Step 5: Run Retrospective Hooks

When all tasks are complete:

1. Close all tasks in the Task view
2. Capture learnings and surprises in the chat thread
3. Link back to the original plan document
4. Note any follow-up issues or tech debt discovered

## Expected Output

- `tasks/current/active_agents.json` updated with task statuses
- Status update message covering: completed tasks, blockers, verification evidence
- Next steps or follow-up issues if the plan extends beyond this session

## Best Practices

- **Verify before advancing** — Never mark a task done without running the verification loop
- **One task at a time** — Complete and verify each task before starting the next
- **Update status in real time** — Stakeholders should see progress, not just a final dump
- **Link everything** — Tasks link to plan, plan links to tasks, status updates reference both
- **Capture blockers immediately** — Don’t wait until the retrospective to surface problems

## Resources

- Execution checklist: `skills/collaboration/executing-plans/resources/checklist.md`
