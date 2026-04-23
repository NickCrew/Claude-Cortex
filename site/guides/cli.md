---
layout: default
title: CLI Usage
parent: Guides
nav_order: 1
---

# CLI Usage

The `cortex` command-line interface provides management and inspection tools for
the installed Cortex environment.

## Core Entry Points

```bash
cortex --help
cortex status
cortex tui
cortex suggest --review --dry-run
```

Use `cortex <group> --help` to inspect a command group before relying on older
examples from historical docs.

## Agent Management

```bash
cortex agent list              # List all agents
cortex agent status            # Show active agents
cortex agent activate <name>   # Activate an agent
cortex agent deactivate <name> # Deactivate an agent
cortex agent graph             # Display dependency graph
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
cortex suggest            # Get AI recommendations
cortex suggest --activate        # Auto-activate high-confidence agents
cortex suggest --watch                # Start real-time monitoring
cortex suggest --watch --daemon       # Run watch mode in background
cortex suggest --record-success --outcome "feature complete"
cortex suggest --export --output recommendations.json
```

## Skills

```bash
cortex skills list                   # List available skills
cortex skills info agent-loops       # Show skill details
cortex skills recommend              # Get skill recommendations
cortex skills context                # Build skill context for a session
cortex skills rate <name> --stars 5  # Rate a skill
cortex skills ratings <name>         # View ratings
cortex skills top-rated              # See top-rated skills
```

## Hooks

```bash
cortex hooks validate          # Validate hooks configuration
```

## Install And Link

```bash
cortex install link            # Link assets into ~/.claude
cortex install link --dry-run  # Preview the link plan
cortex install post            # Install optional extras such as manpages
```

`cortex install link` also generates slash-command aliases from the installed
skill library.

## Practical Reference

```bash
cortex docs                    # Browse bundled docs
cortex suggest --review --context debug  # Run review gate with extra context
```

For slash commands specifically, treat `skills/` as the source of truth and
the installed `commands/` directory as a generated surface.
