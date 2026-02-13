# Installation Test Plan

Manual verification steps for testing the `claude-cortex` package installation.

## Prerequisites

- Python 3.9+
- pipx, uv, or pip installed
- Claude Code CLI installed (`claude` command available)

---

## Test 1: Fresh Package Install

**Purpose**: Verify package installs correctly from PyPI.

### Steps

```bash
# Clean any existing installation
pipx uninstall claude-cortex 2>/dev/null || true

# Install from PyPI
pipx install claude-cortex

# Verify installation
cortex --version
cortex --help
```

### Expected Results

- [ ] `pipx install` completes without errors
- [ ] `cortex --version` shows version (e.g., `2.3.1`)
- [ ] `cortex --help` displays help with subcommands

---

## Test 2: Bootstrap Command

**Purpose**: Verify `cortex install bootstrap` creates ~/.cortex correctly.

### Steps

```bash
# Remove existing ~/.cortex (backup first if needed)
mv ~/.cortex ~/.cortex.backup 2>/dev/null || true

# Run bootstrap (dry-run first)
cortex install bootstrap --dry-run

# Run bootstrap
cortex install bootstrap

# Verify structure
ls -la ~/.cortex/
ls ~/.cortex/rules/
ls ~/.cortex/flags/
ls ~/.cortex/modes/
cat ~/.cortex/cortex-config.json
```

### Expected Results

- [ ] Dry-run shows what would be created
- [ ] Bootstrap creates `~/.cortex/` directory
- [ ] `rules/` contains 6 markdown files
- [ ] `flags/` contains 22 markdown files
- [ ] `modes/` contains 10 markdown files
- [ ] `templates/` directory exists with contents
- [ ] `cortex-config.json` exists with valid JSON
- [ ] `FLAGS.md` exists

### Verify Config Contents

```bash
# Should contain these keys
cat ~/.cortex/cortex-config.json | python3 -m json.tool
```

Expected keys:
- `plugin_id`: "cortex"
- `rules`: array of rule names
- `flags`: array (may be empty)
- `modes`: array (may be empty)
- `principles`: array of principle names
- `claude_args`: array (may be empty)
- `extra_plugin_dirs`: array (may be empty)

---

## Test 3: Bootstrap with Custom Target

**Purpose**: Verify bootstrap works with alternate paths.

### Steps

```bash
# Bootstrap to custom location
cortex install bootstrap --target /tmp/test-cortex

# Verify
ls -la /tmp/test-cortex/
cat /tmp/test-cortex/cortex-config.json

# Clean up
rm -rf /tmp/test-cortex
```

### Expected Results

- [ ] Creates directory at custom path
- [ ] Contains same structure as ~/.cortex
- [ ] Config file is valid JSON

---

## Test 4: Bootstrap --force (Reinitialize)

**Purpose**: Verify --force overwrites existing installation.

### Steps

```bash
# Modify a file
echo "# Modified" >> ~/.cortex/rules/git-rules.md

# Run bootstrap with --force
cortex install bootstrap --force

# Verify file was reset
head -5 ~/.cortex/rules/git-rules.md
```

### Expected Results

- [ ] --force overwrites existing directories
- [ ] Modified file is replaced with original

---

## Test 5: Post-Install (Shell Integrations)

**Purpose**: Verify shell completions and manpages install.

### Steps

```bash
# Dry-run first
cortex install post --dry-run

# Install
cortex install post

# Test manpage
man cortex 2>/dev/null || echo "Manpage not in MANPATH"

# Test completions (varies by shell)
# For zsh:
ls ~/.zsh/completions/_cortex 2>/dev/null || echo "Completion not found"
```

### Expected Results

- [ ] Dry-run shows what would be installed
- [ ] Completions file created for detected shell
- [ ] Manpages installed (may need MANPATH update)

---

## Test 6: Cortex Start (Full Integration)

**Purpose**: Verify `cortex start` launches Claude Code with Cortex context.

### Steps

```bash
# Ensure Claude Code is installed
which claude

# Start with verbose output
cortex start --help

# Dry-run equivalent: check what would be passed
# (cortex start doesn't have --dry-run, so we inspect config)
cat ~/.cortex/cortex-config.json

# Actually launch (will open Claude Code)
cortex start
```

### Expected Results

