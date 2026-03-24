---
layout: default
title: AI Intelligence
parent: Guides
nav_order: 3
---

# AI Intelligence

Cortex ships two related recommendation systems:

1. **Agent intelligence** powers `cortex ai ...`
2. **Skill recommendations** power `cortex skills recommend`, the Claude Code
   hook, and watch-mode skill suggestions

This page focuses on the **agent** side: which agents Cortex thinks you should
activate for the work in front of you.

## What Agent Intelligence Does

Agent intelligence answers:

> Given the files I am changing right now, which agents should I activate?

It works from the current git-backed session context, including:

- changed files and file extensions
- path signals such as `auth`, `schema`, `routes`, and `tests`
- test-failure and issue signals
- previously successful sessions

Recommendations include:

- agent name
- confidence score
- reason
- urgency
- whether the recommendation qualifies for auto-activation

## Core Commands

### Inspect recommendations

```bash
cortex ai recommend
```

This analyzes the current git diff, prints recommended agents, and shows a
workflow prediction when enough history exists.

### Auto-activate high-confidence agents

```bash
cortex ai auto-activate
```

This activates agents whose recommendation is marked for auto-activation.

### Run watch mode

```bash
# Foreground
cortex ai watch

# Background daemon
cortex ai watch --daemon

# Inspect / stop the daemon
cortex ai watch --status
cortex ai watch --stop
```

Useful watch flags:

```bash
cortex ai watch --no-auto-activate
cortex ai watch --threshold 0.8
cortex ai watch --interval 5
cortex ai watch --dir ~/project-a --dir ~/project-b
```

## How Recommendations Are Produced

The current agent recommender combines three strategies:

1. **Semantic similarity** when the optional embedding dependency is available
2. **Pattern matching from successful history**
3. **Rule-based heuristics**

Common rule-based triggers include:

| Signal | Agent |
|:---|:---|
| Auth-related files | `security-auditor` |
| Test failures | `test-automator` |
| Any non-empty changeset | `code-reviewer` |
| Python files | `python-pro` |
| TypeScript files | `typescript-pro` |
| React/UI signals | `react-specialist` |
| Database-heavy changes | `database-optimizer` |

## Watch Mode

Watch mode is where many users first see the system working live. It monitors
git-backed changes and prints:

- detected context
- high-confidence **agent recommendations**
- suggested **skills** from the skill matcher and optional richer recommender

By default, direct `cortex ai watch` runs use:

- auto-activation: `true`
- threshold: `0.7`
- interval: `2.0`

You can override those defaults in `~/.cortex/cortex-config.json`:

```json
{
  "watch": {
    "directories": ["~/projects/my-app"],
    "auto_activate": true,
    "threshold": 0.7,
    "interval": 2.0
  }
}
```

## TUI Integration

Launch the TUI:

```bash
cortex tui
```

Then:

- press `0` for the AI Assistant view
- press `A` to auto-activate recommended agents
- press `r` to refresh recommendations

The AI Assistant is focused on **agent** recommendations. The Skills view is
where you browse and rate skills separately.

## Teaching The System

Record a successful session:

```bash
cortex ai record-success --outcome "feature complete"
```

This primarily improves future **agent** recommendations.

If you use structured specialist reviews, you can also feed them into skill
learning:

```bash
cortex ai ingest-review path/to/review.md
```

## Important Distinction

Do not use these terms interchangeably:

- **agent recommendations** decide which agents to activate
- **skill recommendations** suggest which reusable knowledge packs to load

For the skill side, see the [Skills](skills.md) guide.
