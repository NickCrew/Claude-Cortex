# Installation & Usage Guide

## Installation

### Option 0: Install with the installer (recommended)

```bash
./scripts/install.sh
```

This installs the package, shell completions, and manpages in one step. For a Makefile wrapper:

```bash
make install
```

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
- `w` - Watch Mode (real-time monitoring)
- `/` - Slash Commands catalog
- `S` - Scenarios
- `o` - Orchestrate view
- `g` - Agent Galaxy
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
claude-ctx rules list                    # List all rules
claude-ctx rules activate <name>         # Activate rule
claude-ctx rules deactivate <name>       # Deactivate rule
```

#### Skills
```bash
claude-ctx skills list                   # List local skills
claude-ctx skills info <name>            # Show skill details
claude-ctx skills validate <name>        # Validate skill
claude-ctx skills community list         # Browse community skills
claude-ctx skills community search <term># Search community skills
```

#### Worktrees
```bash
claude-ctx worktree list                 # List git worktrees
claude-ctx worktree add <branch>         # Add a worktree
claude-ctx worktree remove <target>      # Remove a worktree
claude-ctx worktree prune --dry-run      # Prune stale worktrees
claude-ctx worktree dir <path>           # Set base directory
```

#### Init & Migration
```bash
claude-ctx init detect                   # Detect project type
claude-ctx init profile backend          # Apply a profile
claude-ctx init status                   # Show init status
claude-ctx setup migrate                 # Migrate to .active-* activation
```

#### Status
```bash
claude-ctx status                        # Show system overview
```

## Configuration

Configuration files live in the active Claude directory (default `~/.claude/`).
The same layout applies to project-local `.claude/` when you use `--scope project`
or set `CLAUDE_CTX_SCOPE=project`.

### Core Framework Files

| Path | Purpose | Notes |
| --- | --- | --- |
| `CLAUDE.md` | Main manifest with `@` references | Primary entry point for context assembly |
| `FLAGS.md` | Flag activation list (`@flags/*.md`) | Updated by TUI Flag Manager |
| `PRINCIPLES.md` | Engineering principles | Included by `CLAUDE.md` |
| `RULES.md` | Core rules | Included by `CLAUDE.md` |

### Activation State Files

| Path | Purpose | Notes |
| --- | --- | --- |
| `.active-modes` | Active mode list | Reference-based activation |
| `.active-rules` | Active rules list | Reference-based activation |
| `.active-mcp` | Active MCP docs list | Reference-based activation |

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
- Multi-view TUI with dedicated screens for AI, MCP, assets, worktrees, memory, flags, scenarios, and tasks
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
