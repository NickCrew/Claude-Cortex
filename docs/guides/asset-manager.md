---
layout: default
title: Asset Manager
nav_order: 7
---

# Asset Manager

The Asset Manager lets you install, diff, and update plugin assets directly from the TUI. It keeps your local `.claude` directories aligned with the bundled assets in this repository.

## What It Manages

- Hooks
- Commands
- Agents
- Skills
- Modes
- Workflows
- Flags

## Launch

```bash
cortex tui
# Press 'A' for Asset Manager
```

You can also open it from the command palette (`Ctrl+P`) by typing “Assets”.

## Keybindings

| Key | Action | Notes |
| --- | --- | --- |
| `i` | Install selected asset | Installs into the selected target directory |
| `u` | Uninstall selected asset | Removes the asset from the target |
| `d` | Show diff | Compare installed vs source |
| `U` | Update all | Update all assets that differ |
| `I` | Bulk install | Install by category |
| `T` | Change target | Select a different `.claude` directory |
| `Enter` | Details | View full asset details and actions |

## Status Indicators

- **Installed**: Asset matches the plugin version
- **Differs**: Installed asset differs from source
- **Available**: Not installed yet
- **Unknown**: Target directory not selected

## Target Directories

The Asset Manager scans for `.claude` directories (global and project scopes). Use `T` to switch targets before installing or updating assets.

---

**Related guides**: [Modes](modes.html) • [Worktree Manager](worktrees.html) • [TUI Keyboard Reference](tui/tui-keyboard-reference.html)
