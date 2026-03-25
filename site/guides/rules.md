---
layout: default
title: Rules
parent: Guides
nav_order: 6
---

# Rules

Rules are markdown files that define behavioral constraints for Claude Code. They cover git workflow, code quality, file management, and tool usage. Active rules are symlinked to `~/.claude/rules/cortex/` so Claude loads them automatically.

## Shipped Rules

Cortex includes four core rules:

| Rule | Purpose |
|:-----|:--------|
| `git-rules.md` | Conventional commits, atomic changes, identity/attribution |
| `quality-rules.md` | Naming conventions, code organization, root-cause investigation |
| `files.md` | File deletion safety, `.env` protection, multi-agent coordination |
| `codanna.md` | Use codanna MCP tools for semantic search before grep/find |

## Managing Rules

### List and Status

```bash
# List all available rules with status
cortex rules list

# Show currently active rules
cortex rules status
```

### Activate and Deactivate

```bash
# Activate a rule
cortex rules activate quality-rules

# Deactivate a rule
cortex rules deactivate quality-rules

# Activate multiple at once
cortex rules activate git-rules quality-rules
```

### Edit

```bash
# Open a rule in your $EDITOR
cortex rules edit git-rules
```

## How Symlinks Work

When rules are activated, Cortex creates symlinks from your rules directory into `~/.claude/rules/cortex/`. Claude Code automatically loads any `.md` files it finds in `~/.claude/rules/`.

```
~/.claude/rules/cortex/
├── git-rules.md      → ~/.cortex/rules/git-rules.md
├── quality-rules.md  → ~/.cortex/rules/quality-rules.md
├── files.md          → ~/.cortex/rules/files.md
└── codanna.md        → ~/.cortex/rules/codanna.md
```

The launcher also adds `rules/cortex/` to `~/.claude/.gitignore` so symlinks aren't committed.

## Activation State

Active rules are tracked in `~/.cortex/.active-rules`. This file persists across sessions.

```bash
# View the file directly
cat ~/.cortex/.active-rules
```

## Configuration

Set default rules in `cortex-config.json`:

```json
{
  "rules": ["git-rules", "quality-rules", "files"]
}
```

Rule slugs are filenames without the `.md` extension. If omitted, all rules in the directory are activated.

## Priority System

Rules use a three-tier priority system to signal importance:

| Priority | When |
|:---------|:-----|
| CRITICAL | Security, data safety -- never compromise |
| IMPORTANT | Quality, maintainability -- strong preference |
| RECOMMENDED | Optimization, style -- apply when practical |

## TUI Management

In the TUI (`cortex tui`), rules are managed through view `4`:

1. Press `4` to open the Rules view
2. Browse rules with arrow keys
3. Toggle activation with spacebar
4. Press `r` to refresh

Rules are shown with their status, category, and description.

## Writing Custom Rules

Create a new `.md` file in `~/.cortex/rules/`:

```markdown
# My Custom Rule

## Code Style
- Use 4-space indentation in Python files
- Prefer f-strings over .format()

## Testing
- Every bug fix must include a regression test
- Run the test suite before committing
```

Then activate it:

```bash
cortex rules activate my-custom-rule
```

## Archived Rules

Additional rules are available in `archive/rules/`:

- `parallel-execution-rules.md` -- parallel workstream execution
- `quality-gate-rules.md` -- quality gate enforcement

Move them to `~/.cortex/rules/` to make them available for activation.
