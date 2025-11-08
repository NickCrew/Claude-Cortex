# TUI Keyboard Reference

Quick reference for claude-ctx TUI navigation and commands.

## View Navigation (1-9)

| Key | View         | Description                              |
|-----|--------------|------------------------------------------|
| 1   | Overview     | Summary dashboard of all systems         |
| 2   | Agents       | List and manage agents                   |
| 3   | Modes        | Configure behavioral modes               |
| 4   | Rules        | Manage rule modules                      |
| 5   | Skills       | Skill management and community           |
| 6   | Workflows    | Run and resume workflows                 |
| 7   | MCP Servers  | Validate/test Model Context Protocol     |
| 8   | Profiles     | Manage built-in & saved profiles         |
| 9   | Export       | Context export controls                  |
| 0   | AI Assistant | Recommendations & workflow predictions   |

## Global Navigation

| Key        | Action       | Description                    |
|------------|--------------|--------------------------------|
| ↑ / k      | Move up      | Move selection up one row      |
| ↓ / j      | Move down    | Move selection down one row    |
| PgUp       | Page up      | Jump up one page (reserved)    |
| PgDn       | Page down    | Jump down one page (reserved)  |
| Home       | Jump to top  | Jump to first item (reserved)  |
| End        | Jump to end  | Jump to last item (reserved)   |

## Global Actions

| Key   | Action             | Description                          |
|-------|--------------------|--------------------------------------|
| i     | Init wizard        | Start project initialization wizard  |
| /     | Filter             | Context-aware search/filter          |
| Esc   | Clear/Exit         | Clear filter or exit detail view     |
| ?     | Help               | Toggle help overlay                  |
| r     | Refresh            | Refresh current view                 |
| q     | Quit               | Exit TUI                             |

## View-Specific Actions

### Agents View
| Key    | Action             | Description                     |
|--------|--------------------|---------------------------------|
| Space  | Toggle             | Activate/deactivate agent       |
| Enter  | Details            | Show agent details panel        |
| /      | Filter             | Filter agents by name/category  |

### Modes View
| Key    | Action             | Description                     |
|--------|--------------------|---------------------------------|
| Space  | Toggle             | Activate/deactivate mode        |
| Enter  | Details            | Show mode details panel         |
| /      | Filter             | Filter modes                    |

### Rules View
| Key    | Action             | Description                     |
|--------|--------------------|---------------------------------|
| Space  | Toggle             | Activate/deactivate rule        |
| Enter  | Details            | Show rule details panel         |
| /      | Filter             | Filter rules                    |

### Skills View
| Key    | Action             | Description                     |
|--------|--------------------|---------------------------------|
| v      | Validate           | Run skill validation            |
| m      | Metrics            | Show skill metrics              |
| c      | Community          | Browse community skills         |
| Ctrl+P | Palette Commands   | Type “Skill …” for Info/Versions/Deps/Agents/Compose/Analytics/Report/Trending or Community install/validate/rate/search |

### Workflows View
| Key    | Action             | Description                     |
|--------|--------------------|---------------------------------|
| r      | Run                | Run selected workflow           |
| Space  | Resume             | Resume paused workflow          |
| s      | Stop               | Stop running workflow           |

### Profile View
| Key    | Action             | Description                     |
|--------|--------------------|---------------------------------|
| Space  | Apply              | Apply highlighted profile       |
| n      | Save Snapshot      | Save current state as profile   |
| D      | Delete             | Delete selected saved profile   |

### Export View
| Key    | Action             | Description                     |
|--------|--------------------|---------------------------------|
| Space  | Toggle             | Include/exclude component       |
| f      | Format             | Cycle export format             |
| e      | Export             | Export context to file          |
| x      | Clipboard          | Copy export to clipboard        |

### MCP View
| Key        | Action             | Description                         |
|------------|--------------------|-------------------------------------|
| v          | Validate           | Run config validation               |
| d          | Docs               | View server documentation           |
| c          | Snippet            | Generate config snippet (copies)    |
| s          | Details            | Show full server details            |
| Ctrl+T     | Test               | Run configuration test              |
| Ctrl+D     | Diagnose           | Diagnose all configured servers     |

## Tips and Tricks

