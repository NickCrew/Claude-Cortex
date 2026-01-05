# Repository Guidelines

## Project Structure & Module Organization
- `claude_ctx_py/` houses the Python CLI/TUI implementation.
- `commands/`, `agents/`, `modes/`, `rules/`, `flags/` contain plugin assets and reusable context modules.
- `skills/` holds core and community skills (see `skills/community/` for templates).
- `profiles/`, `scenarios/`, `workflows/` define orchestration presets for common workstreams.
- `tests/` contains the pytest suite (`unit/`, `integration/`).
- `docs/` is the Jekyll documentation site; `schema/` and `scripts/` support validation and automation.

## Build, Test, and Development Commands
- `just install` / `just install-dev`: install the CLI/TUI and development dependencies.
- `just test` / `just test-cov`: run pytest; coverage output goes to `htmlcov/`.
- `just lint` / `just lint-fix`: run Black checks or reformat Python code.
- `just type-check`: run focused strict mypy checks for core modules.
- `python -m build`: build sdist and wheel artifacts.
- `just docs`: serve docs locally with Jekyll (Ruby/bundler required).
- `cortex tui` or `cortex`: run the local CLI/TUI after installation.

## Coding Style & Naming Conventions
- Python uses Black (line length 88) and type hints; mypy is configured in `pyproject.toml`.
- YAML uses 2-space indentation and consistent key ordering.
- Markdown uses ATX headers and fenced code blocks with language tags.
- File/dir naming is lowercase hyphen-case (e.g., `skills/my-skill/`, `modes/super-saiyan.md`).

## Testing Guidelines
- Framework: pytest with markers like `unit`, `integration`, and `slow`.
- Conventions: `test_*.py` files, `Test*` classes, `test_*` functions.
- Run subsets: `pytest -m unit`, `pytest tests/integration/`, or `pytest tests/unit/test_composer.py`.
- Coverage target is 80% long term; minimums are enforced via `pyproject.toml`.

## Commit & Pull Request Guidelines
- Recent commits use lowercase type prefixes like `feat:`, `fix:`, `docs:`, `chore:`, `test:` with optional scopes (`feat(agents):`).
- PR titles follow `[Feature] ...`, `[Fix] ...`, `[Docs] ...`; include summary, testing notes, checklist, related issues, and screenshots for UI changes.

## Local Configuration Tips
- Point the CLI to this repo for local testing: `export CLAUDE_PLUGIN_ROOT="$(pwd)"`.
- Avoid committing generated `.active-*` state files from local runs.
