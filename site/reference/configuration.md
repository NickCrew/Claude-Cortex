---
layout: default
title: Configuration Reference
parent: Reference
nav_order: 4
---

# Configuration Reference

## cortex-config.json

**Location:** `~/.cortex/cortex-config.json`

### Full Example

```json
{
  "plugin_dir": "~/Developer/claude-cortex",
  "plugin_id": "cortex",
  "extra_plugin_dirs": ["~/my-custom-plugin"],
  "rules": ["workflow-rules", "quality-rules", "git-rules"],
  "flags": ["mode-activation", "mcp-servers", "testing-quality"],
  "modes": ["Deep_Analysis", "Quality_Focus"],
  "principles": ["00-core-directive", "10-philosophy", "20-engineering-mindset"],
  "settings_path": "~/.claude/settings.json",
  "claude_args": ["--model", "claude-sonnet-4-20250514"],
  "watch": {
    "directories": ["~/projects/my-app"],
    "auto_activate": true,
    "threshold": 0.7,
    "interval": 2.0
  }
}
```

### Fields

| Field | Type | Default | Description |
|:------|:-----|:--------|:------------|
| `plugin_dir` | string | auto-detected | Explicit path to Cortex assets |
| `plugin_id` | string | `"cortex"` | Plugin ID for registry lookup |
| `extra_plugin_dirs` | string[] | `[]` | Additional `--plugin-dir` entries |
| `rules` | string[] | all in `rules/` | Rule slugs (without `.md`) to symlink |
| `flags` | string[] | from `FLAGS.md` | Fallback if `FLAGS.md` missing |
| `modes` | string[] | `[]` | Mode slugs to append to system prompt |
| `principles` | string[] | all in `principles/` | Principles snippets to include |
| `settings_path` | string | -- | Path passed to Claude via `--settings` |
| `claude_args` | string[] | `[]` | Args always passed to `claude` |
| `watch.directories` | string[] | -- | Directories to monitor |
| `watch.auto_activate` | boolean | -- | Auto-activate recommended agents |
| `watch.threshold` | number | -- | Confidence threshold for activation |
| `watch.interval` | number | -- | Polling interval in seconds |

## Environment Variables

| Variable | Default | Description |
|:---------|:--------|:------------|
| `CORTEX_ROOT` | `~/.cortex` | Cortex home directory |
| `CORTEX_SCOPE` | -- | Scope: `project`, `global`, or `plugin` |
| `CLAUDE_PLUGIN_ROOT` | -- | Explicit plugin assets path |
| `CORTEX_PLUGIN_ROOT` | -- | Alias for `CLAUDE_PLUGIN_ROOT` |
| `CORTEX_HOOK_LOG_PATH` | `~/.cortex/logs/hooks.log` | Hook log file location |

## Directory Structure

### ~/.cortex/ (Cortex Home)

```
~/.cortex/
├── cortex-config.json     # Launcher configuration
├── FLAGS.md               # Active flag references
├── PRINCIPLES.md          # Generated principles
├── rules/                 # Rule markdown files
├── flags/                 # Flag category files (22 files)
├── modes/                 # Behavioral mode files
├── principles/            # Principles snippet files
├── data/
│   └── skill-ratings.db   # Skill ratings database
└── logs/
    └── hooks.log          # Hook execution log
```

### ~/.claude/ (Claude Code Integration)

```
~/.claude/
├── agents/        → symlink to Cortex agents/
├── skills/        → symlink to Cortex skills/
├── rules/
│   └── cortex/    → symlinked active rules
├── hooks/         → symlink to Cortex hooks/
├── commands/      → generated skill command aliases
└── settings.json  # Claude Code settings (hooks, etc.)
```

## Activation State Files

| File | Location | Purpose |
|:-----|:---------|:--------|
| `.active-modes` | `~/.cortex/` | Currently active modes |
| `.active-rules` | `~/.cortex/` | Currently active rules |
| `.active-mcp` | `~/.cortex/` | Active MCP documentation |
| `.active-principles` | `~/.cortex/` | Active principles snippets |

## Plugin Manifest

**File:** `.claude-plugin/plugin.json`

```json
{
  "name": "cortex",
  "version": "3.0.0",
  "description": "Context orchestration plugin",
  "commands": ["./commands"]
}
```

## Plugin Root Resolution Order

When `cortex start` launches, it finds Cortex assets in this order:

1. `--plugin-root` CLI argument
2. `CLAUDE_PLUGIN_ROOT` or `CORTEX_PLUGIN_ROOT` environment variable
3. `plugin_dir` field in `cortex-config.json`
4. Bundled assets from the installed Python package
5. Claude's plugin registry (`~/.claude/plugins/installed_plugins.json`)
