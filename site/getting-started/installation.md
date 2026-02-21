---
layout: default
title: Installation
parent: Getting Started
nav_order: 1
---

# Installation

## Option 1: Claude Plugin (Recommended)

Install directly through Claude Code's plugin system:

```bash
claude install github:NickCrew/claude-cortex
```

This installs agents, skills, rules, and hooks. Rules are automatically symlinked to `~/.claude/rules/cortex/`.

After installation, just run Claude:

```bash
claude
```

## Option 2: With Python CLI

For the terminal UI and management features, add the Python package:

```bash
# Install plugin first
claude install github:NickCrew/claude-cortex

# Then install Python CLI
pip install claude-cortex
```

Or install the CLI standalone:

```bash
# pipx (recommended for CLI tools)
pipx install claude-cortex

# uv
uv tool install claude-cortex

# pip
pip install claude-cortex
```

After installing the CLI, link cortex content and install shell completions:

```bash
# Create symlinks in ~/.claude for agents, skills, rules, hooks
cortex install link

# Install shell completions and manpages
cortex install post
```

## Option 3: Development Install

```bash
git clone https://github.com/NickCrew/claude-cortex.git
cd claude-cortex
pip install -e ".[dev]"

# Link content
cortex install link

# Install shell completions and manpages
cortex install post
```

## What Gets Installed

The `cortex install link` command creates symlinks in `~/.claude/`:

```
~/.claude/
├── agents/    → symlink to package agents/
├── skills/    → symlink to package skills/
├── rules/     → symlink to package rules/
├── hooks/     → symlink to package hooks/
└── commands/  → generated (skill command aliases)
```

{: .note }
Run `cortex install link --dry-run` to preview changes before linking. Use `--force` to replace existing directories.

## Verifying Installation

```bash
# Check CLI version
cortex --version

# View plugin status
cortex status

# List available agents
cortex agent list
```

## Requirements

- **Claude Code** -- latest version
- **Python** -- 3.9+ (for CLI only)
- **Git** -- for worktree features
