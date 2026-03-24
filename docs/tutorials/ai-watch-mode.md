---
layout: default
title: AI Watch Mode
parent: Tutorials
nav_order: 3
permalink: /tutorials/ai-watch-mode/
---

# AI Watch Mode Tutorial

Watch mode is the fastest way to see Cortex's recommendation systems working
live. It monitors git-backed file changes, then prints:

- **agent recommendations** from the AI intelligence subsystem
- **skill suggestions** from the skill matcher plus optional recommender

## What You'll Learn

- run watch mode in the foreground and background
- tune notification thresholds and polling intervals
- understand the difference between agent recommendations and skill suggestions
- use the TUI AI Assistant alongside watch mode

## Prerequisites

- Cortex installed and linked
- a git repository with some staged or unstaged changes

## 1. Start Watch Mode

### Foreground mode

```bash
cortex ai watch
```

By default, this:

- watches the current directory
- polls every 2 seconds
- shows notifications for recommendations at `0.7` confidence or above
- auto-activates agents unless disabled

You should see a banner like:

```text
AI WATCH MODE - Real-time Intelligence
  Auto-activate: ON
  Threshold: 70% confidence
  Check interval: 2.0s
```

### Safer first run

If you want to observe without auto-activation:

```bash
cortex ai watch --no-auto-activate
```

## 2. Understand The Output

When watch mode detects changed files, it prints a context summary first:

```text
[10:33:12] Context detected: Backend, Tests, Auth
  3 files changed
```

Then it prints high-confidence **agent recommendations**:

```text
  Agent Recommendations:

     🔴 security-auditor [AUTO]
        90% - Auth code detected - security review recommended

     🔵 python-pro [AUTO]
        85% - Python changes detected - review recommended
```

And, when available, it prints **skill suggestions**:

```text
  Suggested skills: secure-coding-practices, python-testing-patterns
```

The important distinction:

- agent recommendations answer "which agents should I activate?"
- skill suggestions answer "which knowledge packs would help on this task?"

## 3. Tune Watch Mode

### Change the notification threshold

```bash
cortex ai watch --threshold 0.8
```

Use a higher threshold when you want fewer, stronger notifications.

### Slow the polling interval

```bash
cortex ai watch --interval 5
```

Useful when working in a large repo or when you want less terminal churn.

### Watch multiple directories

```bash
cortex ai watch --dir ~/project-a --dir ~/project-b
```

You can also repeat `--dir` or pass comma-separated values.

## 4. Run As A Daemon

### Start background watch mode

```bash
cortex ai watch --daemon --no-auto-activate
```

### Check status

```bash
cortex ai watch --status
```

### Stop it

```bash
cortex ai watch --stop
```

### Custom log path

```bash
cortex ai watch --daemon --log ~/.cortex/logs/my-watch.log
```

## 5. Configure Defaults

Watch mode reads defaults from `~/.cortex/cortex-config.json`:

```json
{
  "watch": {
    "directories": ["~/projects/my-app"],
    "auto_activate": false,
    "threshold": 0.75,
    "interval": 3.0
  }
}
```

CLI flags override config values for the current run.

## 6. Use The TUI Alongside Watch Mode

Launch the TUI:

```bash
cortex tui
```

Then:

- press `0` for the AI Assistant
- press `A` to auto-activate recommended agents
- press `r` to refresh recommendations

The TUI may also auto-start the watch daemon in the background. That gives you
live recommendations even when you primarily work through the interface.

## 7. Teach The System

When a session goes well, record it:

```bash
cortex ai record-success --outcome "auth flow shipped"
```

This improves future agent recommendations and makes a best-effort contribution
to the skill-learning pipeline.

If you use specialist reviews, you can also feed them back into skill learning:

```bash
cortex ai ingest-review .agents/reviews/review-2026-03-23.md
```

## Troubleshooting

### "No recommendations"

Watch mode only reacts when git-backed changes are present. Make sure you have:

- staged files
- unstaged changes
- or a repo state with changed files relative to `HEAD`

### Too much noise

Try one or more of:

- `--threshold 0.8`
- `--interval 5`
- `--no-auto-activate`

### Skills are missing but agents show up

That usually means Layer 1 keyword matching had little to work with, or the
richer `SkillRecommender` path did not contribute for this context. Agent and
skill recommendations are related but separate subsystems.

## Next Steps

- Read [AI Intelligence Features](../AI_INTELLIGENCE.md)
- Read [Skill Recommendation Engine](../architecture/skill-recommendation-engine.md)
- Explore the [Skills Guide](../guides/skills.md)
