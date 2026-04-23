---
layout: default
title: Configuration
parent: Getting Started
nav_order: 3
---

# Configuration

Cortex configuration is split between the Cortex asset root and the resolved
Claude directory.

## Two Important Locations

1. `<CORTEX_ROOT>/cortex-config.json`
2. `<resolved .claude>/settings.json`

`CORTEX_ROOT` defaults to `~/.cortex`. The resolved `.claude/` directory is
chosen from `--scope` or `CORTEX_SCOPE`.

## cortex-config.json

In the current implementation, `cortex-config.json` is primarily a watch-mode
defaults file.

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

### Supported watch keys

- `watch.directories` or `watch.dirs`
- `watch.auto_activate`
- `watch.threshold`
- `watch.interval`

## Environment Variables

| Variable | Purpose |
|:---------|:--------|
| `CORTEX_ROOT` | Override Cortex home directory (default: `~/.cortex`) |
| `CORTEX_SCOPE` | Scope: `project`, `global`, or `auto` |
| `CLAUDE_PLUGIN_ROOT` | Explicit plugin assets path |
| `CORTEX_HOOK_LOG_PATH` | Override hook log location |

## Scope Selection

```bash
# Use project-local .claude/ directory
cortex --scope project status

# Use global ~/.claude/
cortex --scope global status

# Use explicit asset root
cortex --cortex-root /path/to/claude-cortex status
```

## Watch Defaults In Practice

```bash
# Use defaults from <CORTEX_ROOT>/cortex-config.json
cortex suggest --watch

# Override at runtime
cortex suggest --watch --dir . --threshold 0.8 --interval 1.5
```

## Rules And Skills

Rules and skills are managed through their own command groups:

```bash
# Rules
cortex rules list
cortex rules status

# Skills
cortex skills list
cortex skills recommend
```

Slash commands are generated from installed skills, not maintained as a
separate static catalog. See [Commands]({% link reference/commands.md %}) for
the current model.

## Read Next

- [Configuration Reference]({% link reference/configuration.md %})
- [Skills Guide]({% link guides/skills.md %})