- [ ] `cortex start --help` shows available options
- [ ] Claude Code launches successfully
- [ ] Plugin is loaded (check Claude's status)
- [ ] Rules are symlinked to `~/.claude/rules/cortex/`

### Verify Rules Symlink

```bash
ls -la ~/.claude/rules/cortex/
```

Should show symlinks pointing to `~/.cortex/rules/*.md`

---

## Test 7: TUI Launch

**Purpose**: Verify TUI starts correctly.

### Steps

```bash
# Launch TUI
cortex tui

# Or via cortex-ui alias
cortex-ui
```

### Expected Results

- [ ] TUI launches without errors
- [ ] Main screen displays
- [ ] Can navigate with keyboard
- [ ] Press `q` to quit cleanly

---

## Test 8: Asset Detection from Package

**Purpose**: Verify bundled assets are found when not in dev mode.

### Steps

```bash
# Check asset resolution
python3 -c "
from claude_ctx_py.core.base import _resolve_bundled_assets_root
root = _resolve_bundled_assets_root()
print(f'Assets root: {root}')
print(f'Exists: {root.exists() if root else False}')
if root:
    print(f'Contents: {list(root.iterdir())[:5]}...')
"
```

### Expected Results

- [ ] Assets root is found
- [ ] Path exists
- [ ] Contains expected directories (agents, commands, skills, etc.)

---

## Test 9: Environment Variable Override

**Purpose**: Verify CORTEX_ROOT environment variable works.

### Steps

```bash
# Bootstrap to alternate location
cortex install bootstrap --target /tmp/alt-cortex

# Use alternate root
CORTEX_ROOT=/tmp/alt-cortex cortex status

# Clean up
rm -rf /tmp/alt-cortex
```

### Expected Results

- [ ] Commands use alternate CORTEX_ROOT
- [ ] Config is read from alternate location

---

## Test 10: Upgrade Path

**Purpose**: Verify upgrading preserves user config.

### Steps

```bash
# Add custom setting to config
cat ~/.cortex/cortex-config.json | \
  python3 -c "import sys,json; d=json.load(sys.stdin); d['custom_setting']='test'; print(json.dumps(d,indent=2))" \
  > /tmp/config.json && mv /tmp/config.json ~/.cortex/cortex-config.json

# Upgrade package
pipx upgrade claude-cortex

# Verify custom setting preserved
cat ~/.cortex/cortex-config.json | grep custom_setting
```

### Expected Results

- [ ] Upgrade completes successfully
- [ ] Custom config settings are preserved
- [ ] Bootstrap does NOT overwrite existing config (without --force)

---

## Troubleshooting

### Assets Not Found

```bash
# Check if assets are in package
python3 -c "
import claude_ctx_py
from pathlib import Path
pkg = Path(claude_ctx_py.__file__).parent
assets = pkg / 'assets'
print(f'Package: {pkg}')
print(f'Assets exists: {assets.exists()}')
if assets.exists():
    print(f'Assets contents: {list(assets.iterdir())}')
"
```

### Bootstrap Fails

```bash
# Check permissions
ls -la ~/.cortex 2>/dev/null || echo "~/.cortex doesn't exist"
ls -la ~ | grep -E "^d.* \\.cortex"

# Try with verbose
cortex install bootstrap --dry-run
```

### Claude Code Not Found

```bash
# Verify claude is in PATH
which claude
claude --version

# Check if cortex can find it
cortex start --claude-bin $(which claude)
```

---

## Quick Verification Script

Save as `test-install.sh`:

```bash
#!/bin/bash
set -e

echo "=== Testing cortex installation ==="

echo -n "1. Version check: "
cortex --version

echo -n "2. Bootstrap dry-run: "
cortex install bootstrap --target /tmp/cortex-test --dry-run | head -1

echo "3. Bootstrap actual: "
cortex install bootstrap --target /tmp/cortex-test
ls /tmp/cortex-test/

echo "4. Config validation: "
python3 -m json.tool /tmp/cortex-test/cortex-config.json > /dev/null && echo "Valid JSON"

echo "5. Asset detection: "
python3 -c "from claude_ctx_py.core.base import _resolve_bundled_assets_root; print(_resolve_bundled_assets_root())"

echo "6. Cleanup: "
rm -rf /tmp/cortex-test

echo "=== All tests passed ==="
```

Run with: `bash test-install.sh`