### Quick View Switching
- Press number keys (1-9, 0) to instantly switch between views
- View state (selection, filter) is preserved when switching away
- Press 1 to return to overview dashboard at any time
- Use `o` for Orchestrate, `g` for Galaxy, and `t` for Tasks

### Filtering
- Press `/` to start filtering in most views
- Type filter text (case-insensitive)
- Press Enter to apply, Esc to cancel
- Filter applies to name, category, and other relevant fields

### Help System
- Press `?` to show comprehensive help overlay
- Help works from any view
- Shows all available keyboard shortcuts
- Press `?` again or Esc to close

### Details Panel
- Press Enter to show details for selected item
- Details panel splits screen with list view
- Press Esc to close details panel
- Press Enter again to toggle details on/off

### Status Bar
- Bottom status bar shows context-aware hints
- Current view indicator: `[View: Agents]`
- View-specific quick reference
- Active filter indicator
- Connection status

## Common Workflows

### Activating an Agent
1. Press `2` to go to Agents view
2. Use ↑/↓ or j/k to select agent
3. Press Space to toggle active/inactive
4. Status updates automatically

### Finding a Specific Agent
1. Press `2` to go to Agents view
2. Press `/` to start filter
3. Type part of agent name
4. Press Enter to apply filter
5. Press Esc to clear filter

### Viewing Agent Details
1. Select agent with ↑/↓ or j/k
2. Press Enter to open details panel
3. View dependencies and metadata
4. Press Esc to close details

### Running a Workflow
1. Press `6` to go to Workflows view
2. Select workflow with ↑/↓
3. Press `r` to run
4. Monitor in Orchestrate view (press `o`)

### Exporting Context
1. Press `9` to go to Export view
2. Select export items
3. Press `f` to choose format
4. Press `e` to export or `x` for clipboard copy

## Keyboard Layout Reference

```
┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐
│  1  │  2  │  3  │  4  │  5  │  6  │  7  │  8  │  9  │  0  │
│Over │Agent│Mode │Rule │Skill│Work │MCP  │Prof │Exp  │ AI  │
└─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘

┌─────┐
│  i  │ Init wizard
└─────┘

┌─────┐                           ┌─────┐
│  /  │ Filter                    │  ?  │ Help
└─────┘                           └─────┘

┌─────┐       ┌─────┐             ┌─────┐
│  k  │       │  ↑  │             │  r  │ Refresh
└─────┘       └─────┘             └─────┘
┌─────┐ ┌─────┬─────┬─────┐       ┌─────┐
│  j  │ │  ←  │  ↓  │  →  │       │  q  │ Quit
└─────┘ └─────┴─────┴─────┘       └─────┘
```

## State Management

### Per-View State
Each view maintains its own:
- Selected item index
- Scroll offset
- Filter text
- Details panel state

### State Persistence
- State preserved when switching views
- Return to view at same position
- Filter remains active per view
- Details panel state independent

### Navigation History
- View history tracked
- Up to 20 previous views
- Enables future back navigation
- History cleared on quit

## Accessibility Notes

### Keyboard-Only Navigation
- All functionality accessible via keyboard
- No mouse required
- Vim-style navigation (j/k) supported
- Arrow keys also supported

### Visual Indicators
- Selection highlighted with reverse colors
- Current item marked with `>` indicator
- Status colors: green (active), yellow (inactive)
- Connection indicator in status bar

### Help Availability
- Help always available with `?`
- Context-aware hints in status bar
- Clear labels for all actions
- Consistent navigation patterns

## Troubleshooting

### TUI Not Responding
- Press Esc to clear any active mode
- Press `?` to verify TUI is responsive
- Press `q` to quit safely

### Filter Not Working
- Verify current view supports filtering
- Press Esc to clear current filter
- Try `/` again to restart filter mode

### View Switching Issues
- Check you're pressing 1-9 (not numpad)
- Press 1 to return to overview
- Verify view number in status bar

### Details Panel Stuck
- Press Esc to close details
- Press Enter to toggle details off
- Switch views and return to reset

## Future Enhancements

### Planned Features
- Page up/down navigation
- Home/End jump functionality
- Search across all views
- Custom keyboard shortcuts
- Mouse support (optional)
- Color themes
- Configurable layouts

### In Development
- Full Modes view implementation
- Full Rules view implementation
- Skills community browser
- Workflow execution monitoring
- Profile templates
- Export format presets
