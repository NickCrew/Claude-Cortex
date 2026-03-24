---
layout: default
title: Skills
parent: Guides
nav_order: 4
---

# Skills

Skills are reusable knowledge packs that Cortex can suggest, inspect, and rate.
They are different from agents:

- **agents** are working personas you activate
- **skills** are focused instructions and references you load when needed

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

## Core Commands

### Discover skills

```bash
cortex skills list
cortex skills info documentation-production
cortex skills validate --all
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

### Use the prompt hook when:

- you want instant suggestions inside Claude Code
- prompt wording is part of the signal
- you want the lowest-latency path

### Use ratings when:

- you want to record long-term skill quality
- you want to compare top-rated skills
- you want richer reviews than helpful / not-helpful feedback

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
