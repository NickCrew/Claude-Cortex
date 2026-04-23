---
layout: default
title: Quick Start
parent: Getting Started
nav_order: 2
---

# Quick Start

Get productive with Cortex in 5 minutes.

## 1. Install

```bash
pipx install claude-cortex
cortex install link
```

`cortex install link` links agents, skills, rules, hooks, and generated command
aliases into `~/.claude/`.

## 2. Start Claude Code

```bash
claude
```

Cortex agents, skills, and rules are now loaded automatically.

## 3. Use Slash Commands

Slash commands are derived from installed skills. A few common examples:

```
/ctx:agent-loops                 # Implementation workflow with review gates
/ctx:systematic-debugging        # Structured debugging workflow
/ctx:doc-maintenance             # Documentation audit and refresh workflow
/collaboration:brainstorming     # Collaborative ideation workflow
```

If you want to understand a slash command, inspect the skill that backs it.

## 4. Try the TUI

```bash
cortex tui
```

Key views in the TUI:

| Key | View |
|:----|:-----|
| `0` | AI Assistant |
| `1` | Overview |
| `2` | Agents |
| `4` | Skills |
| `M` | MCP Servers |
| `A` | Asset Manager |
| `W` | Worktrees |

## 5. Try Recommendations

```bash
# Agent recommendations
cortex suggest

# Auto-activate high-confidence agents
cortex suggest --activate

# Skill recommendations
cortex skills recommend
```

## 6. Inspect The CLI Surface

```bash
cortex --help
cortex skills --help
cortex suggest --help
```

## Next Steps

- [Configuration]({% link getting-started/configuration.md %}) -- understand roots, scope, and watch defaults
- [CLI Guide]({% link guides/cli.md %}) -- learn the verified command groups
- [TUI Guide]({% link guides/tui.md %}) -- master the terminal UI
- [Commands]({% link reference/commands.md %}) -- see how slash commands are generated from skills
