---
layout: default
title: Export Context
parent: Guides
nav_order: 11
---

# Export Context

`cortex export` packages context into a form you can hand to another session,
sub-agent, or external LLM. This is one of the most practical bridge workflows
in Cortex.

## What Export Is For

Use export when you need to:

- hand context to a sub-agent
- consult another LLM with a curated bundle
- share only the parts of Cortex that matter for the current task
- export specific agent definitions

## Core Commands

```bash
cortex export list
cortex export context -
cortex export agents code-reviewer
```

The main export categories exposed by the CLI are:

- `core`
- `rules`
- `modes`
- `agents`
- `mcp_docs`
- `skills`

## Exporting Session Context

Write to stdout:

```bash
cortex export context -
```

Write to a file:

```bash
cortex export context review-context.md
```

Restrict the export:

```bash
cortex export context - --include core --include skills
cortex export context - --exclude mcp_docs --exclude skills
```

Exclude a specific file:

```bash
cortex export context - --exclude-file rules/quality-rules.md
```

## Exporting Agents

Export one or more agent definitions directly:

```bash
cortex export agents code-reviewer
cortex export agents code-reviewer security-auditor --output review-agents.md
```

This is useful when the handoff is specifically about agent behavior rather
than a broader session context bundle.

## Agent-Generic vs Claude-Specific Output

Both context and agent export support:

```bash
--no-agent-generic
```

Use the default output when you want a general handoff format. Use
`--no-agent-generic` when you specifically want the Claude-oriented format.

## Export Workflow For Sub-Agents

One reliable pattern is:

```bash
# Build a compact context bundle
cortex export context - --include core --include rules --include skills > /tmp/task-context.md

# Optionally generate a skill shortlist too
cortex skills context --no-write > /tmp/skill-context.md
```

Then hand the exported files to the sub-agent or downstream workflow.

## Export Workflow For External LLM Consultation

When consulting another model:

1. export only the categories that matter
2. remove or avoid sensitive data
3. pair the export with a focused prompt
4. treat the response as advisory, not authoritative

This is especially useful alongside the `multi-llm-consult` skill.

## Related

- [Skills]({% link guides/skills.md %}) -- generate skill context for the current task
- [Multi-LLM Consult]({% link guides/llm-consult.md %}) -- use exports in external model consultation
- [Agent Activation]({% link guides/agent-activation.md %}) -- export active-agent context intentionally
