# Cortex

Context orchestration toolkit for Claude Code, with curated agents/skills/rules/hooks and a Python CLI for management.

Docs: <https://cortex.atlascrew.dev/>

## Why Cortex

- Curated context assets for Claude Code (`agents/`, `skills/`, `rules/`, `hooks/`)
- A Python CLI (`cortex`) for activation, validation, TUI workflows, diagnostics, and exports
- Built-in support for MCP docs, memory capture, and review gates

## Feature Highlights

### `agent-loops` Codex skill

- Skill file: `codex/skills/agent-loops/SKILL.md`
- Purpose: structured implementation loop with verification and review gates
- Complements CLI review flow:

```bash
cortex review --dry-run
cortex review -c feature -c debug
```

### Skills command suite

- Discover and inspect skills:

```bash
cortex skills list
cortex skills info agent-loops
cortex skills recommend
```

- Collect feedback and ratings:

```bash
cortex skills feedback agent-loops helpful --comment "High signal loop guidance"
cortex skills rate agent-loops --stars 5 --review "Reliable workflow"
```

### AI command suite

- Recommendations and auto-activation:

```bash
cortex ai recommend
cortex ai auto-activate
```

- Continuous watch mode:

```bash
cortex ai watch --interval 2.0 --threshold 0.7 --dir .
```

- Learning ingestion and export:

```bash
cortex ai ingest-review .agents/reviews/latest.md
cortex ai export --output ai-recommendations.json
```

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

## Installation (pip / pipx)

### Install released CLI

```bash
# Recommended
pipx install claude-cortex

# Alternative
python3 -m pip install claude-cortex
```

### Local development install

```bash
git clone https://github.com/NickCrew/claude-cortex.git
cd claude-cortex
python3 -m pip install -e ".[dev]"
```

## Quick Start

```bash
# Link bundled assets into ~/.claude
cortex install link

# Optional post-install helpers (completions + manpages)
cortex install post

# Check current state
cortex status

# Launch TUI
cortex tui
```

## CLI Arguments and Commands

Current global arguments:

- `--scope {auto,project,global}`
- `--cortex-root PATH` (alias: `--plugin-root`)
- `--skip-wizard` (alias: `--no-init`)

Usage pattern:

```bash
cortex [--scope {auto,project,global}] [--cortex-root PATH] [--skip-wizard] <command> [<args>]
```

Documented command groups in this README:

- `agent`
- `rules`
- `hooks`
- `skills`
- `mcp`
- `statusline`
- `tui`
- `ai`
- `export`
- `install`
- `memory`
- `plan`
- `docs`
- `dev`
- `file`
- `uninstall`
- `status`
- `review`

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

### MCP diagnostics

```bash
cortex mcp list
cortex mcp diagnose
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

- [docs/index.md](docs/index.md)
- [docs/README.md](docs/README.md)
- [docs/guides/getting-started.md](docs/guides/getting-started.md)
- [docs/guides/commands.md](docs/guides/commands.md)
- [docs/guides/skills.md](docs/guides/skills.md)
- [docs/guides/asset-manager.md](docs/guides/asset-manager.md)
- [docs/guides/prompt-library.md](docs/guides/prompt-library.md)
- [docs/tutorials/index.md](docs/tutorials/index.md)
- [docs/reference/index.md](docs/reference/index.md)
- [docs/reference/configuration.md](docs/reference/configuration.md)
- [docs/reference/api/index.md](docs/reference/api/index.md)
- [docs/architecture/README.md](docs/architecture/README.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [CHANGELOG.md](CHANGELOG.md)
- [CREDITS.md](CREDITS.md)

## License

MIT. See `LICENSE`.
