# Memory Vault

The Memory Vault provides persistent knowledge storage for Claude Code sessions. It captures domain knowledge, project context, session summaries, and bug fixes in Markdown format.

## Overview

Memory notes are organized into four types:
- **Knowledge** - Domain knowledge, corrections, and gotchas
- **Projects** - Project context and relationships
- **Sessions** - Session summaries and decisions
- **Fixes** - Bug fixes and solutions

Notes are stored in `~/basic-memory/` by default, organized by type.

## The Memory Keeper Agent

The **Memory Keeper** (`memory-keeper`) is a specialized agent designed to manage this vault for you. It automatically handles:

- **Recording**: Captures sessions and decisions without you needing to remember CLI commands.
- **Retrieving**: Searches past context to answer "What did we do yesterday?" or "How did we fix this last time?".
- **Organizing**: Ensures notes are categorized correctly (Fix vs Knowledge).

Activate it with:
```bash
cortex agent activate memory-keeper
```
Or just ask it: "Remember that..." or "What was the fix for...?"

## Security

The memory system includes robust **Path Validation** to ensure that all read/write operations are strictly confined to the vault directory. Directory traversal attempts (e.g., `../sensitive_file`) are blocked.

## Quick Start

### CLI Commands

```bash
# List all notes
cortex memory list

# List notes by type
cortex memory list knowledge
cortex memory list fixes --recent 5

# Remember domain knowledge
cortex memory remember "Python asyncio uses a single thread"

# Capture session summary
cortex memory capture "Implemented auth feature"

# Document a bug fix
cortex memory fix "Fixed memory leak in stream processor"

# Search notes
cortex memory search "asyncio"

# Check auto-capture status
cortex memory auto status
cortex memory auto on
cortex memory auto off
```

### Slash Commands

Use these commands within Claude Code:

- `/memory:list` - List notes in the vault
- `/memory:list [type]` - List notes by type (knowledge, projects, sessions, fixes)
- `/memory:remember <fact>` - Store domain knowledge
- `/memory:project <context>` - Store project context
- `/memory:capture <summary>` - Capture session summary
- `/memory:fix <description>` - Document a bug fix
- `/memory:search <query>` - Search notes
- `/memory:auto` - Check/toggle auto-capture

## TUI Integration

Access the Memory Vault in the TUI:

1. Launch TUI: `cortex tui`
2. Press `m` or select "Memory" from the view menu
3. Browse notes organized by type
4. View modification times and tags

### Memory View Features

| Column | Description |
|--------|-------------|
| Type | Note category with icon |
| Title | Note name/slug |
| Modified | Time since last update |
| Tags | Associated tags |

### Type Icons

| Icon | Type | Description |
|------|------|-------------|
| 📚 | knowledge | Domain knowledge |
| 📁 | projects | Project context |
| 📅 | sessions | Session summaries |
| 🔧 | fixes | Bug fixes |

## Configuration

### Vault Location

Set a custom vault path:

```bash
# Via environment variable
export CORTEX_MEMORY_VAULT=~/my-notes

# Or in ~/.cortex/memory-config.json
{
  "vault_path": "~/my-notes"
}
```

### Auto-Capture

Enable automatic session capture on exit:

```bash
cortex memory auto on
```

Configuration in `~/.cortex/memory-config.json`:

```json
{
  "vault_path": "~/basic-memory",
  "auto_capture": {
    "enabled": true,
    "min_session_length": 5,
    "exclude_patterns": ["explain", "what is", "how do"]
  }
}
```

## Note Format

Notes are stored as Markdown with YAML frontmatter:

```markdown
# Stream Processor Delay Investigation

tags: #knowledge #debugging #hackermind

## Context
Investigation into streaming delays...

## Key Findings
- Finding 1
- Finding 2

## Related
- [[other-note]]
```

## Directory Structure

```
~/basic-memory/
├── knowledge/
│   └── stream-processor-delay-investigation.md
├── projects/
│   └── my-project-context.md
├── sessions/
│   └── 2025-12-01-auth-implementation.md
└── fixes/
    └── memory-leak-fix.md
```

## Hooks Integration

Use the memory auto-capture hook for automatic session persistence:

```bash
# Install the hook
cortex asset install hooks memory_auto_capture
```

See `hooks/examples/memory_auto_capture.py` for implementation details.

## Best Practices

1. **Use descriptive titles** - Makes searching easier
2. **Add relevant tags** - Improves categorization
3. **Link related notes** - Use `[[note-name]]` syntax
4. **Capture immediately** - Don't wait until end of session
5. **Review periodically** - Clean up outdated notes

## Troubleshooting

### Notes not showing in TUI

If the Memory view shows "No notes found":

1. Check vault exists: `ls ~/basic-memory/`
2. Verify notes are present: `cortex memory list`
3. Refresh the TUI view: press `r`

### Auto-capture not working

1. Check if enabled: `cortex memory auto status`
2. Verify session length meets minimum threshold
3. Check exclude patterns aren't matching your sessions
