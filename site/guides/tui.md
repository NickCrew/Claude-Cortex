---
layout: default
title: Terminal UI
parent: Guides
nav_order: 2
---

# Terminal UI

The Cortex TUI is a full-featured terminal interface built with
[Textual](https://textual.textualize.io/) for managing agents, rules, skills,
hooks, watch mode, and related Cortex assets.

## Launching

```bash
cortex tui
```

## Navigation

### View Switching

| Key | View |
|:----|:-----|
| `0` | AI Assistant |
| `1` | Overview |
| `2` | Agents |
| `3` | Rules |
| `4` | Skills |
| `5` | LLM Skills |
| `6` | Commands |
| `7` | Hooks |
| `8` | Memory |
| `9` | Watch Mode |
| `M` | MCP Servers |
| `E` | Export |
| `T` | Tasks |
| `W` | Worktrees |
| `A` | Asset Manager |
| `F` | Settings |

### Global Shortcuts

| Key | Action |
|:----|:-------|
| `Ctrl+P` | Command Palette |
| `Ctrl+R` | Rate selected skill |
| `Ctrl+E` | Export context |
| `Ctrl+Q` | Quit |
| `?` | Help |

## AI Assistant View

Press `0` to open the AI assistant view. It shows:

- Intelligent recommendations with confidence scores
- Agent suggestions from learned patterns
- Context analysis (files, detected contexts)
- Quick actions via keyboard shortcuts

Press `A` in this view to auto-activate recommended agents.

## Agent Management

Press `2` for the agents view:

- Browse all 29 active agents
- View dependencies and triggers
- Activate/deactivate agents
- See model assignments

## Skills And Commands

The skill system has two complementary views:

- Press `4` for the Skills view.
- Press `6` for the Commands view.

The Commands view is populated from the installed skill library, not from a
separate hand-maintained command catalog. In practice:

- skill metadata comes from `SKILL.md`
- slash commands are derived from skill paths or explicit command frontmatter
- `cortex install link` generates the installed `~/.claude/commands/` aliases

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

Press `W` for worktree management:

| Key | Action |
|:----|:-------|
| `Ctrl+N` | Add worktree |
| `Ctrl+O` | Open worktree |
| `Ctrl+W` | Remove worktree |
| `Ctrl+K` | Prune stale worktrees |
| `B` | Set base directory |

## Command Palette

Press `Ctrl+P` to open the command palette, then type to search:

- `Skill...` -- run skill-oriented actions (info, versions, deps, analytics)
- `Configure LLM Providers` -- set up multi-LLM consult
- Any TUI action by name

## Skill Ratings

In the Skills view (`4`), select a skill and press `Ctrl+R` to open the rating dialog. You can assign 1-5 stars and optionally write a review.
