# Task Execution Workflow

How to work assigned tasks systematically from start to completion.

## Step 1: Claim the Task

Set the task to "In Progress" and assign to yourself:

```bash
backlog task edit 42 -s "In Progress" -a @myself
```

## Step 2: Read Everything

View the complete task:

```bash
backlog task 42 --plain
```

**Read ALL fields:**
- **Title**: What is this task?
- **Description**: Why does this exist? What's the goal?
- **Acceptance Criteria**: What defines "done"? (numbered list)
- **Definition of Done**: Additional checklist items (tests, docs, etc.)
- **References**: File paths or URLs relevant to implementation
- **Documentation**: Links to design docs, specs, related materials

**Open any attached files/URLs** to understand context. You have access to parent directories and can fetch permitted files.

## Step 3: Understand the Implementation Plan

If an implementation plan exists, review it. It was created with context about how to approach the work.

If creating a plan (new work, not deferred), create one now:

```bash
backlog task edit 42 --plan "1. Research approach\n2. Analyze codebase\n3. Implement\n4. Test"
```

**Share plan with user and wait for approval before writing code.**

## Step 4: Implement Systematically

Work through acceptance criteria in order. After completing each:

```bash
backlog task edit 42 --check-ac 1    # Mark AC #1 complete
# implement more...
backlog task edit 42 --check-ac 2    # Mark AC #2 complete
```

**Record your progress progressively:**

```bash
backlog task edit 42 --append-notes "Completed AC #1: basic functionality working"
backlog task edit 42 --append-notes "Fixed edge case in AC #2"
```

## Step 5: Write Final Summary

When implementation complete, write PR-quality summary:

```bash
backlog task edit 42 --final-summary "Implemented feature X with strategy pattern for extensibility. Added 5 new tests covering edge cases. Files: src/parser.ts, src/strategies/. No breaking changes."
```

Quality bar: Write as if reviewer will read it. Include what changed, why, scope, and tests.

## Step 6: Complete Definition of Done

Check all Definition of Done items:

```bash
backlog task edit 42 --check-dod 1
backlog task edit 42 --check-dod 2
```

Ensure:
- ✅ Tests pass (run locally)
- ✅ Linting clean
- ✅ Documentation updated if needed
- ✅ No regressions

## Step 7: Mark Complete

```bash
backlog task edit 42 -s Done
```

## Definition of Done Checklist

Task is truly complete only when ALL are satisfied:

- [ ] All acceptance criteria checked (visible in task)
- [ ] All definition of done items checked (visible in task)
- [ ] Final summary written (PR-quality)
- [ ] Status set to "Done"
- [ ] Tests pass locally
- [ ] Code self-reviewed
- [ ] No regressions introduced
- [ ] Related documentation updated

## Understanding Task Fields

| Field | Meaning | How to Use |
|-------|---------|-----------|
| **Description** | Why this task exists, the goal/context | Read to understand purpose |
| **Acceptance Criteria** | Numbered list of success conditions | Follow each one systematically |
| **Definition of Done** | Quality/process checklist | Check items off as complete |
| **Implementation Plan** | How to approach the work | Follow steps (or create if new) |
| **References** | File paths, URLs, related resources | Open and read as needed |
| **Documentation** | Links to design/spec docs | Review to understand requirements |
| **Implementation Notes** | Your progress log | Append as you make progress |
| **Final Summary** | PR description for reviewers | Write when implementation done |

## Common Patterns

### When Task Has No Implementation Plan

Create one before starting code:
```bash
backlog task edit 42 --plan "1. Research dependencies\n2. Design approach\n3. Implement\n4. Test and verify"
backlog task edit 42 --append-notes "Plan created and shared with user for approval"
```

### When You Get Blocked

Don't mark task done. Instead:
1. Document the blocker in notes: `backlog task edit 42 --append-notes "Blocked on: XYZ service unavailable"`
2. Leave task in "In Progress"
3. Notify user of blocker

### When Scope Expands

Don't add scope silently. Instead:
1. Update AC first: `backlog task edit 42 --ac "New requirement"`
2. Or create follow-up task: `backlog task create "Follow-up: New feature"`
3. Don't exceed original AC without discussion

### When AC Is Ambiguous

Read References and Documentation carefully. If still unclear:
- Append notes: `backlog task edit 42 --append-notes "AC #2 ambiguous—clarifying with user"`
- Pause implementation
- Notify user
