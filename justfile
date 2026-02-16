
help:
    @echo "Cortex Development Justfile"
    @echo ""
    @echo "Available recipes:"
    @echo "  just install              # Install package in editable mode"
    @echo "  just install-link         # Link cortex content to ~/.claude"
    @echo "  just install-completions  # Install shell completions"
    @echo "  just install-manpage      # Install manpages"
    @echo "  just install-post         # Install completions and manpages"
    @echo "  just generate-manpages    # Generate manpages from CLI definitions"
    @echo "  just update-completions   # Update completion scripts"
    @echo "  just uninstall            # Uninstall cortex package and content"
    @echo "  just test                 # Run full test suite"
    @echo "  just test-unit            # Run unit tests only"
    @echo "  just test-integration     # Run integration tests only"
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
    @echo "  just docs-sync            # Sync docs into bundled directory"
    @echo "  just build                # Build sdist/wheel with python -m build"
    @echo "  just publish              # Build and publish to PyPI via twine"
    @echo "  just verify               # Verify CLI, manpage, and dependencies"
    @echo "  just bundle-assets        # Sync bundled assets into claude_ctx_py/assets"
    @echo ""
    @echo "Examples:"
    @echo "  just install         # Install in editable mode"
    @echo "  just install-link    # Link content to ~/.claude"
    @echo "  just test-cov        # Run tests with coverage"
    @echo "  just type-check      # Check types with mypy"

# Install package in editable mode
install:
    @pip install -e ".[dev]"
    @echo "✓ Installed claude-cortex in editable mode"

# Link cortex content to ~/.claude
install-link:
    @cortex install link
    @echo "✓ Linked content to ~/.claude"

# Generate manpages from CLI
generate-manpages:
    @cortex dev manpages
    @echo "✓ Manpages generated"

regen-manpages: generate-manpages

# Update shell completions
update-completions:
    @cortex install completions --force
    @echo "✓ Completions updated"

# Install manpages
install-manpage: generate-manpages
    @cortex install manpage
    @echo "✓ Manpages installed"

# Install shell completions
install-completions:
    @cortex install completions --force
    @echo "✓ Completions installed"

# Install completions and manpages
install-post:
    @cortex install post
    @echo "✓ Post-install complete"

# Uninstall package and content
uninstall:
    @cortex uninstall --dry-run
    @echo ""
    @read -p "Continue with uninstall? (y/N) " confirm && [ "$$confirm" = "y" ] || exit 1
    @cortex uninstall
    @pip uninstall -y claude-cortex
    @echo "✓ Uninstalled"

# Run full test suite
test:
    @pytest

# Run unit tests only
test-unit:
    @pytest tests/unit -v

# Run integration tests
test-integration:
    @pytest tests/integration -v

# Run tests with coverage
test-cov:
    @pytest --cov=claude_ctx_py --cov-report=term-missing --cov-report=html
    @echo ""
    @echo "Coverage report: htmlcov/index.html"

# Check code formatting
lint:
    @black --check claude_ctx_py/
    @echo "✓ Code formatting looks good"

# Auto-format code
lint-fix:
    @black claude_ctx_py/
    @echo "✓ Code formatted"

# Type check focused modules
type-check:
    @echo "Checking Phase 4 modules (strict)..."
    @mypy claude_ctx_py/activator.py claude_ctx_py/composer.py claude_ctx_py/metrics.py \
        claude_ctx_py/analytics.py claude_ctx_py/community.py claude_ctx_py/versioner.py \
        claude_ctx_py/exceptions.py claude_ctx_py/error_utils.py
    @echo "✓ Type checking passed"

# Type check all modules
type-check-all:
    @echo "Checking all modules (informational)..."
    @mypy claude_ctx_py/ || true

# Clean build artifacts
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

# Sync bundled assets
bundle-assets:
    @python3 ./scripts/sync_bundled_assets.py
    @just docs-sync

# Build distribution packages
build: bundle-assets
    @python -m build

# Publish to PyPI
publish:
    @python -m build
    @python -m twine upload dist/*

# Serve docs with livereload
docs:
    @cd docs && bundle exec jekyll serve --livereload

# Serve docs (custom domain config)
docs-serve:
    @cd docs && bundle exec jekyll serve --livereload --config _config.yml

# Serve docs (GitHub Pages config)
docs-serve-gh:
    @cd docs && bundle exec jekyll serve --livereload --config _config.yml,_config_ghpages.yml

# Build docs site
docs-build:
    @cd docs && bundle exec jekyll build --config _config.yml -d _site

# Build docs (GitHub Pages)
docs-build-gh:
    @cd docs && bundle exec jekyll build --config _config.yml,_config_ghpages.yml -d _site

# Sync docs to bundle directory
docs-sync:
    @mkdir -p claude_ctx_py/docs
    @cp README.md CHANGELOG.md CREDITS.md claude_ctx_py/docs/
    @rsync -av --exclude='vendor' --exclude='_site' --exclude='.bundle' --exclude='.jekyll-cache' docs/ claude_ctx_py/docs/
    @echo "✓ Documentation synced to claude_ctx_py/docs/"

# Verify installation
verify:
    @echo "=== Verifying Installation ==="
    @command -v cortex >/dev/null 2>&1 && echo "✓ cortex command found" || echo "✗ cortex not found"
    @man -w cortex >/dev/null 2>&1 && echo "✓ manpage installed" || echo "✗ manpage not found"
    @python3 -c "import argcomplete" 2>/dev/null && echo "✓ argcomplete available" || echo "✗ argcomplete not found"
    @echo ""
    @echo "Cortex version:"
    @cortex --version || true
