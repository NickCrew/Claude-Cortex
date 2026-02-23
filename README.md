# Cortex

Context orchestration toolkit for Claude Code, with curated agents/skills/rules/hooks and a Python CLI for management.

Docs: <https://cortex.atlascrew.dev/>

## Why Cortex

- Curated context assets for Claude Code (`agents/`, `skills/`, `rules/`, `hooks/`)
- A Python CLI (`cortex`) for activation, validation, TUI workflows, diagnostics, and exports
- Built-in support for MCP docs, memory capture, and review gates

## Feature Highlights

### Original Cortex Skills

Cortex includes four foundational skills that drive quality across development workflows:

#### `agent-loops` — Structured Implementation & Verification
- **Skill file**: `skills/agent-loops/SKILL.md`
- **Purpose**: Multi-phase implementation loop with built-in verification and code review gates
- **When to use**: Any feature implementation, bug fix, or refactoring task
- **Workflow**: Plan → Implement → Verify → Review approval before committing
- **CLI integration**: Complements `cortex review` command:

```bash
cortex review --dry-run                    # Preview review gates
cortex review -c feature -c debug          # Full review workflow
```

#### `test-review` — Quality Assurance & Coverage Analysis
- **Skill file**: `skills/test-review/SKILL.md`
- **Purpose**: Audit test quality and coverage across modules
- **When to use**: After test suite changes, coverage gaps, or brittle tests
- **Features**: Identifies gaps, suggests improvements, validates test patterns

#### `doc-claim-validator` — Documentation Accuracy Auditing
- **Skill file**: `skills/doc-claim-validator/SKILL.md`
- **Purpose**: Validates that documentation claims match codebase reality
- **When to use**: Before releases, after major refactors, periodic audits
- **Features**: Extracts verifiable assertions (file paths, code patterns), checks against actual code

#### `doc-maintenance` — Documentation Lifecycle Management
- **Skill file**: `skills/doc-maintenance/SKILL.md`
- **Purpose**: Systematic documentation audit and maintenance
- **When to use**: Documentation may be stale, outdated references, inconsistent structure
- **Features**: Identifies orphaned docs, updates cross-references, improves navigation

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

### Using Original Cortex Skills

**Feature implementation with `agent-loops`:**
```bash
# Start implementation with built-in verification gates
cortex review --dry-run                    # Preview what will be reviewed
cortex review -c feature -c debug          # Run full review workflow
```

**Quality assurance with `test-review`:**
```bash
# Audit test quality and identify coverage gaps
cortex skills info test-review             # View skill details
# Then invoke: /test-review in Claude Code to audit your test suite
```

**Documentation accuracy with `doc-claim-validator`:**
```bash
# Validate documentation matches codebase reality
cortex skills info doc-claim-validator     # View skill details
# Then invoke: /doc-claim-validator in Claude Code to audit docs
```

**Documentation maintenance with `doc-maintenance`:**
```bash
# Perform systematic documentation audit
cortex skills info doc-maintenance         # View skill details
# Then invoke: /doc-maintenance in Claude Code for maintenance workflow
```

### Agent + skill management

```bash
cortex agent list
cortex agent status
cortex skills list
cortex skills feedback agent-loops helpful --comment "High signal loop guidance"
cortex skills rate agent-loops --stars 5 --review "Reliable workflow"
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
