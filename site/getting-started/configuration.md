---
layout: default
title: Configuration
parent: Getting Started
nav_order: 3
---

# Configuration

Cortex is configured through `cortex-config.json` and several supporting files in `~/.cortex/`.

## Config File

**Location:** `~/.cortex/cortex-config.json` (created automatically on first `cortex start`)

```json
{
  "plugin_dir": "~/Developer/claude-cortex",
  "rules": ["workflow-rules", "quality-rules", "git-rules"],
  "flags": ["mode-activation", "mcp-servers", "testing-quality"],
  "modes": ["Deep_Analysis", "Quality_Focus"],
  "settings_path": "~/.claude/settings.json",
  "claude_args": ["--model", "claude-sonnet-4-20250514"]
}
```

### Field Reference

| Field | Type | Description |
|:------|:-----|:------------|
| `plugin_dir` | string | Path to Cortex assets. Overrides auto-discovery. |
| `extra_plugin_dirs` | string[] | Additional plugin directories. |
| `rules` | string[] | Rule slugs (without `.md`) to symlink. |
| `flags` | string[] | Fallback if `FLAGS.md` is missing. |
| `modes` | string[] | Mode slugs to append to system prompt. |
| `principles` | string[] | Principles snippets to include. |
| `settings_path` | string | Path passed to Claude via `--settings`. |
| `claude_args` | string[] | Args always passed to `claude` command. |
| `watch` | object | Watch mode defaults. |

## Directory Layout

```
~/.cortex/
├── cortex-config.json    # Launcher configuration
├── FLAGS.md              # Active flag references
├── PRINCIPLES.md         # Generated principles
├── rules/                # Rule markdown files
├── flags/                # Individual flag category files
├── modes/                # Behavioral mode files
└── principles/           # Principles snippet files
```

## Overriding Per Session

```bash
# Override modes for one session
cortex start --modes "Architect,Deep_Analysis"

# Override flags for one session
cortex start --flags "security-hardening,database-operations"

# Pass extra args to Claude
cortex start -- --model claude-sonnet-4-20250514
```

## Environment Variables

| Variable | Purpose |
|:---------|:--------|
| `CORTEX_ROOT` | Override Cortex home directory (default: `~/.cortex`) |
| `CORTEX_SCOPE` | Scope: `project`, `global`, or `plugin` |
| `CLAUDE_PLUGIN_ROOT` | Explicit plugin assets path |
| `CORTEX_HOOK_LOG_PATH` | Override hook log location |

## Scope Selection

```bash
# Use project-local .claude/ directory
cortex --scope project status

# Use explicit plugin root
cortex --plugin-root /path/to/cortex status

# Set via environment
export CLAUDE_PLUGIN_ROOT="$HOME/Developer/claude-cortex"
cortex status
```

## Managing Rules

```bash
# List available rules
cortex rules list

# Show active rules
cortex rules status

# Activate/deactivate specific rules
cortex rules activate <rule-name>
cortex rules deactivate <rule-name>
```

## Managing Flags

Flags are token-efficient context modules that control Claude's behavior. Enable or disable them through the TUI Flag Manager or by editing `FLAGS.md`.

```bash
# Open Flag Manager in TUI
cortex tui
# Press Ctrl+G for Flag Manager
```

| Profile | Active Flags | Token Savings |
|:--------|:-------------|:--------------|
| minimal | 3 categories | 87% |
| frontend | 7 categories | 67% |
| backend | 7 categories | 71% |
| devops | 5 categories | 81% |
| full | 22 categories | 0% |

See [Flags Reference]({% link reference/flags.md %}) for all 22 flag categories.
