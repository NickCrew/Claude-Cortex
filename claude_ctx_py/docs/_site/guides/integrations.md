# Warp AI & Terminal AI Integration

Integrate `claude-ctx` with Warp AI and other terminal AI tools using convenient shell aliases.

```bash
# Install context export aliases for your shell
claude-ctx install aliases

# Preview what will be installed
claude-ctx install aliases --dry-run

# Show all available aliases
claude-ctx install aliases --show
```

**Available aliases:**
- `ctx` - Export full context (all components)
- `ctx-light` - Lightweight export (excludes skills, mcp_docs)
- `ctx-rules`, `ctx-agents`, `ctx-modes`, `ctx-core` - Specific exports
- `ctx-list` - List available components
- `ctx-copy` - Copy context to clipboard (macOS)
- `ctx-agent-list`, `ctx-mode-list`, `ctx-tui` - Quick management

**Usage with Warp AI:**
```bash
# Export context before asking Warp AI
ctx

# Ask Warp AI your question using Cmd+` (or your hotkey)
# Warp AI will have access to your exported context
```

See [Warp AI Integration Guide](../features/WARP_AI_INTEGRATION.md) for complete documentation.
