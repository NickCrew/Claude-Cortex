---
layout: default
title: TUI Keyboard Reference
---

# TUI Keyboard Reference

Quick reference for claude-ctx TUI navigation and commands.

## View Navigation

### Primary Views

| Key | View | Description |
| --- | --- | --- |
| `1` | Overview | Summary dashboard of all systems |
| `2` | Agents | List and manage agents |
| `3` | Modes | Configure behavioral modes |
| `4` | Rules | Manage rule modules |
| `5` | Skills | Skill management and community |
| `6` | Workflows | Run and resume workflows |
| `7` | MCP Servers | Validate/test MCP configs |
| `8` | Profiles | Manage built-in & saved profiles |
| `9` | Export | Context export controls |
| `0` | AI Assistant | Recommendations & predictions |

### Additional Views

| Key | View | Description |
| --- | --- | --- |
| `A` | Asset Manager | Install/diff/update assets |
| `C` | Worktrees | Git worktree management |
| `F` | Flag Explorer | Toggle flag packs |
| `M` | Memory Vault | Persistent notes |
| `w` | Watch Mode | Real-time monitoring |
| `S` | Scenarios | Scenario orchestration |
| `o` | Orchestrate | Parallel execution view |
| `g` | Agent Galaxy | Dependency graph |
| `t` | Tasks | Task tracking |
| `/` | Slash Commands | Command catalog |

## Global Navigation

| Key | Action | Description |
| --- | --- | --- |
| `↑` / `k` | Up | Move selection up |
| `↓` / `j` | Down | Move selection down |

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

### Modes View
| Key | Action | Description |
| --- | --- | --- |
| `Space` | Toggle | Activate/deactivate mode |
| `Ctrl+E` | Edit | Edit mode file |

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

### Workflows View
| Key | Action | Description |
| --- | --- | --- |
| `R` | Run | Run selected workflow |
| `s` | Stop | Stop active workflow |

### Worktrees View
| Key | Action |
| --- | --- |
| `Ctrl+N` | Add new worktree |
| `Ctrl+O` | Open selected worktree |
| `Ctrl+W` | Remove selected worktree |
| `Ctrl+K` | Prune stale worktrees |
| `Ctrl+B` | Set base directory |

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
| `Ctrl+D` | Diagnose all |

### Profiles View
| Key | Action |
| --- | --- |
| `Enter` | View/Edit profile |
| `Space` | Apply profile |
| `n` | Save new profile |
| `D` | Delete profile |

### Export View
| Key | Action |
| --- | --- |
| `Space` | Toggle export category |
| `f` | Cycle export format |
| `e` | Execute export |
| `x` | Copy to clipboard |

### Memory Vault View
| Key | Action |
| --- | --- |
| `Enter` | View note |
| `O` | Open note in editor |
| `D` | Delete note |

### Scenarios View
| Key | Action |
| --- | --- |
| `P` | Preview scenario |
| `R` | Run scenario |
| `V` | Validate scenario |
| `H` | Status/history |

---

**Related guides**: [TUI Guide](../tui.html) • [Asset Manager](../asset-manager.html) • [Worktree Manager](../worktrees.html)
