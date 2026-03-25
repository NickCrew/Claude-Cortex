---
layout: default
title: Multi-LLM Consult
parent: Guides
nav_order: 12
---

# Multi-LLM Consult

`multi-llm-consult` is the cross-model consultation workflow in Cortex. Use it
when you want a second opinion, an alternative plan, an independent review, or
a delegated analysis from another model family.

The generated skill-backed command is:

```text
/ctx:multi-llm-consult
```

## When To Use It

Use this workflow when:

- you want another model's perspective before acting
- you want to compare plans
- you want an external review or critique
- you want to delegate a bounded analysis task to another model

## Recommended Workflow

The high-value pattern is:

1. prepare the task
2. export or summarize only the needed context
3. sanitize anything sensitive
4. ask the other model a narrow question
5. compare the result against repo reality before acting

## Good Inputs

Good consult requests are:

- specific
- bounded
- sanitized
- paired with the right context bundle

Example purposes from the skill:

- second opinion
- plan check
- independent review
- delegated task

## Pair It With Export

This workflow becomes much more useful when paired with `cortex export`:

```bash
cortex export context - --include core --include skills > /tmp/consult-context.md
cortex skills context --no-write > /tmp/consult-skills.md
```

That gives you a compact bundle for another model without dumping unrelated
repo context into the prompt.

## Pair It With Skills

A strong consultation flow is:

```bash
cortex skills recommend
cortex skills context --no-write
```

Then use the relevant skills, or pass that skill context into the consult
request so the other model understands the intended working style.

## Best Uses

### Second opinion

You already have a plan and want another model to poke holes in it.

### Independent review

You want an outside perspective on risk, correctness, or blind spots.

### Delegated analysis

You want another model to answer a narrow question while you keep the main flow
moving.

## Important Constraints

- Treat the external answer as advisory.
- Verify against the current repo and CLI surface before acting.
- Do not send sensitive data unless you have explicitly decided it is safe.
- Prefer narrow prompts over broad "analyze everything" prompts.

## Related

- [Export Context]({% link guides/export.md %}) -- package context for outside consultation
- [Skills]({% link guides/skills.md %}) -- produce a skill shortlist before consulting
- [Review Recommendations]({% link guides/review.md %}) -- standalone review-oriented skill recommendations
