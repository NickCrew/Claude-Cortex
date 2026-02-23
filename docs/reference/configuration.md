---
layout: default
title: Configuration Reference
parent: Reference
nav_order: 1
---

# Configuration Reference

This guide covers the configuration files and resolution rules used by the current Cortex CLI.

## Resolution model

Cortex resolves two different roots:

1. **Asset root** (CORTEX_ROOT, or `--cortex-root`)  
   Used for bundled assets and watch defaults.
2. **Claude directory** (from `--scope` / CORTEX_SCOPE)  
   Used for user/project state under `.claude/`.

`--scope` supports `auto`, `project`, and `global`.

- `project`: nearest `.claude/` in the current directory tree (or creates one in cwd)
- `global`: `~/.claude/`
- `auto` (default): nearest `.claude/`, else `~/.claude/`

## Quick reference

| File | Location | Purpose |
|---|---|---|
| `cortex-config.json` | `<CORTEX_ROOT>/cortex-config.json` | Watch-mode defaults consumed by `cortex ai watch` |
| `recommendation-rules.json` | `<resolved .claude>/skills/recommendation-rules.json` | File-pattern-based skill recommendations |
| `skill-rules.json` | `<CORTEX_ROOT>/skills/skill-rules.json` (watch fallback: `~/.claude/skills/skill-rules.json`) | Keyword-based skill suggestions |
| `settings.json` | `<resolved .claude>/settings.json` | Claude settings used by hooks/statusline configuration |
| `.onboarding-state.json` | `<resolved .claude>/.onboarding-state.json` | Optional onboarding-state schema target |
| `memory-config.json` | `<resolved .claude>/memory-config.json` | Optional memory-config schema target |

## cortex-config.json

`cortex-config.json` is currently used by watch mode (`cortex ai watch`) for defaults.

### Supported keys (watch block)

- watch.directories (or watch.dirs): list of directories
- watch.auto_activate: boolean
- watch.threshold: float between `0.0` and `1.0`
- watch.interval: polling interval in seconds (`> 0`)

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

Schema: [`schemas/recommendation-rules.schema.json`](https://github.com/NickCrew/claude-cortex/blob/main/schemas/recommendation-rules.schema.json)

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

Schema: [`schemas/skill-rules.schema.json`](https://github.com/NickCrew/claude-cortex/blob/main/schemas/skill-rules.schema.json)

### Minimal example

```json
{
  "version": "2026-02-22",
  "rules": [
    {
      "name": "debugging",
      "command": "/ctx:skill systematic-debugging",
      "description": "Recommend structured debugging when users report failures.",
      "keywords": ["debug", "failing", "error"]
    }
  ]
}
```

## Optional schemas

These schemas are present in `schemas/` and can be used for validation/autocomplete in editors:

- [`schemas/memory-config.schema.json`](https://github.com/NickCrew/claude-cortex/blob/main/schemas/memory-config.schema.json)
- [`schemas/onboarding-state.schema.json`](https://github.com/NickCrew/claude-cortex/blob/main/schemas/onboarding-state.schema.json)

## Practical commands

```bash
# Check which scope/root you are using
cortex --scope project status
cortex --scope global status

# Point CLI at a specific Cortex asset root
cortex --cortex-root /path/to/claude-cortex status

# Inspect command-specific options
cortex ai watch --help
```

## See also

- [Getting Started](../guides/getting-started.md)
- [Settings Files Catalog](../settings-files.md)
