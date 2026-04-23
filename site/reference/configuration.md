---
layout: default
title: Configuration Reference
parent: Reference
nav_order: 4
---

# Configuration Reference

Complete reference for configuration files, environment variables, and resolution
rules used by the Cortex CLI.

## Resolution Model

Cortex resolves two different roots:

1. **Asset root** (`CORTEX_ROOT`, or `--cortex-root`)
   Used for bundled assets and watch defaults.
2. **Claude directory** (from `--scope` / `CORTEX_SCOPE`)
   Used for user or project state under `.claude/`.

`--scope` supports:

| Value | Alias | Behavior |
|:------|:------|:---------|
| `project` | `local` | Nearest `.claude/` in the current directory tree, or creates one in cwd |
| `global` | `home` | `~/.claude/` |
| `auto` | *(default)* | Nearest `.claude/`, else `~/.claude/` |

## Quick Reference

| File | Location | Purpose |
|:-----|:---------|:--------|
| `cortex-config.json` | `<CORTEX_ROOT>/cortex-config.json` | Watch-mode defaults consumed by `cortex suggest --watch` |
| `intelligence-config.json` | `<claude-dir>/intelligence-config.json` | LLM intelligence, model selection, budget, and caching |
| `recommendation-rules.json` | `<claude-dir>/skills/recommendation-rules.json` | File-pattern-based skill recommendations |
| `skill-rules.json` | `<CORTEX_ROOT>/skills/skill-rules.json` with fallback to `~/.claude/skills/skill-rules.json` | Keyword-based skill suggestions |
| `settings.json` | `<claude-dir>/settings.json` | Claude settings used by hooks and related integration |

Where `<claude-dir>` is the resolved `.claude/` directory (see Resolution Model above).

## cortex-config.json

Watch-mode defaults.

### Supported keys

| Key | Type | Default | Description |
|:----|:-----|:--------|:------------|
| `watch.directories` | array | `[]` | Directories to monitor (alias: `watch.dirs`) |
| `watch.auto_activate` | bool | `true` | Auto-activate high-confidence agent recommendations |
| `watch.threshold` | float | `0.7` | Minimum confidence score for recommendations |
| `watch.interval` | float | `2.0` | Polling interval in seconds |

### Example

```json
{
  "watch": {
    "directories": ["~/Developer/my-project"],
    "auto_activate": true,
    "threshold": 0.75,
    "interval": 2.0
  }
}
```

### Usage

```bash
# Uses defaults from <CORTEX_ROOT>/cortex-config.json when present
cortex suggest --watch

# Override defaults at runtime
cortex suggest --watch --no-auto-activate --threshold 0.8 --interval 1.5
```

## intelligence-config.json

Configuration for the optional LLM-powered intelligence layer. Stored in the
resolved Claude directory.

### Supported keys

| Key | Type | Default | Description |
|:----|:-----|:--------|:------------|
| `llm_enabled` | bool | `false` | Enable LLM-powered recommendations (requires `anthropic` package) |
| `semantic_fallback_threshold` | float | `0.5` | Minimum confidence for semantic matching fallback (0.0--1.0) |
| `model_selection.auto_select` | bool | `true` | Auto-select model based on task complexity |
| `model_selection.default_model` | string | `"claude-sonnet-4-20250514"` | Model when not auto-selecting |
| `model_selection.haiku_threshold` | float | `0.4` | Complexity below this uses Haiku (cheaper) |
| `model_selection.opus_threshold` | float | `0.75` | Complexity above this uses Opus (more capable) |
| `model_selection.force_model` | string | `null` | Override: always use this model |
| `budget.enabled` | bool | `false` | Enable daily spending tracking |
| `budget.daily_limit` | float | `1.0` | Daily spending limit in USD (0 = unlimited) |
| `budget.warning_threshold` | float | `0.8` | Warn at this percentage of daily limit |
| `budget.confirmation_threshold` | float | `0.01` | Require confirmation for requests over this cost (USD) |
| `caching.enabled` | bool | `true` | Enable prompt caching (~90% cost reduction) |
| `caching.ttl` | int | `300` | Cache time-to-live in seconds |

