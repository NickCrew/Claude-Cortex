---
layout: default
title: Bug Fix Workflow in Cortex
parent: Tutorials
nav_order: 5
---

# Bug Fix Workflow in Cortex

This tutorial walks through a practical Cortex flow for debugging and fixing a
bug without skipping the investigation step.

The point of the workflow is to keep you from jumping straight into edits based
on a guess. Cortex is most useful here when it helps you separate:

- symptom capture
- diagnosis
- fix implementation
- regression protection
- review and commit

## What You'll Learn

- how to capture a bug clearly before changing code
- how to use `cortex skills` to load the right debugging context
- how to use `systematic-debugging` as the diagnosis phase
- how to connect the fix to tests, review, and a safe commit

## Prerequisites

- Cortex installed locally
- a reproducible bug, failing behavior, or suspicious regression
- a git-backed repository

## Time Estimate

~20-30 minutes

---

## Scenario

Assume something is broken or behaving unexpectedly. You do not yet know the
cause, and that uncertainty is the most important fact in the room.

Your job is to move from:

- "I see a symptom"

to:

- "I understand the root cause and I have a small fix with regression
  protection"

## Step 1: Capture the Symptom

Before asking Cortex for recommendations, write down the bug in concrete terms:

- what is happening?
- what did you expect instead?
- how can you reproduce it?
- what files, components, or commands seem closest to the failure?

Keep this note small and factual. You are not solving yet. You are creating the
debugging input.

## Step 2: Ask for Skill Context

Now ask Cortex which skills fit the bug-fix task:

```bash
cortex skills recommend
```

Then capture the current skill context:

```bash
cortex skills context --no-write
```

This helps you load the right debugging, testing, or review-oriented skills
before you start changing files.

### Checkpoint

- [ ] Captured the bug symptom and reproduction
- [ ] Ran `cortex skills recommend`
- [ ] Ran `cortex skills context --no-write`

## Step 3: Diagnose with Systematic Debugging

Do not jump straight to the fix. Use the debugging workflow first:

```text
/ctx:systematic-debugging
```

Treat this as the root-cause phase. The goal is to understand:

- what actually failed
- what evidence supports the failure theory
- what the smallest plausible fix would be

This keeps bug-fix work distinct from feature work. In a feature flow, you are
deciding what to build. In a bug-fix flow, you are trying to avoid guessing.

## Step 4: Implement the Fix with Agent Loops

Once you understand the likely cause, move into the implementation discipline:

```text
/ctx:agent-loops
```

The important handoff here is:

- `systematic-debugging` explains the cause
- `agent-loops` controls how you change the code safely

Keep the fix narrow. If the bug reveals larger cleanup opportunities, note them
for later instead of widening the first repair.

## Step 5: Add or Tighten Regression Tests

After the fix shape is clear, use the testing workflow:

```text
/ctx:test-generation
```

For a bug fix, the test question is simple:

- what check would have caught this problem before?

The best outcome is usually one focused regression test or one tightened
existing test, not a big speculative test sweep.

## Step 6: Prepare Review with Debug Context

Before review, use the standalone review-recommendation helper:

```bash
cortex review --context debug
```

This helps Cortex suggest review-relevant skills for the debugging scenario.

Then run the review-oriented skill flow:

```text
/ctx:requesting-code-review
```

That keeps the review step grounded in the actual bug-fix context instead of
treating it like a generic code pass.

## Step 7: Commit the Fix Safely

When the bug fix and regression check are ready, commit only the specific files
that belong in the repair:

```bash
cortex git commit "fix(scope): resolve regression" path/to/file1 path/to/file2
```

This matters even more in bug-fix work than in feature work. Fixes often happen
under time pressure, which makes accidental staging more likely if you rely on
raw Git habits.

## Optional Handoff If You Get Stuck

If the bug is still ambiguous after the first diagnosis loop, package context
for another worker:

```bash
cortex export context bug-context.md --include core --include skills
```

That gives you a clean bridge to another session, sub-agent, or external model
without re-explaining the entire issue from scratch.

## Suggested End-to-End Loop

A practical bug-fix loop looks like this:

```text
1. Capture the symptom and reproduction
2. cortex skills recommend
3. cortex skills context --no-write
4. /ctx:systematic-debugging
5. /ctx:agent-loops
6. /ctx:test-generation
7. cortex review --context debug
8. /ctx:requesting-code-review
9. cortex git commit ...
```

This is different from the feature workflow because diagnosis is the center of
gravity, not implementation planning.

## Summary

The strongest Cortex bug-fix workflow is:

1. capture the symptom precisely
2. load the right skill context
3. diagnose before editing
4. keep the code change small
5. add a regression check
6. review with debug context
7. finish with an atomic fix commit

## Related

- [Feature Workflow in Cortex]({% link tutorials/feature-workflow.md %}) -- compare the build-new flow against the fix-existing flow
- [Skills to Context Handoff]({% link tutorials/skill-recommendations.md %}) -- generate the skill context that feeds the debugging loop
- [Review Recommendations]({% link guides/review.md %}) -- use `cortex review` as a composable review helper
- [Git Workflow]({% link guides/git-workflow.md %}) -- deeper guide to atomic commits and worktree hygiene
