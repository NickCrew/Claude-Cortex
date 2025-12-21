---
layout: default
title: Worktree Manager
nav_order: 8
---

# Worktree Manager

Claude Cortex includes a Git worktree manager in both the CLI and TUI. It supports listing, adding, pruning, and removing worktrees with a configurable base directory.

## CLI Commands

```bash
# List worktrees and base directory
claude-ctx worktree list

# Add a new worktree
claude-ctx worktree add my-branch --path ../worktrees/my-branch

# Remove a worktree (path or branch)
claude-ctx worktree remove my-branch

# Prune stale worktrees
claude-ctx worktree prune --dry-run

# Set or clear the base directory (stored in git config)
claude-ctx worktree dir ../worktrees
claude-ctx worktree dir --clear
```

### Base Directory Behavior

The worktree base directory is resolved in this order:

1. `claude-ctx.worktreeDir` (git config)
2. `.worktrees/` in the repo root
3. `worktrees/` in the repo root

## TUI View

```bash
claude-ctx tui
# Press 'C' for Worktrees
```

### TUI Keybindings

| Key | Action |
| --- | --- |
| `Ctrl+N` | Add new worktree |
| `Ctrl+O` | Open selected worktree |
| `Ctrl+W` | Remove selected worktree |
| `Ctrl+K` | Prune stale worktrees |
| `Ctrl+B` | Set base directory (use `-` to clear) |

---

**Related guides**: [Asset Manager](asset-manager.html) • [Modes](modes.html) • [TUI Keyboard Reference](tui/tui-keyboard-reference.html)
