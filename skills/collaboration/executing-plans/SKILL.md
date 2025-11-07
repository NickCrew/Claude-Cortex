---
name: ctx-plan-execution
description: Execution discipline skill adapted from obra/superpowers. Ensures plans translate into tracked tasks, orchestration, and verification runs.
license: MIT (obra/superpowers)
command: /ctx:execute-plan
---

# `/ctx:execute-plan`

Locks in the plan and drives it through claude-ctx’s orchestration + verification stack.

## Prereqs

- `/ctx:plan` output in the thread.
- Tasks captured in the Task view (`T`) or ready to be created now.
- Relevant modes/agents activated.

## Steps

1. **Create/Sync Tasks**
   - For each plan item, add/edit a task (Task view `T` → `A`/`E`).
   - Ensure category + workstream mirror the plan’s stream names.
2. **Activate Modes & Rules**
   - Toggle required modes (`3` view) and rules (`4` view) to match plan.
3. **Run Workstream Loops**
   - Pick a task → do the work → update status/progress.
   - Use `/ctx:verify` rules (tests, lint, Supersaiyan visual check) before moving to next task.
4. **Update Stakeholders**
   - For finished streams, summarize progress + next up; attach screenshots/logs when relevant.
5. **Retrospective Hooks**
   - When all tasks complete, close them in Task view, capture learnings in chat, and link to plan doc.

## Output

- Tasks JSON updated under `tasks/current/active_agents.json`.
- Status update message covering completed tasks, blockers, verification evidence.
- Next steps or follow-up issues if needed.

## Resources

- Execution checklist: `skills/collaboration/executing-plans/resources/checklist.md`.
