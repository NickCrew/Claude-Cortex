---
layout: default
title: TUI Navigation Summary
---

# TUI Navigation Summary

This page summarizes how to move through the cortex TUI and where each major system lives.

## Primary Views (1–9, 0)

```
1  Overview    2  Agents     3  Modes      4  Rules
5  Skills      6  Workflows  7  MCP        8  Profiles
9  Export      0  AI Assistant
```

## Additional Views (Hotkeys)

```
A  Asset Manager     C  Worktrees     F  Flags     M  Memory Vault
p  Principles        w  Watch Mode    S  Scenarios     o  Orchestrate
Alt+g  Agent Galaxy  t  Tasks         /  Slash Commands
```

## Command Palette

Press `Ctrl+P` to open the command palette. It provides fuzzy search across views and actions (for example, “Assets”, “Worktrees”, “MCP”, “Skills”).

## Global Actions

| Key | Action |
| --- | --- |
| `?` | Help overlay |
| `r` | Refresh current view |
| `q` | Quit |
| `Space` | Toggle selected item (where supported) |
| `Ctrl+E` | Edit current item |

## Navigation

| Key | Action |
| --- | --- |
| `j/k` or `↑/↓` | Move selection |
| `gg` | Jump to top |
| `G` | Jump to bottom |
| `Ctrl+U` / `Ctrl+D` | Half page up/down |
| `Ctrl+B` / `Ctrl+F` | Page up/down |

## View Highlights

| View | Key | Key Actions |
| --- | --- | --- |
| Asset Manager | `A` | `i` install, `u` uninstall, `d` diff, `U` update all, `I` bulk install, `T` target |
| Worktrees | `C` | `Ctrl+N` add, `Ctrl+O` open, `Ctrl+W` remove, `Ctrl+K` prune, `B` base dir |
| Workflows | `6` | `R` run, `s` stop |
| Scenarios | `S` | `P` preview, `R` run, `V` validate, `H` history |
| MCP Servers | `7` | `B` browse, `Ctrl+A` add, `E` edit, `X` remove, `v` validate |
| Export | `9` | `f` format, `e` export, `x` copy |
| Memory Vault | `M` | `Enter` view, `O` open, `D` delete |

## Status Bar

The footer shows the current view, quick hints, and runtime metrics (memory/CPU). It updates automatically.

---

**Related guides**: [TUI Keyboard Reference](tui-keyboard-reference.html) • [Asset Manager](../asset-manager.html) • [Worktree Manager](../worktrees.html)
