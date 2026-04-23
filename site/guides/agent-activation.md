---
layout: default
title: Agent Activation
parent: Guides
nav_order: 5
---

# Agent Activation

Agents are the working personas you activate for a task. This is different from
skills:

- **agents** are active workers or specialists
- **skills** are instruction packs you load when needed

This guide is about the user-facing agent workflow: inspect agents, activate the
right ones, understand dependencies, and know when to let recommendations help.

## Core Commands

```bash
cortex agent list
cortex agent status
cortex agent activate code-reviewer
cortex agent deactivate code-reviewer
```

Useful inspection commands:

```bash
cortex agent deps code-reviewer
cortex agent graph
cortex agent validate
```

## Three Ways Agents Get Activated

### 1. Manual activation

Use this when you already know which specialist you want:

```bash
cortex agent activate security-auditor
cortex agent activate python-pro code-reviewer
```

This is the most direct path and the easiest one to reason about.

### 2. AI recommendations

Use the agent intelligence system when you want Cortex to suggest who should be
active based on the current repo context:

```bash
cortex suggest
cortex suggest --activate
```

This is recommendation-driven activation, not skill loading.

### 3. Dependency-driven activation

Some agents pull in related dependencies. Use the dependency tools to
understand what an activation implies:

```bash
cortex agent deps architect-review
cortex agent graph
```

## Activation Workflow

The practical flow is:

1. check what is active now
2. inspect the current task
3. activate the smallest useful set of agents
4. deactivate agents that are no longer relevant

Example:

```bash
# Inspect current state
cortex agent status

# Activate the specialists you need
cortex agent activate python-pro code-reviewer

# Later, trim back the set
cortex agent deactivate python-pro
```

## Deactivation

Deactivation matters because an overgrown active set can add noise.

```bash
cortex agent deactivate code-reviewer
cortex agent deactivate architect-review --force
```

`--force` exists because dependency checks can block deactivation when other
agents still rely on the one you are removing.

## TUI Workflow

```bash
cortex tui
```

Then:

- press `2` for the Agents view
- inspect active versus available agents
- activate or deactivate directly from the interface
- use `0` to compare against AI recommendations in the AI Assistant view

## When To Use Agents vs Skills

Use **agents** when:

- you want a specialist persona active for the task
- you want recommendation-driven activation from `cortex suggest`
- you are managing the working set of collaborators

Use **skills** when:

- you want reusable instructions or references
- you want prompt-time or recommender-driven skill suggestions
- you want a context file for another session or model

## Related

- [AI Intelligence]({% link guides/ai-intelligence.md %}) -- recommendation-driven agent workflow
- [Skills]({% link guides/skills.md %}) -- separate skill workflow
- [Export Context]({% link guides/export.md %}) -- package agent and skill context for handoff
