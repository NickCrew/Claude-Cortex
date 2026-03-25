---
layout: default
title: Review Prep with Cortex Review
parent: Tutorials
nav_order: 8
---

# Review Prep with Cortex Review

This tutorial shows how to use `cortex review` to prepare for review work.

The key idea is simple: `cortex review` is not a full review engine. It is a
standalone recommendation step that helps you load the right review-relevant
skills before you review a diff manually or with another agent.

## What You'll Learn

- how to use `cortex review --dry-run` to preview review-oriented skills
- how to add context signals with `--context`
- how to turn the recommendations into a usable skill-loading step
- how to keep `cortex review` separate from the larger `agent-loops` workflow

## Prerequisites

- Cortex installed locally
- a code change, diff, or review target in front of you
- a reason to review from a specific angle such as debugging, feature work, or
  security

## Time Estimate

~10-15 minutes

---

## What Cortex Review Actually Does

`cortex review` looks at the current working context, adds any extra context
signals you provide, and recommends review-relevant skills to load before you
proceed.

That means its job is:

- detect the kind of review you are about to do
- suggest skills that fit that review
- give you a clean starting point before the real review begins

It does **not** do the whole review for you.

## What It Is Not

Keep this distinction clean:

- `cortex review` prepares review work
- `agent-loops` is a broader implementation workflow with its own review and
  test-audit gates

You can use both in the same session, but they are not the same tool and one
does not replace the other.

## Step 1: Start with a Dry Run

Preview the recommendations first:

```bash
cortex review --dry-run
```

The output varies by repo and current context, but the point of the dry run is
always the same:

- see what review-oriented skills Cortex thinks matter
- decide whether the current signal looks right
- avoid blindly loading a stack of skills you do not need

## Step 2: Add Context Signals When Needed

If the review needs a specific lens, add it explicitly:

```bash
cortex review --dry-run --context debug
cortex review --dry-run --context feature --context security
```

This is useful when the current diff alone does not fully express the kind of
review you want.

Good examples:

- `--context debug` when the review is tied to a bug fix or regression
- `--context feature` when you want review discipline around new behavior
- `--context security` when risk analysis matters more than style feedback

## Step 3: Load the Suggested Skill Context

Once the recommendation looks right, turn it into a usable session step:

```bash
cortex skills context --no-write
```

That gives you the skill context you can load or reference while you review.

Depending on the situation, common follow-on skills can include:

- `/ctx:requesting-code-review`
- `/ctx:doc-claim-validator`
- `/ctx:security-testing-patterns`
- `/ctx:python-testing-patterns`

The exact mix will vary. The important thing is to use `cortex review` to
narrow the field before you start.

## Step 4: Perform the Actual Review

After the prep step, move into the review itself.

For a code review flow, a common handoff is:

```text
/ctx:requesting-code-review
```

For documentation-heavy changes, you may instead want:

```text
/ctx:doc-claim-validator
```

For security-sensitive work, you may want the review to lean on:

```text
/ctx:security-testing-patterns
```

The point is that `cortex review` helps you pick the right lens before you use
the actual review workflow.

## Step 5: Keep the Outcome in the Main Session

Once the review-relevant skills are loaded, stay grounded in your real task:

1. review the diff or files
2. capture findings clearly
3. decide what needs to change
4. rerun the prep step only if the review context changes materially

`cortex review` should shorten the path to a better review. It should not turn
into a separate workflow you have to maintain on its own.

## Safe Defaults

If you are unsure, use this pattern:

1. run `cortex review --dry-run`
2. add one `--context` value if the review needs a specific angle
3. run `cortex skills context --no-write`
4. load the most relevant review skill
5. perform the actual review

That keeps the tool focused on preparation, which is what it is built for.

## Summary

The workflow is:

1. preview review recommendations
2. add context when the review needs a clear lens
3. load the suggested skill context
4. run the actual review with the right skill

That is the best way to use `cortex review`: as a composable review-prep
helper, not as a replacement for the review itself.

## Related

- [Review Recommendations]({% link guides/review.md %}) -- reference guide for the `cortex review` command
- [Bug Fix Workflow in Cortex]({% link tutorials/bug-fix-workflow.md %}) -- see how review prep fits into a debugging flow
- [Multi-LLM Consultation Workflow]({% link tutorials/multi-llm-consultation.md %}) -- take curated review context to another model if needed
- [Agent Loops]({% link guides/agent-loops.md %}) -- separate implementation discipline workflow
