---
layout: default
title: Configuration Reference
parent: Reference
nav_order: 1
---

# Configuration Reference

This guide documents all cortex configuration files, their schemas, and usage examples.

All paths are relative to the cortex root directory (default `~/.cortex/`). You can override this with `CORTEX_ROOT`, `CLAUDE_PLUGIN_ROOT`, or use project-local `.claude/` via `--scope project`.

## Quick Reference

| File | Purpose | Required |
|------|---------|----------|
| [`cortex-config.json`](#cortex-configjson) | Main launcher configuration | No |
| [`memory-config.json`](#memory-configjson) | Memory vault settings | No |
| [`skill-rules.json`](#skill-rulesjson) | Keyword-based skill matching | No |
| [`recommendation-rules.json`](#recommendation-rulesjson) | File pattern recommendations | No |
| [`.onboarding-state.json`](#onboarding-statejson) | Wizard completion state | Auto |

---

## cortex-config.json

Main configuration file for the cortex CLI and launcher. Controls which rules, modes, flags, and plugins are active.

**Location:** `~/.cortex/cortex-config.json` or project `.claude/cortex-config.json`

**Schema:** [`schemas/cortex-config.schema.json`](https://github.com/NickCrew/claude-cortex/blob/main/schemas/cortex-config.schema.json)

### Schema

```json
{
  "$schema": "./schemas/cortex-config.schema.json",
  "plugin_id": "string",
  "plugin_dir": "string | null",
  "settings_path": "string | null",
  "claude_args": ["string"],
  "extra_plugin_dirs": ["string"],
  "rules": ["string"],
  "flags": ["string"],
  "modes": ["string"],
  "principles": ["string"]
}
```

### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `plugin_id` | string | `"cortex"` | Identifier for this plugin configuration |
| `plugin_dir` | string \| null | `null` | Path to plugin directory. If null, uses bundled assets |
| `settings_path` | string \| null | `null` | Path to Claude Code settings.json template |
| `claude_args` | string[] | `[]` | Additional arguments passed to Claude Code CLI |
| `extra_plugin_dirs` | string[] | `[]` | Additional plugin directories to load |
| `rules` | string[] | `[]` | Rule names to activate (without `.md` extension) |
| `flags` | string[] | `[]` | Flag names to enable |
| `modes` | string[] | `[]` | Mode names to activate |
| `principles` | string[] | `[]` | Principle names to include |

### Example

```json
{
  "$schema": "./schemas/cortex-config.schema.json",
  "plugin_id": "cortex",
  "plugin_dir": null,
  "settings_path": "templates/settings.json",
  "claude_args": [],
  "extra_plugin_dirs": ["plugins"],
  "rules": [
    "workflow-rules",
    "git-rules",
    "quality-rules",
    "quality-gate-rules"
  ],
  "flags": ["typescript", "testing"],
  "modes": [],
  "principles": ["clean-code", "tdd"]
}
```

### Usage

The launcher reads this file when running `cortex start`:

```bash
# Uses ~/.cortex/cortex-config.json
cortex start

# Uses project-local config
cortex start --scope project

# Override with environment variable
CORTEX_ROOT=/path/to/config cortex start
```

---

## memory-config.json

Configuration for the memory vault and automatic session capture.

**Location:** `~/.cortex/memory-config.json`

**Schema:** [`schemas/memory-config.schema.json`](https://github.com/NickCrew/claude-cortex/blob/main/schemas/memory-config.schema.json)

### Schema

```json
{
  "$schema": "../schemas/memory-config.schema.json",
  "vault_path": "string",
  "auto_capture": {
    "enabled": "boolean",
    "min_session_length": "integer",
    "exclude_patterns": ["string"],
    "last_capture": "string (ISO 8601)"
  },
  "defaults": {
    "tags": ["string"],
    "project": "string | null"
  }
}
```

### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `vault_path` | string | `"~/.cortex/memory-vault"` | Path to memory vault directory (supports `~`) |
| `auto_capture.enabled` | boolean | `true` | Enable automatic session capture |
| `auto_capture.min_session_length` | integer | `5` | Minimum exchanges before capturing |
| `auto_capture.exclude_patterns` | string[] | `[]` | Patterns to exclude from capture |
| `auto_capture.last_capture` | string | - | ISO 8601 timestamp of last capture (auto-managed) |
| `defaults.tags` | string[] | `[]` | Default tags for new memory entries |
| `defaults.project` | string \| null | `null` | Default project name for new entries |

### Example

```json
{
  "$schema": "../schemas/memory-config.schema.json",
  "vault_path": "~/.cortex/memory-vault",
  "auto_capture": {
    "enabled": true,
    "min_session_length": 5,
    "exclude_patterns": ["explain", "what is", "how do"]
  },
  "defaults": {
    "tags": ["work"],
    "project": "my-project"
  }
}
```

### Usage

Memory capture triggers automatically based on these settings. Use the CLI to manage:

```bash
# View memory status
cortex memory status

# Manually capture current session
cortex memory capture

# Search memory vault
cortex memory search "authentication bug"
```

---

## skill-rules.json

Defines keyword-based rules for recommending skills based on user intent.

**Location:** `~/.cortex/skills/skill-rules.json`

**Schema:** [`schemas/skill-rules.schema.json`](https://github.com/NickCrew/claude-cortex/blob/main/schemas/skill-rules.schema.json)

### Schema

```json
{
  "$schema": "../schemas/skill-rules.schema.json",
  "version": "string (YYYY-MM-DD)",
  "rules": [
    {
      "name": "string",
      "command": "string",
      "description": "string",
      "keywords": ["string"]
    }
  ]
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `version` | string | Schema version date (e.g., `"2025-12-14"`) |
| `rules[].name` | string | Unique identifier (lowercase, hyphens allowed) |
| `rules[].command` | string | Slash command to invoke (e.g., `/ctx:brainstorm`) |
| `rules[].description` | string | Human-readable description (10-200 chars) |
| `rules[].keywords` | string[] | Keywords that trigger this recommendation |

### Example

```json
{
  "$schema": "../schemas/skill-rules.schema.json",
  "version": "2025-12-14",
  "rules": [
    {
      "name": "brainstorm",
      "command": "/ctx:brainstorm",
      "description": "Kick off Supersaiyan ideation before coding",
      "keywords": ["brainstorm", "idea", "scope", "plan?", "where to start"]
    },
    {
      "name": "testing",
      "command": "/dev:test",
      "description": "Run project test suites / coverage gates",
      "keywords": ["test", "unit", "coverage", "pytest", "npm test"]
    },
    {
      "name": "systematic-debugging",
      "command": "/ctx:skill systematic-debugging",
      "description": "Apply systematic debugging techniques.",
      "keywords": ["systematic debug", "debug process", "bug fix"]
    }
  ]
}
```

### How It Works

When a user's message contains keywords from a rule, cortex suggests the corresponding skill:

1. User types: "I need to brainstorm some ideas for this feature"
2. Keyword match: "brainstorm", "ideas"
3. Cortex suggests: `/ctx:brainstorm`

---

## recommendation-rules.json

Defines file pattern-based rules for recommending skills based on which files are being modified.

**Location:** `~/.cortex/skills/recommendation-rules.json`

**Schema:** [`schemas/recommendation-rules.schema.json`](https://github.com/NickCrew/claude-cortex/blob/main/schemas/recommendation-rules.schema.json)

### Schema

```json
{
  "$schema": "../schemas/recommendation-rules.schema.json",
  "version": "string (YYYY-MM-DD)",
  "rules": [
    {
      "trigger": {
        "file_patterns": ["string (glob)"]
      },
      "recommend": [
        {
          "skill": "string",
          "confidence": "number (0-1)",
          "reason": "string"
        }
      ]
    }
  ]
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `version` | string | Schema version date |
| `rules[].trigger.file_patterns` | string[] | Glob patterns to match file paths |
| `rules[].recommend[].skill` | string | Skill name to recommend |
| `rules[].recommend[].confidence` | number | Confidence score (0.0 to 1.0) |
| `rules[].recommend[].reason` | string | Explanation for the recommendation |

### Example

```json
{
  "$schema": "../schemas/recommendation-rules.schema.json",
  "version": "2025-12-28.1",
  "rules": [
    {
      "trigger": {
        "file_patterns": ["**/auth/**", "**/security/**", "**/*secret*.py"]
      },
      "recommend": [
        {
          "skill": "owasp-top-10",
          "confidence": 0.9,
          "reason": "Auth/security code touched; apply OWASP checks"
        },
        {
          "skill": "secure-coding-practices",
          "confidence": 0.87,
          "reason": "Security-sensitive paths modified"
        }
      ]
    },
    {
      "trigger": {
        "file_patterns": ["**/*.tf", "**/terraform/**"]
      },
      "recommend": [
        {
          "skill": "terraform-best-practices",
          "confidence": 0.9,
          "reason": "Terraform detected; apply proven IaC practices"
        }
      ]
    }
  ]
}
```

### How It Works

When files matching a trigger pattern are modified, cortex suggests relevant skills:

1. User modifies: `src/auth/login.py`
2. Pattern match: `**/auth/**`
3. Cortex suggests: `owasp-top-10` (90% confidence), `secure-coding-practices` (87% confidence)

Skills are ranked by confidence score, with higher confidence recommendations shown first.

---

## .onboarding-state.json

Tracks wizard completion state. This file is auto-managed by the setup wizard.

**Location:** `~/.cortex/.onboarding-state.json`

**Schema:** [`schemas/onboarding-state.schema.json`](https://github.com/NickCrew/claude-cortex/blob/main/schemas/onboarding-state.schema.json)

### Schema

```json
{
  "completed_at": "string (ISO 8601) | null",
  "experience_level": "new | familiar | expert",
  "profile_applied": "string",
  "tui_tour_shown": "boolean",
  "version": "string"
}
```

### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `completed_at` | string \| null | `null` | ISO 8601 timestamp when wizard completed |
| `experience_level` | enum | `"new"` | User's self-reported experience level |
| `profile_applied` | string | `"minimal"` | Profile applied during setup |
| `tui_tour_shown` | boolean | `false` | Whether TUI tour was shown |
| `version` | string | `"1.0"` | Schema version for migrations |

### Example

```json
{
  "completed_at": "2025-01-27T14:30:00.000Z",
  "experience_level": "familiar",
  "profile_applied": "backend",
  "tui_tour_shown": true,
  "version": "1.0"
}
```

### Usage

This file is created automatically when running the setup wizard:

```bash
# Run the setup wizard
cortex init wizard

# Reset wizard state (re-run wizard on next start)
rm ~/.cortex/.onboarding-state.json
```

---

## JSON Schema Validation

All configuration files support JSON Schema validation for editor autocompletion and error checking.

### VS Code Setup

Add to your `.vscode/settings.json`:

```json
{
  "json.schemas": [
    {
      "fileMatch": ["**/cortex-config.json"],
      "url": "./schemas/cortex-config.schema.json"
    },
    {
      "fileMatch": ["**/skill-rules.json"],
      "url": "./schemas/skill-rules.schema.json"
    },
    {
      "fileMatch": ["**/recommendation-rules.json"],
      "url": "./schemas/recommendation-rules.schema.json"
    },
    {
      "fileMatch": ["**/memory-config.json"],
      "url": "./schemas/memory-config.schema.json"
    }
  ]
}
```

### Inline Schema Reference

Each config file can include a `$schema` property pointing to its schema:

```json
{
  "$schema": "./schemas/cortex-config.schema.json",
  "plugin_id": "cortex"
}
```

---

## See Also

- [Settings Files Catalog](../settings-files.md) - Complete list of all config and state files
- [Getting Started](../guides/getting-started.md) - Initial setup guide
- [Memory Guide](../guides/memory.md) - Detailed memory system documentation
