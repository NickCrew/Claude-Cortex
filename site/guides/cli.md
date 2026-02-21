---
layout: default
title: CLI Usage
parent: Guides
nav_order: 1
---

# CLI Usage

The `cortex` command-line interface provides management tools outside of Claude Code.

## Starting Claude with Cortex

```bash
# Basic launch
cortex start

# Override modes for this session
cortex start --modes "Architect,Deep_Analysis"

# Override flags for this session
cortex start --flags "security-hardening,testing-quality"

# Pass extra args to Claude (after --)
cortex start -- --model claude-sonnet-4-20250514
```

{: .note }
`cortex claude` is an alias for `cortex start`.

## Agent Management

```bash
cortex agent list              # List all agents
cortex agent list --active     # Show active agents only
cortex agent graph             # Display dependency graph
cortex agent graph --export dependency-map.md
```

## Mode Management

```bash
cortex mode list               # List available modes
cortex mode status             # Show active modes
cortex mode activate Architect # Activate a mode
cortex mode deactivate Architect
```

## Rule Management

```bash
cortex rules list              # List available rules
cortex rules status            # Show active rules
cortex rules activate <name>   # Activate a rule
cortex rules deactivate <name> # Deactivate a rule
cortex rules edit <name>       # Edit a rule file
```

## AI Intelligence

```bash
cortex ai recommend            # Get AI recommendations
cortex ai auto-activate        # Auto-activate high-confidence agents
cortex ai watch                # Start real-time monitoring
cortex ai watch --daemon       # Run watch mode in background
cortex ai record-success --outcome "feature complete"
cortex ai export --output recommendations.json
```

## Init and Profiles

```bash
cortex init detect             # Detect project type
cortex init profile backend    # Apply a profile
cortex init status             # Check init status
```

## Worktrees

```bash
cortex worktree list
cortex worktree add my-branch --path ../worktrees/my-branch
cortex worktree remove my-branch
cortex worktree prune --dry-run
cortex worktree dir ../worktrees   # Set base directory
cortex worktree dir --clear        # Clear base directory
```

## MCP Servers

```bash
cortex mcp list                # List configured servers
cortex mcp show context7       # Show server details
cortex mcp docs serena         # View curated documentation
cortex mcp diagnose            # Diagnose all servers
cortex mcp snippet playwright  # Generate config snippet
```

## Skills

```bash
cortex skills recommend              # Get skill recommendations
cortex skills rate <name> --stars 5  # Rate a skill
cortex skills ratings <name>         # View ratings
cortex skills top-rated              # See top-rated skills
cortex skills export-ratings --format csv
```

## Setup and Migration

```bash
cortex install link            # Create symlinks
cortex install link --dry-run  # Preview changes
cortex install post            # Install completions and manpages
cortex setup migrate           # Migrate activation state
```

## Shell Completions

```bash
cortex completion bash > ~/.bash_completion.d/cortex
cortex completion zsh > ~/.zsh/completions/_cortex
cortex completion fish > ~/.config/fish/completions/cortex.fish
```

## Man Pages

```bash
man cortex                     # Main manual
man cortex-tui                 # TUI manual
man cortex-workflow            # Workflow manual
```
