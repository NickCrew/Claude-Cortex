# Warp AI & Terminal AI Integration

Integrate `cortex` with Warp AI and other terminal AI tools using convenient shell aliases.

```bash
# Install context export aliases for your shell
cortex install aliases

# Preview what will be installed
cortex install aliases --dry-run

# Show all available aliases
cortex install aliases --show
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
