

help:
    @echo "Cortex Development Justfile"
    @echo ""
    @echo "Available recipes:"
    @echo "  just install              # Legacy installer (deprecated)"
    @echo "  just install-dev          # Legacy installer with dev deps (deprecated)"
    @echo "  just install-manpage      # Legacy manpage install (deprecated)"
    @echo "  just install-completions  # Legacy completions install (deprecated)"
    @echo "  just generate-manpages    # Generate manpages from CLI definitions"
    @echo "  just regen-manpages       # Re-generate manpages from CLI definitions"
    @echo "  just update-completions   # Update cortex/cortex completion scripts"
    @echo "  just uninstall            # Uninstall cortex (manual cleanup may remain)"
    @echo "  just test                 # Run test suite"
    @echo "  just test-cov             # Run tests with coverage report"
    @echo "  just lint                 # Run code format checks"
    @echo "  just lint-fix             # Auto-format code with black"
    @echo "  just type-check           # Run focused mypy type checking"
    @echo "  just type-check-all       # Run mypy over entire module tree"
    @echo "  just clean                # Remove build artifacts and caches"
    @echo "  just docs                 # Build documentation site"
    @echo "  just docs-serve           # Serve docs (custom domain config)"
    @echo "  just docs-serve-gh        # Serve docs with GitHub Pages config"
    @echo "  just docs-build           # Build docs site to docs/_site"
    @echo "  just docs-build-gh        # Build docs with GitHub Pages config"
    @echo "  just build                # Build sdist/wheel with python -m build"
    @echo "  just publish              # Build and publish to PyPI via twine"
    @echo "  just verify               # Verify CLI, manpage, and dependencies"
    @echo "  just bundle-assets        # Sync bundled assets into claude_ctx_py/assets"
    @echo ""
    @echo "Examples:"
    @echo "  just install         # Full installation"
    @echo "  just test-cov        # Run tests with coverage"
    @echo "  just type-check      # Check types with mypy"

install:
    @./scripts/deprecated/install.sh

install-dev:
    @./scripts/deprecated/install.sh

generate-manpages:
    @python3 ./scripts/generate-manpages.py

regen-manpages: generate-manpages

update-completions: install-completions

install-manpage: generate-manpages
    @./scripts/deprecated/install-manpage.sh

install-completions:
    @./scripts/deprecated/install.sh --no-package --no-manpage

uninstall:
    @pip uninstall -y cortex-py
    @echo "Note: Manpage and completions must be removed manually"
    @echo "  Manpage: sudo rm /usr/local/share/man/man1/cortex.1"
    @echo "  Bash: rm ~/.local/share/bash-completion/completions/cortex"
    @echo "  Zsh: rm ~/.local/share/zsh/site-functions/_cortex"
    @echo "  Fish: rm ~/.config/fish/completions/cortex.fish"

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

bundle-assets:
    @python3 ./scripts/sync_bundled_assets.py

build:
    @python -m build

publish:
    @python -m build
    @python -m twine upload dist/*

docs:
    @cd docs && bundle exec jekyll serve --livereload

docs-serve:
    @cd docs && bundle exec jekyll serve --livereload --config _config.yml

docs-serve-gh:
    @cd docs && bundle exec jekyll serve --livereload --config _config.yml,_config_ghpages.yml

docs-build:
    @cd docs && bundle exec jekyll build --config _config.yml -d _site

docs-build-gh:
    @cd docs && bundle exec jekyll build --config _config.yml,_config_ghpages.yml -d _site

verify:
    @echo "=== Verifying Installation ==="
    @command -v cortex >/dev/null 2>&1 && echo "✓ cortex command found" || echo "✗ cortex not found"
    @man -w cortex >/dev/null 2>&1 && echo "✓ manpage installed" || echo "✗ manpage not found"
    @python3 -c "import argcomplete" 2>/dev/null && echo "✓ argcomplete available" || echo "✗ argcomplete not found"
    @echo ""
    @echo "Cortex version:"
    @cortex --help | head -1 || true
