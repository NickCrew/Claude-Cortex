# Installation & Usage Guide

## Installation

### Option 0: Legacy installer (deprecated)

```bash
./scripts/deprecated/install.sh
```

This installs the package, shell completions, and manpages in one step. For a Just wrapper:

```bash
just install
```

### Option 0.5: Post-install via the CLI

If the package is already installed, finish setup with:

```bash
cortex install post
```

This installs shell completions, manpages, and the local architecture docs.

### Option 1: Install from source (recommended for development)

```bash
cd ~/Developer/personal/cortex-plugin
pipx install -e .
```

This installs the package in editable mode, so any changes you make to the code will be immediately available.

Alternative (uv):

```bash
uv pip install -e .[dev]
```

If `cortex` is already available, you can also use:

```bash
cortex install package --manager uv --editable --dev --path .
```

### Option 2: Install from source (standard)

```bash
cd ~/Developer/personal/cortex-plugin
pipx install .
```

Standard installation. You'll need to reinstall after making code changes:

```bash
pipx reinstall cortex-py
```

Alternative (uv):

```bash
uv pip install .
```

Or via CLI (requires `cortex` already installed):

```bash
cortex install package --manager pipx
```

### Option 3: Uninstall and reinstall

If you need to completely remove and reinstall:

```bash
pipx uninstall cortex-py
pipx install ~/Developer/personal/cortex-plugin
```

## Usage

### TUI (Terminal User Interface)

Launch the interactive TUI:

```bash
cortex tui
```

### Launch Claude Code with Cortex

```bash
cortex start
```

The launcher creates `~/.cortex/cortex-config.json` on first run and uses it
along with `FLAGS.md` to select active flags, rules, modes, and principles. Override the Claude binary with
`--claude-bin` or pass extra Claude arguments after `--`.

Use `--modes` or `--flags` to override config/`FLAGS.md` for a single launch.

Alias: `cortex claude`

#### TUI Navigation

**Primary Views:**
- `1` - Overview (system summary)
- `2` - Agents (manage agents)
- `3` - Modes (behavioral modes)
- `4` - Rules (rule modules)
- `5` - Skills (local + community skills)
- `6` - Workflows (workflow management)
- `7` - MCP Servers (MCP management)
- `8` - Profiles (quick profile switching)
- `9` - Export (context export)
- `0` - AI Assistant (recommendations)

**Additional Views:**
- `A` - Asset Manager (install/diff/update assets)
- `C` - Worktrees (git worktree manager)
- `F` - Flag Explorer (flags + token budgets)
- `M` - Memory Vault (persistent notes)
- `p` - Principles (manage snippet activation)
- `w` - Watch Mode (real-time monitoring)
- `/` - Slash Commands catalog
- `S` - Scenarios
- `o` - Orchestrate view
- `Alt+g` - Agent Galaxy
- `t` - Tasks

**Navigation:**
- `↑/k` - Move up
- `↓/j` - Move down
- `Space` - Toggle active/inactive
- `Enter` - Show details
- `Esc` - Close dialogs / cancel
- `?` - Help
- `q` - Quit

### CLI Commands

#### Agents
```bash
cortex agent list                    # List all agents
cortex agent activate <name>         # Activate agent
cortex agent deactivate <name>       # Deactivate agent
cortex agent info <name>             # Show agent details
```

#### Modes
```bash
cortex mode list                     # List all modes
cortex mode activate <name>          # Activate mode
cortex mode deactivate <name>        # Deactivate mode
```

#### Rules
```bash
cortex rules list                    # List all rules
cortex rules activate <name>         # Activate rule
cortex rules deactivate <name>       # Deactivate rule
```

Rules are file-based: active rules live in `rules/`, inactive rules live in
`inactive/rules/`. The CLI/TUI toggles rules by moving files between those
folders and regenerating `CLAUDE.md`.

#### Skills
```bash
cortex skills list                   # List local skills
cortex skills info <name>            # Show skill details
cortex skills validate <name>        # Validate skill
cortex skills community list         # Browse community skills
cortex skills community search <term># Search community skills
```

#### Worktrees
```bash
cortex worktree list                 # List git worktrees
cortex worktree add <branch>         # Add a worktree
cortex worktree remove <target>      # Remove a worktree
cortex worktree prune --dry-run      # Prune stale worktrees
cortex worktree dir <path>           # Set base directory
```

#### Init & Migration
```bash
cortex init detect                   # Detect project type
cortex init profile backend          # Apply a profile
cortex init status                   # Show init status
cortex setup migrate                 # Migrate to .active-* activation
cortex setup migrate-commands --dry-run   # Preview command layout migration
cortex setup migrate-commands --force     # Overwrite conflicts (backups created)
```

If you add or update CLI subcommands, regenerate shell completions so the new options appear.

#### Status
```bash
cortex status                        # Show system overview
```

## Configuration

Configuration files live in the active Cortex directory (default `~/.cortex/`).
The same layout applies to project-local `.claude/` when you use `--scope project`
or set `CORTEX_SCOPE=project`.

### Core Framework Files

| Path | Purpose | Notes |
| --- | --- | --- |
| `CLAUDE.md` | Main manifest with `@` references | Primary entry point for context assembly |
| `FLAGS.md` | Flag activation list (`@flags/*.md`) | Updated by TUI Flag Manager; used by `cortex start` |
| `PRINCIPLES.md` | Engineering principles | Generated from `principles/*.md` |
| `RULES.md` | Core rules | Included by `CLAUDE.md` |

