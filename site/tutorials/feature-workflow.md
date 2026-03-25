---
layout: default
title: Feature Workflow in Cortex
parent: Tutorials
nav_order: 4
---

# Feature Workflow in Cortex

This tutorial shows a practical feature-development flow in Cortex from initial
planning through implementation, review, and commit.

The goal is not to use every Cortex feature. The goal is to combine the parts
that help most during real work:

- skill recommendations
- agent recommendations and activation
- isolated worktrees
- tmux-based task windows
- `agent-loops` quality gates
- safe Git commits

## What You'll Learn

- how to prepare a feature task before you start editing files
- how to use `cortex skills` and `cortex ai` together without mixing them up
- how to isolate work with `cortex git worktree`
- how to run the work inside a tmux window
- how to finish with review-oriented skills and an atomic commit

## Prerequisites

- Cortex installed locally
- a git-backed repository
- a feature idea small enough to fit in one focused implementation slice

## Time Estimate

~20-30 minutes

---

## Scenario

Assume you want to add a small feature to the project. You want a workflow that
keeps context organized, reduces accidental blast radius, and ends with a clean
commit.

## Step 1: Plan the Slice

Before you ask Cortex for anything, define the slice clearly in your own words:

- what user-visible outcome are you trying to create?
- what files or areas are likely involved?
- how will you know the feature is done?

For a first pass, keep the slice small enough that you could describe the done
state in one short paragraph.

A good planning note usually includes:

1. the feature goal
2. the main constraints or risks
3. the smallest reviewable change that would count as progress

This matters because the rest of Cortex works better when the task is already
scoped rather than fuzzy.

## Step 2: Ask for Skill Recommendations

Start with the skill side of the workflow:

```bash
cortex skills recommend
```

Then generate the current skill context:

```bash
cortex skills context --no-write
```

Use this to answer:

- what knowledge packs fit this feature?
- what instructions or references should be active in your head before coding?

The distinction is:

- `cortex skills recommend` suggests what knowledge to use
- `cortex skills context` packages that recommendation into a usable summary

### Checkpoint

- [ ] Wrote a small plan for the feature slice
- [ ] Ran `cortex skills recommend`
- [ ] Ran `cortex skills context --no-write`

## Step 3: Ask for Agent Recommendations

Now switch to the agent side:

```bash
cortex ai recommend
```

If the recommendation looks useful, activate the smallest agent set that fits
the task:

```bash
cortex agent activate code-reviewer
```

Or activate more than one when the task genuinely needs it:

```bash
cortex agent activate python-pro code-reviewer
```

Keep the distinction clean:

- **skills** = instruction and reference packs
- **agents** = active specialist personas

## Step 4: Isolate the Work in a Worktree

Create a worktree for the feature branch:

```bash
cortex git worktree add feat/my-feature --base main
```

This gives you a clean place to work without mixing unrelated repository state
into the slice.

If you want to inspect current worktrees first:

```bash
cortex git worktree list
```

The worktree step is one of the highest-value habits in the whole workflow,
especially if you expect parallel work or a long-running branch.

## Step 5: Start a Dedicated Tmux Window

Create a named window for the feature work:

```bash
cortex tmux new feature
```

Start the work inside it:

```bash
cortex tmux send feature "cd path/to/worktree && $SHELL"
```

Or kick off a long-running task directly:

```bash
cortex tmux send feature "pytest -m unit"
```

You can inspect output without attaching:

```bash
cortex tmux read feature 80
cortex tmux wait feature 180
```

This keeps the task runtime isolated the same way the worktree keeps the Git
state isolated.

## Step 6: Implement with Agent Loops

Once the task is scoped and isolated, use the implementation-quality workflow:

```text
/ctx:agent-loops
```

This is the point where you drive the actual code change through the normal
quality gates instead of improvising your own review discipline.

Pair it with:

```text
/ctx:test-generation
/ctx:requesting-code-review
```

A practical mental model is:

1. implement the smallest complete change
2. generate or tighten tests
3. request review-oriented scrutiny
4. fix findings if needed

## Step 7: Commit the Feature Slice Safely

When the slice is ready, commit only the specific files you intend to ship:

```bash
cortex git commit "feat(scope): add feature slice" path/to/file1 path/to/file2
```

This is safer than staging the whole tree because the wrapper:

- requires explicit file paths
- unstages everything first
- stages only the paths you named

If the feature needs another small follow-up change, treat that as a second
loop, not as a reason to widen the first commit.

## Step 8: Optional Push and Follow-On Handoff

If the branch is ready to share:

```bash
cortex git push
```

If the feature needs a downstream handoff instead:

```bash
cortex export context feature-context.md --include core --include skills
```

That gives you a clean bridge to another agent, another session, or an external
LLM without having to restate the whole task manually.

## Suggested End-to-End Loop

A practical end-to-end flow looks like this:

```text
1. Define the smallest reviewable feature slice
2. cortex skills recommend
3. cortex skills context --no-write
4. cortex ai recommend
5. cortex agent activate ...
6. cortex git worktree add ...
7. cortex tmux new ...
8. /ctx:agent-loops
9. /ctx:test-generation
10. /ctx:requesting-code-review
11. cortex git commit ...
```

That sequence keeps planning, context, execution, review, and Git hygiene tied
together instead of leaving them as separate habits.

## Summary

The strongest feature workflow in Cortex is not "use every tool." It is:

1. scope the task clearly
2. get the right skill context
3. activate the right agents
4. isolate Git state with a worktree
5. isolate runtime with tmux
6. use `agent-loops` for implementation discipline
7. finish with an atomic commit

## Related

- [Skills to Context Handoff]({% link tutorials/skill-recommendations.md %}) -- prepare the skill side of the task
- [Export Context for Handoffs]({% link tutorials/export-context.md %}) -- hand the feature off cleanly if needed
- [Git Workflow]({% link guides/git-workflow.md %}) -- deeper guide to worktrees and atomic commits
- [Tmux Workflow]({% link guides/tmux-workflow.md %}) -- deeper guide to task-window orchestration
