---
layout: default
title: Planning & Collaboration
parent: Guides
nav_order: 8
---

# Planning & Collaboration

Cortex provides a structured workflow for moving from ideation to execution
using collaboration skills, task tracking, and optional plan files.

## The Workflow

```
/collaboration:brainstorming → /collaboration:writing-plans → /collaboration:executing-plans
```

1. **Brainstorm** goals, constraints, and options
2. **Write the plan** with workstreams and validation criteria
3. **Execute** with task tracking and quality gates

## /collaboration:brainstorming

Structured ideation before writing code. Captures goals, success signals, and solution options.

**When to use:**
- Before touching code -- align on the problem first
- After major context shifts (new stakeholder, dependency change)
- When stuck -- broaden the solution space

**Output format:**

```markdown
### Problem / Goal
### Success Signals
### Constraints / Risks
### Existing Assets
### Options
- Option A (pros/cons/risks)
- Option B (pros/cons/risks)
- Option C (pros/cons/risks)
### Chosen Direction & Next Steps
```

The command generates at least three distinct approaches with trade-off analysis, then selects a candidate direction.

## /collaboration:writing-plans

Transforms brainstorm output into a concrete execution plan with workstreams and tasks.

**Inputs:** The brainstorm summary from the previous step.

**Output format:**

```markdown
## Objective
One paragraph with constraints and scope.

## Workstreams
### Stream 1 -- Backend API
- Task: Implement auth endpoints (agent: rest-expert, validation: tests pass)
- Task: Add rate limiting (agent: security-auditor, validation: load test)

### Stream 2 -- Frontend
- Task: Build login form (agent: react-specialist, validation: a11y check)

## Risks & Mitigations
- Risk: Token refresh race condition → Mitigation: add mutex
```

Each task includes:
- Definition of Done
- Suggested agent
- Validation criteria

Plans can stay in the conversation, or you can save plan documents and inspect
them later with the `cortex plan` command group.

## /collaboration:executing-plans

Drives plan execution through task tracking and verification.

**Prerequisites:** A plan from `/collaboration:writing-plans` in the conversation.

**Workflow:**
1. Create tasks in the Task view (press `T` in TUI, then `A` to add)
2. Activate relevant agents
3. Work through tasks -- pick a task, do the work, update its status
4. Verify each task against its Definition of Done
5. Capture learnings when complete

**Integration points:**
- Tasks sync to `tasks/current/active_agents.json`
- Status updates include completed tasks, blockers, and verification evidence
- Quality gate hooks run automatically during development

## Plan Files

Use the CLI to inspect saved plans:

```bash
cortex plan list
cortex plan view <plan-name>
cortex plan edit <plan-name>
cortex plan path
```

## Putting It Together

A typical feature development session:

```
# 1. Ideate
/collaboration:brainstorming
> "Build a user settings page with profile editing and notification preferences"

# 2. Plan
/collaboration:writing-plans
> Creates 3 workstreams: API, Frontend, Tests

# 3. Execute
/collaboration:executing-plans
> Tracks tasks, runs quality gates

# 4. Build
/ctx:agent-loops
/ctx:test-generation
/ctx:requesting-code-review
/ctx:git-ops
```

## TUI Task View

Press `T` in the TUI to manage tasks created by the planning workflow:

| Key | Action |
|:----|:-------|
| `T` | Open Task view |
| `A` | Add new task |
| `E` | Edit task |

Tasks are organized by category and workstream, matching the structure from
`/collaboration:writing-plans`.

## Skill Auto-Suggester

The collaboration commands are automatically suggested by the skill auto-suggester hook when it detects relevant keywords in your prompts. For example, typing "let's brainstorm" triggers a suggestion for the brainstorming skill.

Keyword mappings are defined in `skills/skill-rules.json`.
