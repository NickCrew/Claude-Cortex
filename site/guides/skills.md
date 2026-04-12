---
layout: default
title: Skills
parent: Guides
nav_order: 4.1
---

# Skills

Skills are reusable knowledge packs that Cortex can suggest, inspect, and rate.
They are different from agents:

- **agents** are working personas you activate
- **skills** are focused instructions and references you load when needed

For most users, `cortex skills` is one of the most important public workflows in
the product: it helps you discover which skills to use, generate a lightweight
skill context file, and teach the system which recommendations actually helped.

## The Main User Flows

There are four common workflows behind `cortex skills`:

1. **discover** what exists
2. **recommend** what to load for the current task
3. **capture context** for the current session
4. **teach the system** with feedback and ratings

If you only remember one pattern, it is this:

```bash
cortex skills recommend
cortex skills context
# use the recommended skills
cortex skills feedback <skill> helpful
```

## How Skills Are Suggested

Cortex surfaces skills in two different ways.

### 1. Prompt-time suggestions

The Claude Code hook in `hooks/skill_auto_suggester.py` looks at:

- your prompt text
- changed files
- file types and directories
- git branch name
- recent commit subjects

It prints a compact suggestion list such as:

```text
Suggested skills: agent-loops, documentation-production
```

This is the low-latency, deterministic path.

### 2. Structured skill recommendations

The richer recommender behind `cortex skills recommend` and watch mode uses:

- file-pattern rules
- learned history from successful past sessions
- optional semantic similarity
- agent-to-skill mappings when active agents are present in context

In normal CLI usage, file-pattern and historical signals currently do most of
the work.

## Core Workflow

### 1. Discover the catalog

```bash
cortex skills list
cortex skills info documentation-production
cortex skills compose documentation-production
```

Use this path when you already know roughly what you want and need to inspect
the underlying skill, its metadata, or its dependency tree.

### 2. Ask for recommendations

```bash
cortex skills recommend
```

This is the "what should I load right now?" command. It uses the richer skill
recommender rather than only prompt keywords.

### 3. Generate a session context file

```bash
cortex skills context
cortex skills context --no-write
```

`cortex skills context` is especially useful when you want to hand the current
task to another session, sub-agent, or external LLM with a compact recommended
skill bundle. By default it writes `.claude/skill-context.md`; `--no-write`
prints the result to stdout instead.

### 4. Record whether the recommendation helped

```bash
cortex skills feedback documentation-production helpful
cortex skills feedback documentation-production not-helpful
cortex skills feedback documentation-production helpful \
  --comment "Useful for restructuring a stale docs tree"
```

This is recommendation-level feedback: did the suggested skill help for this
task?

### 5. Rate the skill itself

```bash
cortex skills rate documentation-production --stars 5 --review "Helpful for restructuring docs"
cortex skills rate documentation-production --stars 2 --failed --review "Too broad for a small edit"
```

This is broader than recommendation feedback. Ratings capture overall skill
quality, not just whether one recommendation was timely.

## Core Commands

### Discover skills

```bash
cortex skills list
cortex skills info documentation-production
cortex skills validate --all
cortex skills analyze "Need help debugging a flaky API test"
```

### Ask for recommendations

```bash
cortex skills recommend
cortex skills context
```

`cortex skills context` writes a short `.claude/skill-context.md` file for the
current session with the top recommendations.

### Give recommendation feedback

```bash
cortex skills feedback documentation-production helpful
cortex skills feedback documentation-production not-helpful
```

This teaches the recommendation system whether a suggested skill was actually
useful.

### Rate a skill

```bash
cortex skills rate documentation-production --stars 5 --review "Helpful for restructuring docs"
```

Ratings are broader quality signals than recommendation feedback.

### Inspect ratings

```bash
cortex skills ratings documentation-production
cortex skills top-rated --limit 10
cortex skills export-ratings --format json
cortex skills export-ratings --format csv
```

### Audit or community workflows

```bash
cortex skills audit documentation-production --quick
cortex skills community list
cortex skills community search documentation
```

## TUI Workflow

Launch the TUI:

```bash
cortex tui
```

Useful keys:

- `4` opens the Skills view
- `0` opens the AI Assistant
- `Ctrl+R` rates the selected skill from the Skills view

The AI Assistant focuses on **agent** recommendations. The Skills view is where
you browse and rate the skill catalog.

## Feedback vs Ratings

This distinction is important:

- `skills feedback` answers: "Was this recommendation useful for this task?"
- `skills rate` answers: "How good is this skill overall?"

Use feedback when you are teaching the recommender. Use ratings when you are
building long-term quality signal around the skill library.

## Where Skill Data Lives

Recommendation data:

- `~/.claude/data/skill-recommendations.db`
- `~/.claude/skills/recommendation-rules.json`
- `~/.claude/skills/skill-rules.json`

Ratings data:

- `~/.claude/data/skill-ratings.db`

The repository ships the default rules in:

- `skills/recommendation-rules.json`
- `skills/skill-rules.json`

## When To Use Which Path

### Use `cortex skills recommend` when:

- you want a quick shortlist for the current repo changes
- you are working from the terminal
- you want a session context file via `cortex skills context`
- you want a recommendation flow separate from agent activation

### Use the prompt hook when:

- you want instant suggestions inside Claude Code
- prompt wording is part of the signal
- you want the lowest-latency path

### Use ratings when:

- you want to record long-term skill quality
- you want to compare top-rated skills
- you want richer reviews than helpful / not-helpful feedback

### Use `skills context` when:

- you want a compact handoff file for another session
- you want to provide skill context to a sub-agent
- you want to consult another LLM with the currently relevant skills

## Skill Authoring Basics

Each skill lives in its own directory under `skills/` and starts with
`SKILL.md`.

Minimum frontmatter:

```yaml
---
name: documentation-production
description: Use when generating, updating, or organizing documentation.
---
```

Validation:

```bash
cortex skills validate documentation-production
```

## Important Distinction

The recommendation system has two halves:

- `cortex ai ...` is for **agent** intelligence
- `cortex skills ...` plus the hook/watch pipeline are for **skill**
  recommendations

If you are looking for agent auto-activation and watch-mode behavior, see
[AI Intelligence](ai-intelligence.md).

## Related

- [Export Context]({% link guides/export.md %}) -- package skill context for other sessions or models
- [Multi-LLM Consult]({% link guides/llm-consult.md %}) -- combine skills with external model consultation
- [Agent Activation]({% link guides/agent-activation.md %}) -- separate agent workflow
