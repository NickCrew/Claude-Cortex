---
layout: default
title: Planning & Collaboration
parent: Guides
nav_order: 9
---

# Planning & Collaboration

Cortex provides a structured workflow for moving from ideation to execution using three collaboration commands and session management.

## The Workflow

```
/session:load → /ctx:brainstorm → /ctx:plan → /ctx:execute-plan → /session:save
```

1. **Load context** and get oriented
2. **Brainstorm** goals, constraints, and options
3. **Plan** workstreams with tasks and validation criteria
4. **Execute** with task tracking and quality gates
5. **Save** session context and learnings

## /ctx:brainstorm

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

## /ctx:plan

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
- Suggested agent or mode
- Validation criteria

Plans are stored in the conversation and optionally saved to `docs/plans/<date>-<slug>.md`.

## /ctx:execute-plan

Drives plan execution through task tracking and verification.

**Prerequisites:** A plan from `/ctx:plan` in the conversation.

**Workflow:**
1. Create tasks in the Task view (press `T` in TUI, then `A` to add)
2. Activate relevant modes and agents
3. Work through tasks -- pick a task, do the work, update its status
4. Verify each task against its Definition of Done
5. Capture learnings when complete

**Integration points:**
- Tasks sync to `tasks/current/active_agents.json`
- Status updates include completed tasks, blockers, and verification evidence
- Quality gate hooks run automatically during development

## Session Management

### /session:load

Loads project context at the start of a session:

```bash
/session:load                              # Load current directory
/session:load /path/to/project --analyze   # Load and analyze
/session:load --type checkpoint --checkpoint session_123
```

**Types:** `project`, `config`, `deps`, `checkpoint`

Loads project context, retrieves cross-session memories, and sets up the working environment. Reminds you to brainstorm if starting fresh work.

### /session:save

Persists session state for future sessions:

```bash
/session:save                            # Basic save with auto-checkpoint
/session:save --type all --checkpoint    # Full preservation
/session:save --summarize                # With session summary
/session:save --type learnings           # Discoveries only
```

**Types:** `session`, `learnings`, `context`, `all`

Auto-creates checkpoints for sessions longer than 30 minutes.

### /session:reflect

Validates progress and quality mid-session:

```bash
/session:reflect --type task --analyze      # Check task adherence
/session:reflect --type session --validate  # Assess session progress
/session:reflect --type completion          # Validate completion criteria
```

**Types:** `task`, `session`, `completion`

## Putting It Together

A typical feature development session:

```
# 1. Start fresh
/session:load

# 2. Ideate
/ctx:brainstorm
> "Build a user settings page with profile editing and notification preferences"

# 3. Plan
/ctx:plan
> Creates 3 workstreams: API, Frontend, Tests

# 4. Execute
/ctx:execute-plan
> Tracks tasks, runs quality gates

# 5. Build
/dev:implement          # Write code
/dev:code-review        # Review quality
/test:generate          # Generate tests

# 6. Mid-session check
/session:reflect --type task

# 7. Wrap up
/session:save --summarize
```

## TUI Task View

Press `T` in the TUI to manage tasks created by the planning workflow:

| Key | Action |
|:----|:-------|
| `T` | Open Task view |
| `A` | Add new task |
| `E` | Edit task |

Tasks are organized by category and workstream, matching the plan structure from `/ctx:plan`.

## Skill Auto-Suggester

The collaboration commands are automatically suggested by the skill auto-suggester hook when it detects relevant keywords in your prompts. For example, typing "let's brainstorm" triggers a suggestion for the brainstorming skill.

Keyword mappings are defined in `skills/skill-rules.json`.