### Example

```json
{
  "llm_enabled": true,
  "model_selection": {
    "auto_select": true,
    "haiku_threshold": 0.4,
    "opus_threshold": 0.75
  },
  "budget": {
    "enabled": true,
    "daily_limit": 2.0,
    "warning_threshold": 0.8
  },
  "caching": {
    "enabled": true,
    "ttl": 300
  }
}
```

## recommendation-rules.json

Powers the Layer 2 skill recommender with file-pattern-based rules.

Schema: `schemas/recommendation-rules.schema.json`

### Example

```json
{
  "version": "2026-02-22",
  "rules": [
    {
      "trigger": {
        "file_patterns": ["**/auth/**", "**/security/**"]
      },
      "recommend": [
        {
          "skill": "secure-coding-practices",
          "confidence": 0.9,
          "reason": "Security-sensitive files changed"
        }
      ]
    }
  ]
}
```

## skill-rules.json

Powers the low-latency keyword matcher used by the prompt hook and
watch-mode skill suggestions.

Schema: `schemas/skill-rules.schema.json`

### Example

```json
{
  "version": "2026-02-22",
  "rules": [
    {
      "name": "debugging",
      "command": "/ctx:systematic-debugging",
      "description": "Recommend structured debugging when users report failures.",
      "keywords": ["debug", "failing", "error"]
    }
  ]
}
```

## Environment Variables

### Cortex Core

| Variable | Default | Description |
|:---------|:--------|:------------|
| `CORTEX_ROOT` | `~/.cortex` | Cortex home directory (asset root) |
| `CORTEX_SCOPE` | `auto` | Scope selector: `project`/`local`, `global`/`home`, or `auto` |
| `CLAUDE_PLUGIN_ROOT` | *(unset)* | Explicit plugin assets path (set by Claude Code for plugin commands) |

### User-Facing Overrides

| Variable | Default | Description |
|:---------|:--------|:------------|
| `CORTEX_SKIP_WIZARD` | *(unset)* | Set to suppress the first-run setup wizard |
| `CORTEX_CONTEXT_LIMIT` | `200000` | Override context token limit |
| `CORTEX_TUI_THEME` | *(unset)* | Path to a custom TUI theme file (also: `CLAUDE_TUI_THEME`) |
| `CORTEX_MEMORY_VAULT` | *(unset)* | Override memory vault directory |
| `CLAUDE_TASKS_HOME` | *(unset)* | Override tasks directory |

### Watch Mode (Internal)

| Variable | Default | Description |
|:---------|:--------|:------------|
| `CORTEX_WATCH_DAEMON` | *(unset)* | Internal: marks a daemon process |
| `CORTEX_WATCH_PID_PATH` | *(unset)* | Override PID file path |
| `CORTEX_WATCH_LOG_PATH` | *(unset)* | Override watch log file path |

### Hook Environment

These variables are set automatically when hooks execute:

| Variable | Description |
|:---------|:------------|
| `CLAUDE_HOOK_PROMPT` | The user's prompt text |
| `CLAUDE_SESSION_CONTEXT` | Current session context |
| `CLAUDE_CHANGED_FILES` | Colon-separated list of changed files |

## Practical Commands

```bash
# Check which scope/root you are using
cortex --scope project status
cortex --scope global status

# Point the CLI at a specific Cortex asset root
cortex --cortex-root /path/to/cortex status

# Inspect watch-mode options
cortex suggest --watch --help
```

## Related

- [AI Intelligence]({% link guides/ai-intelligence.md %}) --- agent recommendations and watch mode
- [Skills]({% link guides/skills.md %}) --- skill recommendation system
- [Terminal UI]({% link guides/tui.md %}) --- TUI configuration and views
