---
layout: default
title: Onboarding Path
parent: Learning Paths
grand_parent: Tutorials
nav_order: 1
permalink: /tutorials/learning-paths/onboarding/
---

# Onboarding: Zero to Productive with Cortex

A focused path from installation to daily use. Each stage builds on the last and includes checkpoints so you know when you're ready to move on.

| Stage | What you'll do | Time |
|-------|---------------|------|
| [1. Install & Verify](#stage-1-install--verify) | Get cortex running | ~5 min |
| [2. Orient Yourself](#stage-2-orient-yourself) | Launch TUI, learn navigation | ~10 min |
| [3. Core Loop](#stage-3-core-loop) | Agents, skills, modes — the daily toolkit | ~15 min |
| [4. Your First Review Loop](#stage-4-your-first-review-loop) | Run a quality gate pass end to end | ~10 min |
| [5. What's Next](#stage-5-whats-next) | Pick your path forward | — |

**Prerequisites:** Python 3.9+, basic terminal familiarity, Claude Code installed.

---

## Stage 1: Install & Verify

### Steps

```bash
# Clone and install
git clone https://github.com/NickCrew/claude-cortex.git
cd claude-cortex
python3 -m pip install -e .

# Finish setup (completions, man pages)
cortex install post

```

### Checkpoint

Verify your installation by running these commands and confirming they produce output:

```bash
cortex --help         # prints command help
cortex status         # shows agent/skill/mode counts
cortex agent list     # lists available agents
```

If all three work, you're ready for Stage 2.

---

## Stage 2: Orient Yourself

### Launch the TUI

```bash
cortex tui
```

The TUI is an interactive dashboard with multiple views. Each view focuses on a different part of cortex.

### Navigation basics

| Key | Action |
|-----|--------|
| `Tab` / `Shift+Tab` | Cycle between views |
| `↑` `↓` | Move within a list |
| `Enter` | Select / expand |
| `/` | Filter / search |
| `?` | Help overlay |
| `q` | Quit |

Spend a minute cycling through views with `Tab`. You'll see panels for agents, skills, modes, workflows, and more. Don't activate anything yet — just get the lay of the land.

### CLI alternative

Everything in the TUI has a CLI equivalent. If you prefer the terminal:

```bash
cortex agent list          # agents view
cortex skills list         # skills view
cortex status              # overall status
```

### Checkpoint

- [ ] You can launch and quit the TUI
- [ ] You've cycled through at least 4 views
- [ ] You can filter a list with `/`

---

## Stage 3: Core Loop

This is the daily toolkit: **agents**, **skills**, and **modes**.

### Agents — specialized AI personas

Agents are focused AI personas (29 available). Each has a defined responsibility, model assignment, and optional dependencies.

**Try it:**

```bash
# See what's available
cortex agent list

# Inspect an agent
cortex agent deps code-reviewer

# Activate one
cortex agent activate code-reviewer
```

In the TUI, navigate to the Agents view, highlight an agent, and press `Enter` to toggle it.

### Skills — on-demand knowledge packs

Skills are modular knowledge packages (100+). They load progressively to save tokens — metadata first, full instructions only when activated.

```bash
# Browse skills
cortex skills list

# Get details on a skill
cortex skills info python-testing-patterns
```

Skills activate automatically via triggers (file patterns, keywords) or manually with `/ctx:<skill-name>` in Claude Code.

### Modes — behavioral presets

Modes shape how Claude behaves: verbosity, safety checks, focus areas.

```bash
# Inspect active mode state
cat ~/.claude/.active-modes
```

Common modes:
- **architect** — system design focus, longer reasoning
- **security-audit** — security-first analysis
- **token-efficiency** — compressed output, minimal overhead

### Profiles — saved configurations

Use install/scope commands to manage local setup:

```bash
# Ensure assets are linked
cortex install link

# Inspect project vs global scope
cortex --scope project status
cortex --scope global status
```

### Checkpoint

- [ ] You've activated and deactivated an agent
- [ ] You've inspected a skill with `cortex skills info`
- [ ] You know where active mode state is stored (`.active-modes`)
- [ ] You understand the difference: agents = who, skills = what they know, modes = how they behave

---

## Stage 4: Your First Review Loop

Use the review gate to run a quick quality check pass.

```bash
# Dry-run reviewer selection
cortex review --dry-run
```

Then run targeted commands based on your context (for example `cortex agent activate code-reviewer` and `cortex skills info testing-anti-patterns`).

### Export a context bundle

Context bundles package your current configuration (active agents, modes, skills) for sharing or backup:

```bash
cortex export context my-setup.md
```

### Checkpoint

- [ ] You've run the review gate
- [ ] You've exported a context bundle
- [ ] You can explain what a workflow does vs. activating agents individually

---

## Stage 5: What's Next

You now have a working cortex setup and understand the core loop. Pick a path based on what you need:

### Deepen your TUI skills

The full TUI tutorial covers every view, shortcut, and feature in detail.

**[Getting Started with TUI](../getting-started-tui/)** — 20-30 min, 15+ checkpoints

### Automate with CI/CD

Learn to run validation, exports, and quality gates in pipelines.

**[CI/CD Integration](../ci-cd-integration/)** — 20-25 min

### Create your own skills

Package domain knowledge into reusable skill packs.

**[Skill Authoring Cookbook](../skill-authoring-cookbook/)** — 30-45 min

### Set up AI Watch Mode

Enable real-time intelligent recommendations as you work.

**[AI Watch Mode](../ai-watch-mode/)** — ~15 min

### Integrate with CI/CD

Automate cortex in your deployment pipelines.

**[CI/CD Integration](../ci-cd-integration/)** — ~20 min

### Reference material

- [Command Reference](../../guides/commands/) — all 49 slash commands
- [Skills Guide](../../guides/skills/) — progressive disclosure deep dive
- [Architecture](../../guides/development/architecture/) — system design and internals
- `man cortex` — offline CLI reference

---

## Quick Reference Card

Commands you'll use daily:

```bash
# Status
cortex status                    # overview

# Agents
cortex agent list                # browse
cortex agent activate <name>     # enable
cortex agent deactivate <name>   # disable

# Skills
cortex skills list               # browse
cortex skills info <name>        # details

# Modes
cat ~/.claude/.active-modes      # inspect active state

# Review loop
cortex review --dry-run          # inspect reviewers

# TUI
cortex tui                       # launch dashboard
```
