# AGENTS.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build, Test, and Development Commands

```bash
# Installation
just install           # Full installation via legacy scripts
pip install -e ".[dev]" # Development install with extras

# Testing
just test              # Run pytest suite
just test-cov          # Run with coverage (output: htmlcov/)
pytest -m unit         # Unit tests only
pytest -m integration  # Integration tests only
pytest tests/unit/test_composer.py::TestComposer::test_specific  # Single test

# Code Quality
just lint              # Check formatting with Black
just lint-fix          # Auto-format with Black
just type-check        # Strict mypy on core modules
just type-check-all    # Full mypy (informational)
python3 -m mypy --strict claude_ctx_py  # Direct strict check

# Build & Docs
python -m build        # Build sdist/wheel
just docs              # Serve docs locally (requires Ruby/bundler)
just docs-build        # Build static docs
```

## Architecture Overview

### Core Module Organization (`claude_ctx_py/`)

The Python package follows a domain-driven architecture:

```
claude_ctx_py/
├── cli.py              # Main CLI entrypoint (argparse-based)
├── core/               # Domain modules re-exported via __init__.py
│   ├── base.py         # Utilities, path resolution, YAML/front-matter parsing
│   ├── agents.py       # Agent graph, dependencies, activation
│   ├── skills.py       # Skill discovery, metrics, community integration
│   ├── rules.py        # Rule management
│   ├── hooks.py        # Hook installation and validation
│   ├── mcp.py          # MCP server discovery and configuration
│   ├── mcp_installer.py # MCP server installation
│   ├── mcp_registry.py # MCP server registry
│   ├── worktrees.py    # Git worktree management
│   ├── backup.py       # Configuration backup/restore
│   ├── components.py   # Shared component utilities
│   ├── asset_discovery.py # Asset discovery across scopes
│   ├── asset_installer.py # Asset installation (symlinks)
│   ├── codex_skills.py # Codex skill integration
│   └── context_export.py # Context export functionality
├── tui/                # Textual-based terminal UI
│   ├── main.py         # CortexApp (main application class)
│   ├── types.py        # TypedDicts for TUI data structures
│   ├── constants.py    # View bindings, profile descriptions
│   ├── dialogs/        # Modal dialogs (backup, profile editor, LLM settings)
│   └── widgets.py      # Custom Textual widgets
├── intelligence/       # AI-powered automation
│   ├── base.py         # SessionContext, AgentRecommendation dataclasses
│   ├── semantic.py     # Semantic matching (fastembed integration)
│   └── config.py       # Intelligence configuration
└── memory/             # Memory and context capture
    ├── capture.py      # Session capture
    ├── search.py       # Memory search
    └── notes.py        # Memory note management
```

### Plugin Assets Structure

The repository ships these asset directories that are symlinked into `~/.claude`:

```
agents/         # Claude subagent definitions (YAML front matter + markdown)
commands/       # Slash command definitions
rules/          # Reusable rule sets
skills/         # Core and community skills (127+)
hooks/          # Automation hooks for command workflows
```

### Key Architectural Patterns

**Path Resolution Chain**: The CLI resolves its data folder in order:
1. `CORTEX_SCOPE` (project/global/plugin)
2. `CLAUDE_PLUGIN_ROOT` (set by Claude Code for plugin commands)
3. `CORTEX_ROOT` (default: `~/.cortex`)

**State Management**: Active assets tracked via `.active-*` state files (e.g., `.active-agents`, `.active-rules`), not CLAUDE.md comments.

**Front Matter Parsing**: Agent/skill metadata extracted from YAML front matter in markdown files via `_tokenize_front_matter()` and `_extract_front_matter()`.

**TUI Views**: The TUI uses Textual's `ContentSwitcher` with view IDs (0-9, plus named keys) for different screens (Overview, Agents, Skills, Rules, etc.). Each view has its own data refresh and action bindings.

## Type Checking

Mypy is configured with `--strict` in `pyproject.toml`. New modules should:

- Prefer `TypedDict`/`Protocol` over raw `dict`/`Any`
- Use explicit type annotations for Textual widget state
- Check `/tmp/mypy.log` for CI failure output when iterating locally

## Coding Style & Naming Conventions

- Python uses Black (line length 88) and type hints; mypy is configured in `pyproject.toml`.
- YAML uses 2-space indentation and consistent key ordering.
- Markdown uses ATX headers and fenced code blocks with language tags.
- File/dir naming is lowercase hyphen-case (e.g., `skills/my-skill/`, `rules/git-rules.md`).

## Testing Guidelines

- Framework: pytest with markers like `unit`, `integration`, and `slow`.
- Conventions: `test_*.py` files, `Test*` classes, `test_*` functions.
- Run subsets: `pytest -m unit`, `pytest tests/integration/`, or `pytest tests/unit/test_composer.py`.
- Coverage target is 80% long term; minimums are enforced via `pyproject.toml`.

## Testing Conventions

- Markers: `unit`, `integration`, `slow`, `tui`, `cli`, `core`, `intelligence`
- Test files: `test_*.py`, classes: `Test*`, functions: `test_*`
- Coverage target: 80% (current minimum enforced: 15%)

## Commit & Pull Request Guidelines

- Recent commits use lowercase type prefixes like `feat:`, `fix:`, `docs:`, `chore:`, `test:` with optional scopes (`feat(agents):`).
- PR titles follow `[Feature] ...`, `[Fix] ...`, `[Docs] ...`; include summary, testing notes, checklist, related issues, and screenshots for UI changes.

## Local Configuration Tips

- Point the CLI to this repo for local testing: `export CLAUDE_PLUGIN_ROOT="$(pwd)"`.
- Avoid committing generated `.active-*` state files from local runs.

## Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   bd sync
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds

