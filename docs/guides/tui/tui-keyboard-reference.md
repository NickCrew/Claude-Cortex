---
layout: default
title: TUI Keyboard Reference
---

# TUI Keyboard Reference

Quick reference for cortex TUI navigation and commands.

## View Navigation

### Primary Views

| Key | View | Description |
| --- | --- | --- |
| `1` | Overview | Summary dashboard of all systems |
| `2` | Agents | List and manage agents |
| `3` | Rules | Manage rule modules |
| `4` | Skills | Skill management and community |
| `C` | Worktrees | Git worktree management |
| `5` | Tasks | Task tracking |
| `6` | Commands | Slash command catalog |
| `7` | MCP Servers | Validate/test MCP configs |
| `E` | Export | Context export controls |
| `0` | AI Assistant | Recommendations & predictions |

### Additional Views

| Key | View | Description |
| --- | --- | --- |
| `w` | Watch Mode | Real-time context monitoring |
| `A` | Asset Manager | Install/diff/update assets |
| `M` | Memory Vault | Persistent notes |
| `X` | Codex Skills | Browse Codex skill library |

## Global Navigation

| Key | Action | Description |
| --- | --- | --- |
| `↑` / `k` | Up | Move selection up |
| `↓` / `j` | Down | Move selection down |
| `gg` | Top | Jump to top |
| `G` | Bottom | Jump to bottom |
| `Ctrl+U` | Half Page Up | Scroll up half a page |
| `Ctrl+D` | Half Page Down | Scroll down half a page |
| `Ctrl+B` | Page Up | Scroll up one page |
| `Ctrl+F` | Page Down | Scroll down one page |

## Global Actions

| Key | Action | Description |
| --- | --- | --- |
| `?` | Help | Toggle help overlay |
| `r` | Refresh | Refresh current view |
| `q` | Quit | Exit TUI |
| `Ctrl+P` | Command Palette | Fuzzy search actions |
| `Space` | Toggle | Toggle selected item (where supported) |
| `Ctrl+E` | Edit | Open current item in editor |

## View-Specific Actions

### Agents View
| Key | Action | Description |
| --- | --- | --- |
| `Enter` | View | Show agent definition |
| `Space` | Toggle | Activate/deactivate agent |
| `s` | Details | Show agent details |
| `v` | Validate | Validate agent |

### Rules View
| Key | Action | Description |
| --- | --- | --- |
| `Space` | Toggle | Activate/deactivate rule |
| `Ctrl+E` | Edit | Edit rule file |

### Skills View
| Key | Action | Description |
| --- | --- | --- |
| `s` | Details | Show skill details |
| `v` | Validate | Run skill validation |
| `m` | Metrics | Show skill metrics |
| `d` | Docs | View skill docs |
| `c` | Actions | Skill actions menu |

### Worktrees View
| Key | Action |
| --- | --- |
| `Ctrl+N` | Add new worktree |
| `Ctrl+O` | Open selected worktree |
| `Ctrl+W` | Remove selected worktree |
| `Ctrl+K` | Prune stale worktrees |
| `B` | Set base directory |

### Asset Manager View
| Key | Action |
| --- | --- |
| `i` | Install selected asset |
| `u` | Uninstall selected asset |
| `d` | View diff |
| `U` | Update all outdated |
| `I` | Bulk install by category |
| `T` | Change target directory |
| `Enter` | Show asset details |

**Dialog Shortcuts:**
- **Bulk Install:** `i` or `Enter` to Install All
- **Asset Details:** `i` Install/Update, `u` Uninstall, `d` Diff


### MCP View
| Key | Action |
| --- | --- |
| `B` | Browse & install registry |
| `Ctrl+A` | Add new MCP server |
| `E` | Edit selected server |
| `X` | Remove selected server |
| `s` | Show details |
| `d` | View docs |
| `v` | Validate server |
| `Ctrl+T` | Test server |
| `D` | Diagnose all |

### Export View
| Key | Action |
| --- | --- |
| `Space` | Toggle export category |
| `f` | Cycle export format |
| `e` | Execute export |
| `x` | Copy to clipboard |

### AI Assistant View
| Key | Action |
| --- | --- |
| `a` | Auto-activate recommendations |
| `J` | Consult Gemini |
| `K` | Assign LLM tasks |
| `Y` | Request review tasks |

### Memory Vault View
| Key | Action |
| --- | --- |
| `Enter` | View note |
| `O` | Open note in editor |
| `D` | Delete note |

---

**Related guides**: [TUI Guide](../tui.html) • [Asset Manager](../asset-manager.html) • [Worktree Manager](../worktrees.html)
