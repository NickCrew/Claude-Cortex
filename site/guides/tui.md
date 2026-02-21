---
layout: default
title: Terminal UI
parent: Guides
nav_order: 2
---

# Terminal UI

The Cortex TUI is a full-featured terminal interface built with [Textual](https://textual.textualize.io/) for managing agents, skills, modes, flags, and more.

## Launching

```bash
cortex tui
```

## Navigation

### View Switching

| Key | View |
|:----|:-----|
| `1` | Agents |
| `2` | Modes |
| `3` | Workflows |
| `4` | Scenarios |
| `5` | Skills |
| `6` | Memory Vault |
| `7` | MCP Servers |
| `0` | AI Assistant |
| `A` | Asset Manager |
| `C` | Worktrees |

### Global Shortcuts

| Key | Action |
|:----|:-------|
| `Ctrl+P` | Command Palette |
| `Ctrl+G` | Flag Manager |
| `Ctrl+R` | Rate selected skill |
| `Ctrl+E` | Export context |
| `Ctrl+Q` | Quit |
| `?` | Help |

## AI Assistant View

Press `0` to open the AI assistant view. It shows:

- Intelligent recommendations with confidence scores
- Workflow predictions from learned patterns
- Context analysis (files, detected contexts)
- Quick actions via keyboard shortcuts

Press `A` in this view to auto-activate recommended agents.

## Agent Management

Press `1` for the agents view:

- Browse all 29 active agents
- View dependencies and triggers
- Activate/deactivate agents
- See model assignments

## Flag Manager

Press `Ctrl+G` to open the Flag Manager:

```
Status  Flag Category              Tokens
------  -------------------------  ------
 ON     Mode Activation Flags       120
 ON     MCP Server Flags            160
 OFF    Testing Quality Flags       170
...

Controls: Up/Down Select   Space Toggle
```

Changes persist immediately to `FLAGS.md`.

## Asset Manager

Press `A` for the Asset Manager:

| Key | Action |
|:----|:-------|
| `i` | Install asset |
| `u` | Uninstall asset |
| `d` | Diff installed vs source |
| `U` | Update all |
| `I` | Bulk install by category |
| `T` | Set target directory |

## Worktree Manager

Press `C` for worktree management:

| Key | Action |
|:----|:-------|
| `Ctrl+N` | Add worktree |
| `Ctrl+O` | Open worktree |
| `Ctrl+W` | Remove worktree |
| `Ctrl+K` | Prune stale worktrees |
| `B` | Set base directory |

## Command Palette

Press `Ctrl+P` to open the command palette, then type to search:

- `Skill...` -- run skill commands (info, versions, deps, analytics)
- `Configure LLM Providers` -- set up multi-LLM consult
- Any TUI action by name

## Skill Ratings

In the Skills view (`5`), select a skill and press `Ctrl+R` to open the rating dialog. You can assign 1-5 stars and optionally write a review.
