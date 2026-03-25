---
layout: default
title: Skills to Context Handoff
parent: Tutorials
nav_order: 1
---

# Skills to Context Handoff

This tutorial walks through one of the most useful Cortex workflows:

1. ask Cortex which skills fit the current task
2. turn those recommendations into a compact skill context
3. export a broader context bundle for another session, sub-agent, or external
   LLM

The goal is not just to get suggestions. The goal is to produce a clean
handoff package that another worker can act on quickly.

## What You'll Learn

- how `cortex skills recommend` and `cortex skills context` fit together
- how `cortex export context` complements the skill context file
- how to build a compact handoff bundle for another agent or model
- how to record whether the recommendation actually helped afterward

## Prerequisites

- Cortex installed and available on your shell path
- a project with real task context or changed files
- a downstream target in mind:
  another session, a sub-agent, or an external LLM

## Time Estimate

~10-15 minutes

---

## Scenario

Assume you are about to hand a task to another worker. You want Cortex to help
you answer two different questions:

- which skills matter for this task?
- what supporting context should the downstream worker receive?

Those are related, but they are not the same thing.

## Step 1: Ask for Skill Recommendations

Start with the shortest recommendation path:

```bash
cortex skills recommend
```

This is the "what should I load right now?" command. It gives you a shortlist
based on the current repo and task context.

### What to look for

You should see a small set of relevant skills, not a giant catalog dump.
Examples might include docs, debugging, review, or workflow-oriented skills
depending on the repository state.

### Checkpoint

- [ ] Ran `cortex skills recommend`
- [ ] Saw a shortlist of recommended skills
- [ ] Identified which one or two skills actually match the task

## Step 2: Generate Skill Context

Now turn the recommendation into a reusable skill context bundle:

```bash
# Write .claude/skill-context.md
cortex skills context
```

If you want to inspect it without writing a file:

```bash
cortex skills context --no-write
```

This step is different from `skills recommend`:

- `skills recommend` gives you a shortlist
- `skills context` turns that shortlist into a lightweight task-ready artifact

The output is useful when another worker needs the recommended skill set in a
single readable block instead of a transient terminal recommendation.

### Checkpoint

- [ ] Ran `cortex skills context` or `cortex skills context --no-write`
- [ ] Confirmed the skill context matches the recommendation shortlist
- [ ] Verified the output is compact enough to hand off

## Step 3: Export Broader Task Context

The skill context alone is often not enough. The next worker may also need core
project context, rules, or selected skill content in one export bundle.

Write the bundle to stdout:

```bash
cortex export context -
```

Write it to a file:

```bash
cortex export context task-context.md
```

For a tighter handoff, include only the categories you want:

```bash
cortex export context task-context.md --include core --include skills
```

Or exclude categories that would add noise:

```bash
cortex export context task-context.md --exclude mcp_docs --exclude agents
```

You can also remove a specific file from the export:

```bash
cortex export context task-context.md --exclude-file rules/quality-rules.md
```

## Step 4: Build a Clean Handoff Package

One reliable pattern is:

```bash
# 1. Ask Cortex which skills fit the task
cortex skills recommend

# 2. Build a compact skill summary
cortex skills context --no-write > /tmp/skill-context.md

# 3. Export the broader task bundle
cortex export context /tmp/task-context.md --include core --include skills
```

At this point you have:

- `/tmp/skill-context.md` for the recommendation-focused summary
- `/tmp/task-context.md` for the broader session handoff

That split is useful:

- the skill context explains what Cortex thinks is relevant
- the export bundle provides the downstream working context

## Step 5: Use the Handoff

### For another agent or session

Use the exported files as part of the task handoff so the next worker starts
with the right context instead of recomputing it from scratch.

### For an external LLM

Use the same bundle, but keep the export selective. Prefer:

- only the categories needed for the task
- focused prompts
- no unnecessary or sensitive context

Treat the external response as advisory input, not as automatic truth.

## Step 6: Record Whether the Recommendation Helped

After the task, tell Cortex whether the recommendation was actually useful:

```bash
cortex skills feedback documentation-production helpful
```

Or:

```bash
cortex skills feedback documentation-production not-helpful
```

You can attach a short explanation:

```bash
cortex skills feedback documentation-production helpful \
  --comment "Useful for restructuring the public docs flow"
```

This closes the loop between "Cortex suggested a skill" and "that suggestion
was or was not actually helpful in practice."

## Common Mistakes

- treating `skills recommend` and `skills context` as the same thing
- exporting everything when only `core` and `skills` are needed
- handing off recommendations without any broader context bundle
- using export as a dumping ground instead of a curated handoff

## Summary

You now have a repeatable workflow:

1. `cortex skills recommend`
2. `cortex skills context`
3. `cortex export context`
4. hand off the result
5. record recommendation feedback

That pattern is one of the cleanest ways to move from Cortex recommendation to
real downstream execution.

## Related

- [Skills]({% link guides/skills.md %}) -- deeper guide to recommendation, context, ratings, and audit flows
- [Export Context]({% link guides/export.md %}) -- reference guide to selective export patterns
- [Multi-LLM Consult]({% link guides/llm-consult.md %}) -- use exported context with another model
