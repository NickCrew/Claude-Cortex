set shell := ["bash", "-lc"]

default := ["help"]

help:
    @echo "Claude-ctx Development Justfile"
    @echo ""
    @echo "Available recipes:"
    @echo "  just install              # Install package, completions, and manpage"
    @echo "  just install-dev          # Install in development mode with all dependencies"
    @echo "  just install-manpage      # Install manpage only"
    @echo "  just install-completions  # Install shell completions only"
    @echo "  just uninstall            # Uninstall claude-ctx (manual cleanup may remain)"
    @echo "  just test                 # Run test suite"
    @echo "  just test-cov             # Run tests with coverage report"
    @echo "  just lint                 # Run code format checks"
    @echo "  just type-check           # Run focused mypy type checking"
    @echo "  just type-check-all       # Run mypy over entire module tree"
    @echo "  just clean                # Remove build artifacts and caches"
    @echo "  just docs                 # Build documentation site"
    @echo "  just build                # Build sdist/wheel with python -m build"
    @echo "  just publish              # Build and publish to PyPI via twine"
    @echo "  just verify               # Verify CLI, manpage, and dependencies"
    @echo ""
    @echo "Examples:"
    @echo "  just install         # Full installation"
    @echo "  just test-cov        # Run tests with coverage"
    @echo "  just type-check      # Check types with mypy"

install:
    @./scripts/install.sh

install-dev:
    @./scripts/install.sh

generate-manpages:
    @python3 ./scripts/generate-manpages.py

install-manpage: generate-manpages
    @./scripts/install-manpage.sh

install-completions:
    @./scripts/install.sh --no-package --no-manpage

uninstall:
    @pip uninstall -y claude-ctx-py
    @echo "Note: Manpage and completions must be removed manually"
    @echo "  Manpage: sudo rm /usr/local/share/man/man1/claude-ctx.1"
    @echo "  Bash: rm ~/.local/share/bash-completion/completions/claude-ctx"
    @echo "  Zsh: rm ~/.local/share/zsh/site-functions/_claude-ctx"
    @echo "  Fish: rm ~/.config/fish/completions/claude-ctx.fish"

test:
    @.venv/bin/pytest

test-cov:
    @.venv/bin/pytest --cov=claude_ctx_py --cov-report=term-missing --cov-report=html
    @echo ""
    @echo "Coverage report: htmlcov/index.html"

lint:
    @black --check claude_ctx_py/
    @echo "✓ Code formatting looks good"

lint-fix:
    @black claude_ctx_py/
    @echo "✓ Code formatted"

type-check:
    @echo "Checking Phase 4 modules (strict)..."
    @mypy claude_ctx_py/activator.py claude_ctx_py/composer.py claude_ctx_py/metrics.py \
        claude_ctx_py/analytics.py claude_ctx_py/community.py claude_ctx_py/versioner.py \
        claude_ctx_py/exceptions.py claude_ctx_py/error_utils.py
    @echo "✓ Type checking passed"

type-check-all:
    @echo "Checking all modules (informational)..."
    @mypy claude_ctx_py/ || true

clean:
    @rm -rf build/
    @rm -rf dist/
    @rm -rf *.egg-info
    @rm -rf .pytest_cache/
    @rm -rf .mypy_cache/
    @rm -rf htmlcov/
    @rm -rf .coverage
    @find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    @find . -type f -name "*.pyc" -delete
    @echo "✓ Cleaned build artifacts"

build:
    @python -m build

publish:
    @python -m build
    @python -m twine upload dist/*

docs:
    @cd docs && bundle exec jekyll serve --livereload

verify:
    @echo "=== Verifying Installation ==="
    @command -v claude-ctx >/dev/null 2>&1 && echo "✓ claude-ctx command found" || echo "✗ claude-ctx not found"
    @man -w claude-ctx >/dev/null 2>&1 && echo "✓ manpage installed" || echo "✗ manpage not found"
    @python3 -c "import argcomplete" 2>/dev/null && echo "✓ argcomplete available" || echo "✗ argcomplete not found"
    @echo ""
    @echo "Claude-ctx version:"
    @claude-ctx --help | head -1 || true
