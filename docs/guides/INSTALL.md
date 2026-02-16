# Installation & Usage Guide

## Quick Install

### Recommended: pipx

```bash
# Install the package
pipx install claude-cortex

# Link cortex content to ~/.claude
cortex install link

# Optional: Install shell completions and manpages
cortex install post
```

### Alternative: uv

```bash
uv tool install claude-cortex
cortex install link
cortex install post  # optional
```

### Alternative: pip

```bash
pip install claude-cortex
cortex install link
cortex install post  # optional
```

## Development Install

### Editable Install (Recommended for Development)

```bash
git clone https://github.com/NickCrew/claude-cortex.git
cd claude-cortex
pip install -e ".[dev]"

# Link content (creates symlinks for agents, skills, rules, hooks)
cortex install link

# Optional: Install shell completions and manpages
cortex install post
```

### Standard Install from Source

```bash
git clone https://github.com/NickCrew/claude-cortex.git
cd claude-cortex
pipx install .

cortex install link
cortex install post  # optional
```

## What Gets Installed

The `cortex install link` command creates symlinks in `~/.claude/`:

```
~/.claude/
├── agents/        → symlink to package agents/
├── skills/        → symlink to package skills/
├── rules/         → symlink to package rules/
├── hooks/         → symlink to package hooks/
└── commands/      → generated (skill command aliases)
```

**Preview changes before linking:**
```bash
cortex install link --dry-run
```

**Force replace existing directories:**
```bash
cortex install link --force
```

## Shell Integrations

The `cortex install post` command installs:

- **Shell completions** (bash, zsh, fish)
- **Manpages** (`cortex.1`, `cortex-tui.1`)
- **Architecture docs** (in system share directory)

**Options:**
```bash
# Specify shell explicitly
cortex install post --shell zsh

# Use system paths
cortex install post --system

# Preview without installing
cortex install post --dry-run
```

## Usage

### TUI (Terminal User Interface)

Launch the interactive TUI:

```bash
cortex tui
```

**Primary Views:**
- `1` - Overview (system summary)
- `2` - Agents (manage agents)
- `3` - Modes (behavioral modes)
- `4` - Rules (rule modules)
- `5` - Skills (local + community skills)
- `6` - Workflows (workflow management)
- `7` - MCP Servers (MCP management)
- `M` - Memory Vault (knowledge graph)

**Navigation:**
- `Tab` - Cycle through views
- `/` - Command palette
- `?` - Help
- `q` - Quit

### Launch Claude Code with Cortex

```bash
cortex start
```

The launcher uses `~/.claude/` for rules, agents, skills, and hooks.

**Pass additional Claude arguments:**
```bash
cortex start -- --model sonnet
```

**Override Claude binary:**
```bash
cortex start --claude-bin /custom/path/to/claude
```

## Managing Rules

Once linked, you can manage which rules are active:

```bash
# List available rules
cortex rules list

# Show active rules
cortex rules status

# Activate/deactivate specific rules
cortex rules activate <rule-name>
cortex rules deactivate <rule-name>

# Edit a rule
cortex rules edit <rule-name>
```

## Managing Skills

```bash
# List available skills
cortex skills list

# Get skill information
cortex skills info <skill-name>

# Validate skill structure
cortex skills validate <skill-name>

# View skill dependencies
cortex skills deps <skill-name>

# View skill metrics
cortex skills metrics
```

## Uninstalling

```bash
# Preview what would be removed
cortex uninstall --dry-run

# Uninstall (keeps config files)
cortex uninstall

# Uninstall including config
cortex uninstall --keep-config=false

# Remove the package
pipx uninstall claude-cortex
```

## Troubleshooting

### Commands not found after install

If `cortex` command is not found, ensure pipx/uv bin directory is in your PATH:

```bash
# For pipx
pipx ensurepath

# For uv
export PATH="$HOME/.local/bin:$PATH"
```

### Symlinks not created

If `cortex install link` fails, check permissions:

```bash
# Ensure ~/.claude is writable
ls -la ~/.claude

# Try with force flag
cortex install link --force
```

### Completions not working

Restart your shell after installing completions:

```bash
exec $SHELL
```

## Getting Help

```bash
# General help
cortex --help

# Command-specific help
cortex install --help
cortex skills --help
cortex tui --help
```

For more documentation, see:
- [Skills Guide](skills.md)
- [TUI Guide](tui.md)
- [Hooks Reference](hooks.md)
