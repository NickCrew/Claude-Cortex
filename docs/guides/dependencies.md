---
layout: default
title: Dependencies
parent: Guides
nav_order: 2
---

# Dependencies

This guide lists external tools required or recommended for cortex functionality.

## Quick Install (macOS)

```bash
# Required
brew install git

# Recommended (for MCP servers)
brew install node           # Provides npm/npx
brew install uv             # Fast Python package runner

# Optional
brew install gh             # GitHub CLI
brew install bun            # Fast JS runtime (used by some plugins)
```

## Quick Install (Linux)

```bash
# Required
sudo apt install git

# Recommended
sudo apt install nodejs npm
pip install uv              # Or: pipx install uv

# Optional
sudo apt install gh xclip
```

---

## Dependency Reference

### Required

| Tool | Purpose | Install |
|------|---------|---------|
| **git** | Version control, worktrees, hooks | `brew install git` or `apt install git` |
| **python3** | Hooks, CLI, MCP servers | Usually pre-installed |

### Recommended

| Tool | Purpose | Install |
|------|---------|---------|
| **node/npm/npx** | MCP servers (context7) | `brew install node` |
| **uv/uvx** | MCP servers (mcp-memory) | `brew install uv` or `pip install uv` |
| **pip/pipx** | Python package installation | `brew install pipx` |

### Optional

| Tool | Purpose | Install |
|------|---------|---------|
| **bun** | Some plugins (claude-mem) | `brew install bun` or `npm install -g bun` |
| **gh** | GitHub CLI operations | `brew install gh` |
| **cargo** | Rust-based tools | `brew install rust` |

### Platform-Specific

| Tool | Platform | Purpose | Install |
|------|----------|---------|---------|
| **pbcopy** | macOS | Clipboard | Pre-installed |
| **xclip** | Linux | Clipboard | `apt install xclip` |
| **open** | macOS | Open files/URLs | Pre-installed |
| **xdg-open** | Linux | Open files/URLs | Pre-installed |

---

## MCP Server Dependencies

Default MCP servers and their requirements:

### context7 (Documentation Lookup)

```bash
# Requires Node.js
brew install node

# Verify
npx -y @upstash/context7-mcp --help
```

### mcp-memory (Knowledge Graph)

```bash
# Requires uv
brew install uv
# Or: pip install uv

# Verify
uvx mcp-memory-py --help
```

### basic-memory (Optional)

```bash
# Requires uv
uvx basic-memory mcp --help
```

---

## Plugin Dependencies

Some Claude Code plugins have additional requirements:

### claude-mem Plugin

Requires **bun** (JavaScript runtime):

```bash
# macOS
brew install bun

# Or via npm
npm install -g bun

# IMPORTANT: Create symlink for hooks (runs in /bin/sh)
sudo ln -sf $(which bun) /usr/local/bin/bun
```

**Why the symlink?** Hooks execute in `/bin/sh` which has a minimal PATH. If bun is installed via nvm or brew, it won't be found. The symlink makes it available system-wide.

---

## Verifying Dependencies

Check your dependencies manually:

```bash
# Core
git --version
python3 --version

# MCP servers
which npx && npx --version
which uvx && uvx --version

# Optional
which bun && bun --version
which gh && gh --version
```

---

## Troubleshooting

### "command not found" in Hooks

Hooks run in `/bin/sh` with a minimal PATH. If a command works in your terminal but fails in hooks:

1. **Find the full path**: `which bun` → `/Users/you/.nvm/.../bun`
2. **Create a symlink**: `sudo ln -sf $(which bun) /usr/local/bin/bun`

### MCP Server Won't Start

```bash
# Check if the command works directly
npx -y @upstash/context7-mcp --help
uvx mcp-memory-py --help

# Check MCP configuration
cat ~/.cortex/.mcp.json
```

### Missing Python Dependencies

```bash
# Install cortex with all extras
pip install claude-cortex[all]

# Or install specific extras
pip install claude-cortex[intelligence]  # For AI features
pip install claude-cortex[tui]           # For terminal UI
```

---

## See Also

- [Getting Started](getting-started.md) - Initial setup
- [Configuration Reference](../reference/configuration.md) - Config files
- [MCP Servers](mcp.md) - MCP configuration
