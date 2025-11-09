# Installation & Usage Guide

## Installation

### Option 1: Install from source (recommended for development)

```bash
cd ~/Developer/personal/claude-ctx-plugin
pipx install -e .
```

This installs the package in editable mode, so any changes you make to the code will be immediately available.

### Option 2: Install from source (standard)

```bash
cd ~/Developer/personal/claude-ctx-plugin
pipx install .
```

Standard installation. You'll need to reinstall after making code changes:

```bash
pipx reinstall claude-ctx-py
```

### Option 3: Uninstall and reinstall

If you need to completely remove and reinstall:

```bash
pipx uninstall claude-ctx-py
pipx install ~/Developer/personal/claude-ctx-plugin
```

## Usage

### TUI (Terminal User Interface)

Launch the interactive TUI:

```bash
claude-ctx tui
```

#### TUI Navigation

**View Switching:**
- `1` - Overview (system summary)
- `2` - Agents (manage agents)
- `3` - Modes (behavioral modes)
- `4` - Rules (rule modules)
- `5` - Skills (local + community skills)
- `6` - Workflows (workflow management)
- `7` - Orchestrate (parallel execution monitoring)
- `8` - Profile (quick profile switching)
- `9` - Export (context export)

**Navigation:**
- `↑/k` - Move up
- `↓/j` - Move down
- `Space` - Toggle active/inactive
- `Enter` - Show details
- `/` - Filter/search
- `Esc` - Clear filter
- `?` - Help
- `q` - Quit

### CLI Commands

#### Agents
```bash
claude-ctx agent list                    # List all agents
claude-ctx agent activate <name>         # Activate agent
claude-ctx agent deactivate <name>       # Deactivate agent
claude-ctx agent info <name>             # Show agent details
```

#### Modes
```bash
claude-ctx mode list                     # List all modes
claude-ctx mode activate <name>          # Activate mode
claude-ctx mode deactivate <name>        # Deactivate mode
```

#### Rules
```bash
claude-ctx rule list                     # List all rules
claude-ctx rule activate <name>          # Activate rule
claude-ctx rule deactivate <name>        # Deactivate rule
```

#### Skills
```bash
claude-ctx skill list                    # List local skills
claude-ctx skill info <name>             # Show skill details
claude-ctx skill validate <name>         # Validate skill
claude-ctx skill community list          # Browse community skills
claude-ctx skill community search <term> # Search community skills
```

#### Status
```bash
claude-ctx status                        # Show system overview
```

## Configuration

Configuration files are located in `~/.claude/`:

```
~/.claude/
├── CLAUDE.md              # Main configuration
├── FLAGS.md               # Behavioral flags
├── RULES.md               # Core rules
├── PRINCIPLES.md          # Engineering principles
├── agents/                # Agent definitions
├── modes/                 # Behavioral modes
├── rules/                 # Rule modules
└── skills/                # Custom skills
```

## Troubleshooting

### TUI not updating after code changes

```bash
pipx reinstall claude-ctx-py
```

### Missing dependency errors

```bash
pipx inject claude-ctx-py <package-name>
```

Example for PyYAML:
```bash
pipx inject claude-ctx-py PyYAML
```

### Clear Python cache

```bash
cd ~/Developer/personal/claude-ctx-plugin
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
```

### Complete reinstall

```bash
pipx uninstall claude-ctx-py
cd ~/Developer/personal/claude-ctx-plugin
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
pipx install .
```

## Development Workflow

1. Make code changes in `~/Developer/personal/claude-ctx-plugin/`
2. Clear cache: `find . -type d -name __pycache__ -exec rm -rf {} +`
3. Reinstall: `pipx reinstall claude-ctx-py`
4. Test: `claude-ctx tui`

## Features

### TUI Features
- 9 interactive views with complete CLI parity
- Pagination (max 8 items per view to prevent scrolling)
- Real-time filtering and search
- Keyboard navigation
- Status indicators
- Position counters

### CLI Features
- Tab completion (if argcomplete installed)
- Rich formatted output
- Status summaries
- Batch operations
- Community skill browsing

## Quick Start

1. Install the package:
   ```bash
   cd ~/Developer/personal/claude-ctx-plugin
   pipx install .
   ```

2. Launch the TUI:
   ```bash
   claude-ctx tui
   ```

3. Navigate with number keys (1-9) and arrow keys

4. Press `?` for help at any time

5. Press `q` to quit

## Getting Help

- In TUI: Press `?` for keyboard shortcuts
- CLI help: `claude-ctx --help`
- Command help: `claude-ctx <command> --help`
- Report issues: https://github.com/NickCrew/claude-ctx-plugin/issues
