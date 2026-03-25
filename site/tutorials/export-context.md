---
layout: default
title: Export Context for Handoffs
parent: Tutorials
nav_order: 2
---

# Export Context for Handoffs

This tutorial shows how to use `cortex export` to hand the right amount of
context to another worker without dumping the entire project state on them.

The core idea is simple:

- export only what the next worker needs
- choose different export shapes for sub-agents and external LLMs
- keep the handoff small enough to reason about

## What You'll Learn

- how to select export categories intentionally
- how to exclude noisy categories or specific files
- when to export broader session context versus specific agent definitions
- how to shape exports differently for sub-agents and external LLMs

## Prerequisites

- Cortex installed locally
- a task you want to hand off
- a destination in mind:
  another session, a sub-agent, or an external model

## Time Estimate

~10 minutes

---

## Scenario

Assume you have already figured out what the next worker needs to do. Your job
now is to package the context for them.

There are two common handoff targets:

- a sub-agent or another Cortex session
- an external LLM you are consulting for a second opinion

Those two targets often want different export shapes.

## Step 1: Start with a Minimal Context Export

The main command is:

```bash
cortex export context handoff-context.md
```

You can also print to stdout:

```bash
cortex export context -
```

The export command works with these context categories:

- `core`
- `rules`
- `modes`
- `agents`
- `mcp_docs`
- `skills`

The most important choice is usually not "Can I export context?" It is "Which
parts belong in this handoff?"

## Step 2: Use Selective Include Patterns

When you already know what matters, use `--include` instead of exporting
everything:

```bash
cortex export context handoff-context.md --include core --include skills
```

This is a good starting point when the downstream worker mainly needs:

- core project context
- the relevant skill material

For many tasks, that is enough.

### Checkpoint

- [ ] Chose a target file or stdout export
- [ ] Selected a minimal include set
- [ ] Avoided exporting categories just because they exist

## Step 3: Remove Noise with Exclusions

Sometimes it is easier to start broad and trim back:

```bash
cortex export context handoff-context.md --exclude mcp_docs --exclude agents
```

Or exclude one especially noisy file:

```bash
cortex export context handoff-context.md \
  --exclude-file rules/quality-rules.md
```

This is useful when one category or file adds a lot of text without helping the
next worker do the task.

## Step 4: Sub-Agent Handoff Pattern

For another Cortex session or sub-agent, you usually want a practical working
bundle rather than a polished external prompt.

One reliable pattern is:

```bash
# Export the main working context
cortex export context /tmp/task-context.md --include core --include rules --include skills

# Export specific agent definitions only if the downstream worker needs them
cortex export agents code-reviewer security-auditor \
  --output /tmp/review-agents.md
```

Use this when:

- the next worker is operating inside the same ecosystem
- rules and skills matter more than presentation polish
- you want to pass specific agent definitions on purpose

## Step 5: External LLM Handoff Pattern

For an external LLM, prefer a tighter export:

```bash
cortex export context /tmp/llm-context.md --include core --include skills
```

If you need Claude-oriented formatting rather than the default agent-generic
format:

```bash
cortex export context /tmp/llm-context.md \
  --include core --include skills \
  --no-agent-generic
```

The safe default for an external model is:

- include fewer categories
- remove obviously noisy files
- pair the export with a focused prompt
- treat the result as advisory

## Step 6: Export Agents Only When They Matter

Sometimes the handoff is specifically about agent behavior, not the whole
session bundle.

In that case:

```bash
cortex export agents code-reviewer
cortex export agents code-reviewer security-auditor --output agents.md
```

This is a better fit than a full context export when you are sharing how a
particular worker should behave, not all the surrounding repo context.

## Safe Defaults

If you are unsure, use these defaults:

1. start with `--include core --include skills`
2. add `rules` only when the downstream worker needs repo-specific guardrails
3. avoid `mcp_docs` unless external documentation is central to the task
4. export `agents` separately when agent definitions matter on their own
5. use `--exclude-file` for known noisy files instead of giving up on export

## Common Mistakes

- exporting every category by default
- using the same export shape for sub-agents and external LLMs
- mixing agent definitions into every handoff whether they are needed or not
- forgetting that smaller exports are usually easier for the next worker to use

## Summary

The workflow is:

1. choose the handoff target
2. export only the categories that matter
3. trim noise with `--exclude` or `--exclude-file`
4. export agents separately when behavior matters
5. hand off a curated bundle, not a dump

That keeps `cortex export` aligned with its real job: packaging useful context
for the next worker, not maximizing document size.

## Related

- [Skills to Context Handoff]({% link tutorials/skill-recommendations.md %}) -- pair skill recommendations with context export
- [Export Context]({% link guides/export.md %}) -- reference guide to export commands and options
- [Multi-LLM Consult]({% link guides/llm-consult.md %}) -- consult another model with an exported bundle
