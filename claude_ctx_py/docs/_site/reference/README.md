# Manpage Generation

Manpages for `claude-ctx` are **auto-generated** from the CLI argparse definitions.

## 📄 Generated Files

- `claude-ctx.1` - Main command reference
- `claude-ctx-tui.1` - TUI subcommand reference  
- `claude-ctx-workflow.1` - Workflow subcommand reference

## 🔄 Regeneration

Manpages are automatically regenerated:

1. **During installation** - `make install` or `./scripts/deprecated/install.sh`
2. **Manual generation** - `make generate-manpages` or `python3 scripts/generate-manpages.py`
3. **Pre-commit hook** - When `claude_ctx_py/cli.py` is modified (optional)

## 🔧 Setup Pre-commit Hook

To automatically regenerate manpages when CLI changes:

```bash
git config core.hooksPath .githooks
```

## 📝 Editing

**Do NOT manually edit the `.1` files** - they will be overwritten.

Instead:
1. Update CLI help text in `claude_ctx_py/cli.py`
2. Modify the generator in `scripts/generate-manpages.py`
3. Run `make generate-manpages` to regenerate

## 🧪 Testing

View generated manpages:

```bash
# After generation
man docs/reference/claude-ctx.1

# After installation
man claude-ctx
```

## 📅 Version & Date

- **Version**: Extracted from `pyproject.toml`
- **Date**: Set to generation date (YYYY-MM-DD format)