### Launcher Configuration

| Path | Purpose | Notes |
| --- | --- | --- |
| `cortex-config.json` | Launcher settings for `cortex start` | Controls active rules/modes/principles and settings path (flags come from `FLAGS.md` unless overridden) |

### Principles Snippets

| Path | Purpose | Notes |
| --- | --- | --- |
| `principles/*.md` | Principles snippets | Concatenated by `cortex principles build` |

### Activation State Files

| Path | Purpose | Notes |
| --- | --- | --- |
| `.active-modes` | Active mode list | Reference-based activation |
| `.active-rules` | Active rules list | Legacy tracking for profiles/wizard; rules are active by file location |
| `.active-mcp` | Active MCP docs list | Reference-based activation |
| `.active-principles` | Active principles snippet list | Used by `cortex principles build` (order is filename-sorted) |

### Agent and Skill Settings

| Path | Purpose | Notes |
| --- | --- | --- |
| `agents/triggers.yaml` | Agent trigger metadata | Used by recommendations |
| `skills/activation.yaml` | Skill keyword activation map | Used by auto-activation |
| `skills/composition.yaml` | Skill composition rules | Used by skill composer |
| `skills/versions.yaml` | Skill version registry | Used by `skills versions` |
| `skills/skill-rules.json` | Skill selection rules | Recommendation logic |
| `skills/recommendation-rules.json` | Recommendation rules | AI suggestions |
| `skills/community/registry.yaml` | Community skill registry | Community skill install |
| `skills/analytics.schema.json` | Skill analytics schema | Validation/reference |
| `skills/metrics.schema.json` | Skill metrics schema | Validation/reference |

### Hooks and MCP

| Path | Purpose | Notes |
| --- | --- | --- |
| `settings.json` | Claude Code settings (hooks) | TUI hooks manager updates this |
| `mcp/docs/*.md` | Local MCP docs | Activated via `.active-mcp` |

### Intelligence and Memory

| Path | Purpose | Notes |
| --- | --- | --- |
| `intelligence-config.json` | LLM intelligence settings | Model selection/budget/caching |
| `memory-config.json` | Memory vault settings | Vault path and auto-capture |

### Schemas

| Path | Purpose | Notes |
| --- | --- | --- |
| `schema/agent-schema-v2.yaml` | Agent validation schema | Used by validators |
| `schema/scenario-schema-v1.yaml` | Scenario validation schema | Used by validators |

### Auto-Managed Data (for reference)

| Path | Purpose | Notes |
| --- | --- | --- |
| `.metrics/skills/stats.json` | Skill metrics summary | Generated automatically |
| `.metrics/skills/activations.json` | Activation log | Generated automatically |
| `data/skill-ratings.db` | Skill ratings database | SQLite |
| `data/skill-rating-prompts.json` | Rating prompt state | Auto-managed |
| `intelligence/session_history.json` | Recommendation history | Auto-managed |
| `intelligence/semantic_cache/session_embeddings.jsonl` | Embedding cache | Auto-managed |
| `tasks/current/active_agents.json` | Task view state | Auto-managed |
| `tasks/current/active_workflow` | Current workflow name | Auto-managed |
| `tasks/current/workflow_status` | Workflow status | Auto-managed |
| `tasks/current/workflow_started` | Workflow start time | Auto-managed |
| `tasks/current/current_step` | Workflow step label | Auto-managed |
| `community/ratings/*.json` | Community skill ratings | Auto-managed |

### External (Claude Desktop MCP Config)

Claude Desktop config is outside `.claude` but is read for MCP server setup:

| Platform | Path |
| --- | --- |
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%/Claude/claude_desktop_config.json` |

## Troubleshooting

### TUI not updating after code changes

```bash
pipx reinstall cortex-py
```

### Missing dependency errors

```bash
pipx inject cortex-py <package-name>
```

Example for PyYAML:
```bash
pipx inject cortex-py PyYAML
```

### Clear Python cache

```bash
cd ~/Developer/personal/cortex-plugin
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
```

### Complete reinstall

```bash
pipx uninstall cortex-py
cd ~/Developer/personal/cortex-plugin
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
pipx install .
```

## Development Workflow

1. Make code changes in `~/Developer/personal/cortex-plugin/`
2. Clear cache: `find . -type d -name __pycache__ -exec rm -rf {} +`
3. Reinstall: `pipx reinstall cortex-py`
4. Test: `cortex tui`

## Features

### TUI Features
- Multi-view TUI with dedicated screens for AI, MCP, assets, worktrees, memory, flags, principles, scenarios, and tasks
- Pagination (max 8 items per view to prevent scrolling)
- Real-time filtering and search
- Keyboard navigation
- Status indicators
- Position counters

### CLI Features
- Tab completion (if argcomplete installed)
- Rich formatted output
- Status summaries
- Batch operations and migration helpers
- Community skill browsing

## Quick Start

1. Install the package:
   ```bash
   cd ~/Developer/personal/cortex-plugin
   pipx install .
   ```

2. Launch the TUI:
   ```bash
   cortex tui
   ```

3. Navigate with number keys (1-9) and arrow keys

4. Press `?` for help at any time

5. Press `q` to quit

## Getting Help

- In TUI: Press `?` for keyboard shortcuts
- CLI help: `cortex --help`
- Command help: `cortex <command> --help`
- Report issues: https://github.com/NickCrew/claude-cortex/issues
