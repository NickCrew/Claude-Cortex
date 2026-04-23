---
layout: default
title: Notes Vault
parent: Guides
nav_order: 7
---

# Notes Vault

The Notes Vault provides persistent knowledge storage across Claude Code sessions. Capture domain knowledge, project context, session summaries, and bug fixes in structured markdown notes.

## Note Types

| Type | Icon | Purpose |
|:-----|:-----|:--------|
| **Knowledge** | brain | Domain knowledge, gotchas, corrections |
| **Projects** | building | Project context and architecture |
| **Sessions** | calendar | Work session summaries and decisions |
| **Fixes** | wrench | Bug fixes with root cause analysis |

## Capturing Notes

### Quick Knowledge

```bash
cortex notes remember "FastAPI uses Starlette under the hood"
cortex notes remember "Uses ASGI" --topic "fastapi" --tags "python,async"
```

### Project Context

```bash
cortex notes project "my-api" --purpose "REST API for users"
cortex notes project "auth-service" \
  --path "~/services/auth" \
  --related "user-db,redis"
```

### Session Summaries

```bash
cortex notes capture "Added auth" --summary "Built JWT authentication"
cortex notes capture "API Refactor" \
  --summary "Refactored API endpoints" \
  --decisions "Use dependency injection|Add caching layer" \
  --implementations "Refactored auth|Added Redis cache" \
  --open "Add metrics|Write docs" \
  --project "my-api"
```

### Bug Fixes

```bash
cortex notes fix "Token expired too fast" \
  --problem "Tokens expiring in 1 minute" \
  --cause "Wrong TTL constant" \
  --solution "Changed TTL to 3600 seconds"
```

## Searching and Listing

```bash
# List all notes
cortex notes list

# List by type
cortex notes list knowledge
cortex notes list sessions --recent 5
cortex notes list fixes --tags "my-api"

# Search across notes
cortex notes search "asyncio"
cortex notes search "authentication" --type knowledge
cortex notes search "bug" --limit 5

# Vault statistics
cortex notes stats
```

## Auto-Capture

Auto-capture creates session notes automatically based on session length:

```bash
# Enable auto-capture
cortex notes auto on

# Disable
cortex notes auto off

# Check status
cortex notes auto status
```

Auto-capture triggers when:
- Session length exceeds 5 minutes (configurable)
- Time since last capture exceeds 30 minutes
- Prompt doesn't match exclude patterns (e.g., "explain", "what is")

## TUI Memory View

Press `M` in the TUI to open the Notes Vault:

| Key | Action |
|:----|:-------|
| `M` | Open Notes Vault view |
| `/` | Focus search input |
| `n` or `N` | New note dialog |
| `r` | Refresh notes list |
| `Enter` | View selected note |
| `O` | Open note in editor |
| `D` | Delete selected note |
| `Esc` | Close view |

The view shows a browsable list of notes with type icons, titles, and dates, plus a preview pane with syntax-highlighted content.

## Storage

Notes are stored as markdown files with YAML frontmatter:

```
~/basic-memory/
├── knowledge/
│   └── fastapi-starlette.md
├── projects/
│   └── my-api-context.md
├── sessions/
│   └── 2026-02-16-auth-implementation.md
└── fixes/
    └── token-ttl-fix.md
```

Each note looks like:

```markdown
# Token TTL Fix

tags: #fixes #auth #jwt

## Problem
Tokens expiring in 1 minute instead of 1 hour.

## Root Cause
Wrong TTL constant -- was set to 60 (seconds) instead of 3600.

## Solution
Changed TTL to 3600 seconds in config.py.
```

### Configuration

Override the vault location:

```bash
# Environment variable
export CORTEX_MEMORY_VAULT=~/my-notes

# Or in ~/.claude/memory-config.json
{
  "vault_path": "~/basic-memory",
  "auto_capture": {
    "enabled": true,
    "min_session_length": 5,
    "exclude_patterns": ["explain", "what is", "how do"]
  }
}
```

## Memory Keeper Agent

For automatic memory management, activate the Memory Keeper agent:

```bash
cortex agent activate memory-keeper
```

The agent proactively captures session context, retrieves relevant past notes, and classifies entries into the correct note type.

## CLI Reference

```bash
cortex notes remember TEXT [--topic TOPIC] [--tags TAGS]
cortex notes project NAME [--path PATH] [--purpose PURPOSE] [--related PROJECTS]
cortex notes capture [TITLE] [--summary TEXT] [--decisions TEXT]
                              [--implementations TEXT] [--open TEXT] [--project NAME]
cortex notes fix TITLE [--problem TEXT] [--cause TEXT] [--solution TEXT]
                        [--files FILES] [--project NAME]
cortex notes auto [on|off|status]
cortex notes list [TYPE] [--recent N] [--tags TAGS]
cortex notes search QUERY [--type TYPE] [--limit N]
cortex notes stats
```
