# Cortex

Context orchestration toolkit for Claude Code, with curated agents/skills/rules/hooks and a Python CLI for management.

Docs: <https://cortex.atlascrew.dev/>

## Why Cortex

- Curated context assets for Claude Code (`agents/`, `skills/`, `rules/`, `hooks/`)
- A Python CLI (`cortex`) for activation, validation, TUI workflows, and diagnostics
- Built-in support for MCP documentation, worktree management, memory capture, and review gates

## Repository Layout

| Path | Purpose |
|---|---|
| `agents/` | Agent definitions used by Claude Code |
| `skills/` | Reusable skill modules with metadata and guidance |
| `rules/` | Rule modules for behavior and quality guardrails |
| `hooks/` | Hook definitions and validation assets |
| `commands/` | Slash-command style command assets |
| `claude_ctx_py/` | Python CLI implementation |
| `docs/` | Documentation source for guides/reference |
| `schemas/` | Validation schemas |
| `tests/` | Unit and integration tests |

## Installation

### 1) Install plugin assets in Claude Code

```bash
claude install github:NickCrew/claude-cortex
```

### 2) Install CLI (optional but recommended)

```bash
# pipx
pipx install claude-cortex

# or pip
pip install claude-cortex
```

For local development:

```bash
git clone https://github.com/NickCrew/claude-cortex.git
cd claude-cortex
pip install -e ".[dev]"
```

## Quick Start

```bash
# Link bundled assets into ~/.claude
cortex install link

# Optional post-install helpers
cortex install post

# Check current state
cortex status

# Launch TUI
cortex tui
```

## CLI Command Map

Top-level commands currently available:

- `agent` - list, activate/deactivate, dependency graph, validation
- `rules` - list, activate/deactivate, edit, status
- `hooks` - hooks configuration validation
- `skills` - discovery, validation, analytics, recommendations, ratings
- `mcp` - list/show/docs/test/diagnose MCP server configurations
- `worktree` - list/add/remove/prune git worktrees
- `statusline` - render and configure statusline output
- `tui` - interactive Textual UI
- `ai` - recommendations, auto-activation, watch mode, learning ingestion
- `export` - export context for sharing/use in other tools
- `install` - link/completions/manpage/statusline helpers
- `memory` - capture/search session and project notes
- `plan` - inspect/manage plan files
- `docs` - list/search/view docs with optional docs TUI
- `dev` - schema/manpage maintenance helpers
- `file` - Claude Files API helpers
- `uninstall` - remove installed cortex assets
- `status` - summary status output
- `review` - run reviewer gate before task completion

Run help anytime:

```bash
cortex --help
cortex <command> --help
```

## Common Workflows

### Agent + skill management

```bash
cortex agent list
cortex agent status
cortex skills list
cortex skills info doc-claim-validator
```

### MCP + worktrees

```bash
cortex mcp list
cortex mcp diagnose
cortex worktree list
```

### AI recommendations

```bash
cortex ai recommend
cortex ai auto-activate
cortex ai watch
```

### Review gate

```bash
cortex review --dry-run
cortex review -c feature -c debug
```

## Development

### Preferred local commands

```bash
command -v committer
command -v tx
```

- Use `committer` for atomic commits
- Use `tx` for local workflow/service orchestration

### Build, test, quality

```bash
just install
just test
just lint
just type-check
```

Additional useful targets:

```bash
just test-unit
just test-integration
just test-cov
just docs
just docs-build
just build
```

### Docs preview

```bash
cd docs
bundle exec jekyll serve --livereload
```

## Documentation Index

- [docs/README.md](docs/README.md)
- [docs/reference/index.md](docs/reference/index.md)
- [docs/architecture/README.md](docs/architecture/README.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [CHANGELOG.md](CHANGELOG.md)
- [CREDITS.md](CREDITS.md)

## License

MIT. See `LICENSE`.
