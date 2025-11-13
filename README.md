# Claude CTX Plugin

This repository packages the `claude-ctx` context management toolkit as a Claude Code plugin. It bundles the curated agents, commands, modes, rules, and supporting Python CLI so teams can install the complete experience through the plugin system or keep using the standalone `claude-ctx` script.

> 📚 **Docs:** <https://nickcrew.github.io/claude-ctx-plugin/>
> 🎬 **Presentations:** [Claude CTX Overview](docs/presentations/claude-ctx-overview.html) • [TUI Showcase](docs/presentations/tui-showcase.html)

## What's inside

- `commands/` – slash command definitions that surface curated behavioural prompts
- `agents/` and `agents-disabled/` – Claude subagents with dependency metadata
- `modes/` and `modes-inactive/` – opinionated context modules that toggle workflow defaults
- `rules/` – reusable rule sets referenced by the CLI and plugin commands
- `profiles/`, `scenarios/`, `workflows/` – higher-level orchestration templates for complex workstreams
- `claude_ctx_py/` and `claude-ctx-py` – Python CLI entrypoint mirroring the original `claude-ctx`
- `schema/` and `scripts/` – validation schemas and helper scripts

### 🔥 New: Super Saiyan Mode

Universal visual excellence framework with platform detection:
- **`modes/Super_Saiyan.md`** – Core generic mode with auto-detection
- **`modes/supersaiyan/`** – Platform-specific implementations (Web, TUI, CLI, Docs)
- **`claude_ctx_py/tui_supersaiyan.py`** – Enhanced Textual components
- **`examples/supersaiyan_demo.py`** – Interactive demo
- **Three power levels**: ⭐ Super Saiyan → ⚡ Kamehameha → 💥 Over 9000

**Quick start:**
```bash
python examples/supersaiyan_demo.py  # See it in action!
```

See [Super Saiyan Integration Guide](docs/guides/features/SUPER_SAIYAN_INTEGRATION.md) for details.

### 🤖 New: AI Intelligence & Automation

**Stay in Claude Code flow** - Let AI manage the framework for you with context-aware intelligence, pattern learning, and auto-activation:

- **Context Detection** – Automatically analyzes changed files, detects auth/API/tests/frontend/backend
- **Pattern Learning** – Learns from successful sessions, recommends optimal agent combinations
- **Workflow Prediction** – Predicts agent sequences based on similar past work
- **Auto-Activation** – High-confidence agents activate automatically (≥80%)
- **Watch Mode** – Real-time monitoring with instant recommendations (no daemon required)
- **TUI AI Assistant** – Interactive view with recommendations and predictions (press `0`)
- **Skill Palette Shortcuts** – `Ctrl+P` → type “Skill…” to run info, versions, deps, analytics, trending, or community install/validate/rate/search commands without leaving the TUI

**Quick start:**
```bash
# Get AI recommendations for current context
claude-ctx ai recommend

# Auto-activate high-confidence agents
claude-ctx ai auto-activate

# Start watch mode (real-time monitoring)
claude-ctx ai watch

# Interactive TUI with AI assistant
claude-ctx tui
# Press '0' for AI Assistant view
# Press 'A' to auto-activate recommendations

# Record successful sessions for learning
claude-ctx ai record-success --outcome "feature complete"
```

**Watch Mode Example:**
```
══════════════════════════════════════════════════════════════════════
🤖 AI WATCH MODE - Real-time Intelligence
══════════════════════════════════════════════════════════════════════

[10:33:12] 🔍 Context detected: Backend, Auth
  3 files changed

  💡 Recommendations:
     🔴 security-auditor [AUTO]
        95% - Auth code detected

[10:33:12] ⚡ Auto-activating 1 agents...
     ✓ security-auditor
```

See [AI Intelligence Guide](docs/guides/development/AI_INTELLIGENCE_GUIDE.md) and [Watch Mode Guide](docs/guides/development/WATCH_MODE_GUIDE.md) for complete documentation.

### 🔌 New: MCP Server Management

**Intelligent MCP server management** - Observe, validate, and document your Model Context Protocol servers:

- **Server Discovery** – Automatically finds MCP servers from Claude Desktop config
- **Configuration Validation** – Diagnose issues and verify server setup
- **Curated Documentation** – Built-in guides for Context7, Serena, Sequential, Magic, and more
- **Visual Dashboard** – TUI view with server status, testing, and docs (press `7`)
- **Smart Recommendations** – Integration with `/tools:select` for optimal MCP routing

**Quick start:**
```bash
# List all configured MCP servers
claude-ctx mcp list

# Show server details and validation
claude-ctx mcp show context7

# View curated documentation
claude-ctx mcp docs serena

# Diagnose all servers
claude-ctx mcp diagnose

# Generate config snippet
claude-ctx mcp snippet playwright
```

**TUI Interface:**
```
claude-ctx tui
# Press '7' for MCP Servers view
# t=test, d=docs, c=copy, v=validate
```

See [MCP Management Guide](docs/guides/mcp/MCP_MANAGEMENT.md) for complete documentation.

The plugin manifest lives in `.claude-plugin/plugin.json` so Claude Code detects commands and agents automatically when the marketplace entry points to this repository.

## Installing via Claude Code

