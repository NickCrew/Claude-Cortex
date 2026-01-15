---
layout: default
title: Worktree Manager
nav_order: 8
---

# Worktree Manager

Cortex includes a Git worktree manager in both the CLI and TUI. It supports listing, adding, pruning, and removing worktrees with a configurable base directory.

## CLI Commands

```bash
# List worktrees and base directory
cortex worktree list

# Add a new worktree
cortex worktree add my-branch --path ../worktrees/my-branch

# Remove a worktree (path or branch)
cortex worktree remove my-branch

# Prune stale worktrees
cortex worktree prune --dry-run

# Set or clear the base directory (stored in git config)
cortex worktree dir ../worktrees
cortex worktree dir --clear
```

### Base Directory Behavior

The worktree base directory is resolved in this order:

1. `cortex.worktreeDir` (git config)
2. `.worktrees/` in the repo root
3. `worktrees/` in the repo root

## TUI View

```bash
cortex tui
# Press 'C' for Worktrees
```

### TUI Keybindings

| Key | Action |
| --- | --- |
| `Ctrl+N` | Add new worktree |
| `Ctrl+O` | Open selected worktree |
| `Ctrl+W` | Remove selected worktree |
| `Ctrl+K` | Prune stale worktrees |
| `B` | Set base directory (use `-` to clear) |

---

**Related guides**: [Asset Manager](asset-manager.html) • [Modes](modes.html) • [TUI Keyboard Reference](tui/tui-keyboard-reference.html)
