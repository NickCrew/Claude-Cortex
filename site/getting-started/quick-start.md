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
claude install github:NickCrew/claude-cortex
```

## 2. Start Claude Code

```bash
claude
```

Cortex agents, skills, and rules are now loaded automatically.

## 3. Use Slash Commands

Cortex provides 49 slash commands organized by category. Try these:

```
/dev:implement     # Implement a feature with quality gates
/dev:code-review   # Review code for quality and security
/analyze:code      # Analyze code structure and patterns
/test:generate     # Generate tests for a module
```

## 4. Add the CLI (Optional)

The Python CLI unlocks the terminal UI, AI recommendations, and management tools:

```bash
pip install claude-cortex
cortex install link
```

### Try the TUI

```bash
cortex tui
```

Key views in the TUI:

| Key | View |
|:----|:-----|
| `1` | Agents |
| `2` | Modes |
| `5` | Skills |
| `7` | MCP Servers |
| `0` | AI Assistant |
| `A` | Asset Manager |
| `C` | Worktrees |

### Get AI Recommendations

```bash
# Analyze your project and get agent recommendations
cortex ai recommend

# Auto-activate high-confidence agents
cortex ai auto-activate

# Start real-time monitoring
cortex ai watch
```

## 5. Customize with Profiles

Apply a profile that matches your workflow:

```bash
# Detect your project type
cortex init detect

# Apply a profile
cortex init profile frontend   # or: backend, devops, quality, minimal
```

Profiles configure which agents, modes, and flags are active for your context.

## Next Steps

- [Configuration]({% link getting-started/configuration.md %}) -- customize flags, modes, and rules
- [CLI Guide]({% link guides/cli.md %}) -- learn all CLI commands
- [TUI Guide]({% link guides/tui.md %}) -- master the terminal UI
