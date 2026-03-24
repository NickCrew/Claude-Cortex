---
layout: default
title: Home
nav_order: 1
permalink: /
---

# Cortex Documentation
{: .fs-9 }

Context orchestration toolkit for Claude Code. Agents, skills, rules, hooks,
and skill-derived slash commands with a Python CLI and terminal UI.
{: .fs-6 .fw-300 }

[Get Started]({% link getting-started/index.md %}){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }
[View on GitHub](https://github.com/NickCrew/claude-cortex){: .btn .fs-5 .mb-4 .mb-md-0 }

<div class="home-hero-image">
  <img src="{{ '/assets/images/cortex-home-hero.svg' | relative_url }}" alt="Cortex hero artwork showing the Cortex wordmark and the tagline Context orchestration for Claude Code, Codex, and Gemini." />
</div>

---

## What is Cortex?

Cortex bundles a curated stack of **agents**, **skills**, **rules**, and **hooks** for [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Install the Python package for full management through the CLI and terminal UI.

### At a Glance

| Component | Count | Purpose |
|:----------|:------|:--------|
| Agents | 29 | Specialized subagents (code review, security, architecture, etc.) |
| Skills | 100+ | Reusable skill modules with activation triggers |
| Commands | Skill-derived | Slash command aliases generated from installed skills |
| Hooks | Included | Automation on Claude Code lifecycle events |

### Key Features

- **Python Package** -- `pip install claude-cortex` and go
- **AI Intelligence** -- context-aware agent recommendations with auto-activation
- **Watch Mode** -- real-time file monitoring with instant recommendations
- **Terminal UI** -- full management interface (`cortex tui`)
- **Skill Ratings** -- rate, review, and discover skills with quality metrics
- **Asset Manager** -- install, diff, and update plugin assets from the TUI
- **Worktree Manager** -- git worktree workflows from CLI or TUI

---

## Quick Install

```bash
# Install the Python package
pipx install claude-cortex

# Link assets into ~/.claude and install shell completions
cortex install link
cortex install post
```

See [Installation]({% link getting-started/installation.md %}) for detailed options.

---

## Where to Start

- **New to Cortex?** Start with the [Quick Start]({% link getting-started/quick-start.md %}) guide
- **Want the TUI?** See the [TUI Guide]({% link guides/tui.md %})
- **Looking for commands?** Check the [Command Reference]({% link reference/commands.md %})
- **Configuring your setup?** Read [Configuration]({% link getting-started/configuration.md %})
