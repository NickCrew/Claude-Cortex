---
layout: default
title: Review Recommendations
parent: Guides
nav_order: 8
---

# Review Recommendations

`cortex suggest --review` is a standalone recommendation surface for review work. It is
not the same thing as the `agent-loops` workflow.

The job of `cortex suggest --review` is:

> Suggest which review-relevant skills should be loaded before you perform a
> review.

## What It Is Not

`cortex suggest --review` does **not** run the full `agent-loops` review/test-audit loop
for you. `agent-loops` is a larger implementation discipline workflow. `cortex
review` is a composable helper you can use before review work begins.

## Core Command

```bash
cortex suggest --review --dry-run
cortex suggest --review --context debug
cortex suggest --review --context feature --context security
```

The command takes optional context signals and recommends review-relevant
skills based on what kind of review you are about to do.

## When To Use It

Use `cortex suggest --review` when:

- you are about to review a diff manually
- you want Cortex to suggest the right skills before reviewing
- you are preparing a review-oriented handoff for another agent or model

It is especially useful when the review mode is not obvious from the diff alone
and you want a nudge toward the right review discipline.

## Practical Workflow

```bash
# Ask for review-oriented skill recommendations
cortex suggest --review --context security --context api

# Build skill context for the session if needed
cortex skills context --no-write
```

Then load the suggested skills or use their generated slash-command aliases.

Common follow-on skills include:

- `/ctx:requesting-code-review`
- `/ctx:doc-claim-validator`
- `/ctx:security-testing-patterns`
- `/ctx:python-testing-patterns`

## Relationship To Agent Loops

Keep the distinction clean:

- **`cortex suggest --review`** recommends review-relevant skills
- **`agent-loops`** is the full implementation workflow with review, test audit,
  lint, and commit gates

That means `cortex suggest --review` can be used on its own, or it can be one piece of a
larger composable workflow.

## Related

- [Agent Loops]({% link guides/agent-loops.md %}) -- full implementation discipline workflow
- [Skills]({% link guides/skills.md %}) -- inspect or rate the skills being recommended
- [Multi-LLM Consult]({% link guides/llm-consult.md %}) -- take review context to another model if needed
