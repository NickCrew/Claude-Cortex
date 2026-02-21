---
layout: default
title: Home
nav_order: 1
permalink: /
---

# Cortex Documentation
{: .fs-9 }

Context orchestration toolkit for Claude Code. Agents, skills, rules, and hooks with an optional Python CLI.
{: .fs-6 .fw-300 }

[Get Started]({% link getting-started/index.md %}){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }
[View on GitHub](https://github.com/NickCrew/claude-cortex){: .btn .fs-5 .mb-4 .mb-md-0 }

---

## What is Cortex?

Cortex bundles a curated stack of **agents**, **skills**, **rules**, **hooks**, and **behavioral modes** for [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Install it as a plugin or pair it with the Python CLI for advanced management through a terminal UI.

### At a Glance

| Component | Count | Purpose |
|:----------|:------|:--------|
| Agents | 29 | Specialized subagents (code review, security, architecture, etc.) |
| Skills | 100+ | Reusable skill modules with activation triggers |
| Commands | 49 | Slash commands across 13 categories |
| Modes | 9 | Behavioral presets (Architect, Brainstorming, Security Audit, etc.) |
| Flags | 22 | Token-efficient context modules |

### Key Features

- **Plugin Install** -- `claude install github:NickCrew/claude-cortex` and go
- **AI Intelligence** -- context-aware agent recommendations with auto-activation
- **Watch Mode** -- real-time file monitoring with instant recommendations
- **Terminal UI** -- full management interface (`cortex tui`)
- **Skill Ratings** -- rate, review, and discover skills with quality metrics
- **Asset Manager** -- install, diff, and update plugin assets from the TUI
- **Worktree Manager** -- git worktree workflows from CLI or TUI

---

## Quick Install

```bash
# Plugin install (recommended)
claude install github:NickCrew/claude-cortex

# With Python CLI for TUI and management features
pip install claude-cortex
```

See [Installation]({% link getting-started/installation.md %}) for detailed options.

---

## Where to Start

- **New to Cortex?** Start with the [Quick Start]({% link getting-started/quick-start.md %}) guide
- **Want the TUI?** See the [TUI Guide]({% link guides/tui.md %})
- **Looking for commands?** Check the [Command Reference]({% link reference/commands.md %})
- **Configuring your setup?** Read [Configuration]({% link getting-started/configuration.md %})
