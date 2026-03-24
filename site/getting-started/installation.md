---
layout: default
title: Installation
parent: Getting Started
nav_order: 1
---

# Installation

## Option 1: Python Package (Recommended)

Install the Python package using your preferred tool:

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

## Option 2: Development Install

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
└── commands/  → generated aliases derived from installed skills
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
