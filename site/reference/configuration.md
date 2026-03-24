---
layout: default
title: Configuration Reference
parent: Reference
nav_order: 4
---

# Configuration Reference

This guide covers the current configuration files and resolution rules used by
the Cortex CLI.

## Resolution Model

Cortex resolves two different roots:

1. **Asset root** (`CORTEX_ROOT`, or `--cortex-root`)  
   Used for bundled assets and watch defaults.
2. **Claude directory** (from `--scope` / `CORTEX_SCOPE`)  
   Used for user or project state under `.claude/`.

`--scope` supports:

- `project`: nearest `.claude/` in the current directory tree, or creates one in cwd
- `global`: `~/.claude/`
- `auto`: nearest `.claude/`, else `~/.claude/`

## Quick Reference

| File | Location | Purpose |
|:---|:---|:---|
| `cortex-config.json` | `<CORTEX_ROOT>/cortex-config.json` | Watch-mode defaults consumed by `cortex ai watch` |
| `recommendation-rules.json` | `<resolved .claude>/skills/recommendation-rules.json` | File-pattern-based skill recommendations |
| `skill-rules.json` | `<CORTEX_ROOT>/skills/skill-rules.json` with watch fallback to `~/.claude/skills/skill-rules.json` | Keyword-based skill suggestions |
| `settings.json` | `<resolved .claude>/settings.json` | Claude settings used by hooks and related integration |
| `.onboarding-state.json` | `<resolved .claude>/.onboarding-state.json` | Optional onboarding-state schema target |
| `memory-config.json` | `<resolved .claude>/memory-config.json` | Optional memory-config schema target |

## cortex-config.json

`cortex-config.json` is currently used by watch mode for defaults.

### Supported watch keys

- `watch.directories` or `watch.dirs`
- `watch.auto_activate`
- `watch.threshold`
- `watch.interval`

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
cortex ai watch

# Override defaults at runtime
cortex ai watch --dir . --threshold 0.8 --interval 1.5
```

## recommendation-rules.json

This file powers the richer Layer 2 skill recommender.

Schema:

- `schemas/recommendation-rules.schema.json`

### Minimal example

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

This file powers the low-latency keyword matcher used by the prompt hook and
watch-mode keyword suggestions.

Schema:

- `schemas/skill-rules.schema.json`

### Minimal example

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

| Variable | Default | Description |
|:---|:---|:---|
| `CORTEX_ROOT` | `~/.cortex` | Cortex home directory |
| `CORTEX_SCOPE` | unset | Scope selector: `project`, `global`, or `auto` |
| `CLAUDE_PLUGIN_ROOT` | unset | Explicit plugin assets path |
| `CORTEX_PLUGIN_ROOT` | unset | Alias for `CLAUDE_PLUGIN_ROOT` |
| `CORTEX_HOOK_LOG_PATH` | `~/.cortex/logs/hooks.log` | Hook log file location |

## Practical Commands

```bash
# Check which scope/root you are using
cortex --scope project status
cortex --scope global status

# Point the CLI at a specific Cortex asset root
cortex --cortex-root /path/to/claude-cortex status

# Inspect watch-mode options
cortex ai watch --help
```

## Notes

- `cortex-config.json` should be treated primarily as a watch-defaults file in
  the current implementation.
- `recommendation-rules.json` and `skill-rules.json` are separate on purpose:
  the first is for structured recommendations, the second is for keyword
  matching.
- When documenting skill recommendations, keep root and scope behavior separate
  from recommendation behavior so the pages do not drift into old plugin-model
  explanations.

## See Also

- [Skills](../guides/skills.md)
- [AI Intelligence](../guides/ai-intelligence.md)