1. Add the marketplace that references this repository (see the companion [`NickCrew/claude-marketplace`](https://github.com/NickCrew/claude-marketplace) project).
2. Install the plugin with `/plugin install claude-ctx@<marketplace-name>`.
3. Restart Claude Code so the new commands and agents load.

After installation, the `/plugin` browser will list the bundled commands, and the `/agents` panel will show all active agents from the `agents/` directory.

## Installing the CLI

### Quick Install (Recommended)

Install the package, shell completions, and manpage with one command:

```bash
./scripts/install.sh
```

This will:
- Install `claude-ctx-py` in editable mode with dev dependencies
- Set up shell completions for your shell (bash/zsh/fish)
- Install the manpage system-wide

**Options:**
```bash
./scripts/install.sh --help              # Show all options
./scripts/install.sh --no-completions    # Skip completions
./scripts/install.sh --system-install    # Install system-wide (not editable)
./scripts/install.sh --shell zsh         # Specify shell for completions
```

### Using Make

```bash
make install        # Full installation
make install-dev    # Development installation
make help           # Show all targets
```

### Manual Installation

```bash
python3 -m pip install .
claude-ctx mode list
claude-ctx agent graph --export dependency-map.md
```

Running the CLI directly will operate on the directories in this repository, which mirror the layout expected inside `~/.claude`.

> **Tip:** The CLI looks in this order for its data folder: `CLAUDE_CTX_HOME`, `CLAUDE_PLUGIN_ROOT` (set automatically when Claude Code runs plugin commands), then `~/.claude`. After installing the plugin you can point the standalone CLI at the cached copy with:
>
> ```bash
> export CLAUDE_CTX_HOME="$HOME/.claude/plugins/cache/claude-ctx"
> ```
>
> or, if you work from another checkout:
>
> ```bash
> export CLAUDE_CTX_HOME="$HOME/Developer/personal/claude-ctx-plugin"
> ```
>
> Set that once (for example in `~/.zshrc`) and both the CLI and Claude Code will use the same data without reinstalling.

### Shell completion

Shell completions are automatically installed when using `./scripts/install.sh`. For manual setup:

**Automatic (recommended):**
```bash
# Generate and install completions for your shell
claude-ctx completion bash > ~/.bash_completion.d/claude-ctx
claude-ctx completion zsh > ~/.zsh/completions/_claude-ctx
claude-ctx completion fish > ~/.config/fish/completions/claude-ctx.fish

# Show installation instructions
claude-ctx completion bash --install
```

**Using argcomplete (legacy method):**
```bash
# Bash
register-python-argcomplete claude-ctx > ~/.local/share/bash-completion/completions/claude-ctx

# Zsh
register-python-argcomplete --shell zsh claude-ctx > ~/.local/share/zsh/site-functions/_claude-ctx

# Fish
register-python-argcomplete --shell fish claude-ctx > ~/.config/fish/completions/claude-ctx.fish
```

See [Shell Completions Guide](docs/guides/COMPLETIONS.md) for detailed instructions.

### Manual page (manpage)

A comprehensive manual page is available in `docs/reference/claude-ctx.1` and is automatically installed when using `./scripts/install.sh`.

**View locally:**
```bash
man docs/reference/claude-ctx.1
```

Dedicated entries are also available for the TUI (`man claude-ctx-tui`) and the
workflow/scenario orchestration commands (`man claude-ctx-workflow`).

**Manual installation:**
```bash
./scripts/install-manpage.sh
```

**After installation:**
```bash
man claude-ctx
```

The manpage documents all commands, subcommands, options, file locations, environment variables, and includes practical examples. It follows standard Unix manual page conventions and can be searched with `/` when viewing.

### Advanced Features

For more advanced features, see the following guides:
- [Warp AI & Terminal AI Integration](docs/guides/integrations.md)
- [Hooks and Auto-Suggestions](docs/guides/hooks.md)

## License & Attribution

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### Credits

Claude CTX builds upon ideas and patterns from several excellent projects in the Claude Code ecosystem:

- **[obra/superpowers](https://github.com/obra/superpowers)** - Systematic debugging and quality gate patterns (MIT License)
- **[VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents)** - Specialized agent architecture and modular design (MIT License)
- **[SuperClaude-Org/SuperClaude_Framework](https://github.com/SuperClaude-Org/SuperClaude_Framework)** - Behavioral modes, slash commands, and MCP integration patterns (MIT License)
- **[just-every/code](https://github.com/just-every/code)** - Multi-agent orchestration and reasoning control concepts (Apache-2.0 License)

See [CREDITS.md](CREDITS.md) for detailed attribution and a complete list of inspirations and dependencies.

## Development notes

- Update the version in `.claude-plugin/plugin.json` whenever you publish a new release.
- Keep semantic changes to commands or agents alongside changelog entries in `CLAUDE.md` or `RULES.md`.
- Use `claude plugin validate .` to confirm the manifest structure prior to publishing.

For marketplace configuration examples, see `../claude-private-marketplace`.

## Preview the docs locally

The documentation site under `docs/` now uses the default GitHub Pages **minima** theme with custom styling. To run it locally:

```bash
cd docs
bundle install
bundle exec jekyll serve --source . --livereload
```

Then open <http://127.0.0.1:4000>. Changes to Markdown or assets refresh automatically.
