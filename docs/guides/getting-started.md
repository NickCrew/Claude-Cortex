---
layout: default
title: Getting Started
nav_order: 2
---

# Getting Started

Cortex packages curated Claude Code assets (agents, skills, rules, hooks) and a Python CLI (`cortex`) for managing them.

## What’s in this repository

- `commands/` - command markdown assets
- `agents/` - active agent definitions
- `skills/` - reusable skill packs
- `rules/` - rule modules
- `hooks/` - hook scripts and config
- `claude_ctx_py/` - CLI implementation
- `schemas/` - JSON/YAML schemas
- `docs/` - guides and reference docs

## Install

### 1) Install plugin assets in Claude Code

```bash
claude install github:NickCrew/claude-cortex
```

### 2) Install the CLI (optional, recommended)

```bash
# pipx
pipx install claude-cortex

# or pip
pip install claude-cortex
```

## Local development setup

```bash
git clone https://github.com/NickCrew/claude-cortex.git
cd claude-cortex
pip install -e ".[dev]"

# Link repo assets into ~/.claude
cortex install link

# Optional post-install helpers (completions + manpages)
cortex install post
```

## Verify your setup

```bash
cortex --help
cortex status
cortex agent list
cortex skills list
```

## First useful commands

```bash
# AI recommendations
cortex ai recommend

# MCP inventory/diagnostics
cortex mcp list
cortex mcp diagnose

# Worktree support
cortex worktree list

# Interactive UI
cortex tui
```

## Scope and root controls

The CLI has two important selectors:

- `--scope {auto,project,global}` chooses which `.claude/` directory is used for user state/config.
- `--cortex-root` (alias: `--plugin-root`) points Cortex to a specific asset root.

Examples:

```bash
# Use project-local .claude if present
cortex --scope project status

# Force a specific asset root
cortex --cortex-root /path/to/claude-cortex status
```

## Shell completions

```bash
# Auto-detect shell
cortex install completions

# Explicit shell
cortex install completions --shell zsh
```

For options and paths, run `cortex install completions --help`.

## Development notes

- Run `just test`, `just lint`, and `just type-check` before shipping docs or code changes.
- Use `cortex dev validate` to validate the skill registry and `cortex dev manpages` when CLI docs need regenerated.
