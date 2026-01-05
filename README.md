# Cortex

This repository packages the Cortex (`cortex`) context management toolkit as a Claude Code plugin.
It bundles the curated agents, commands, modes, rules, and supporting Python CLI + TUI so teams can install the complete experience through the plugin system or keep using the standalone `cortex` / `cortex-ui` scripts.

**Note:** The `cortex` command  has been deprecated but will remain available for a while.  

> 📚 **Docs:** <https://nickcrew.github.io/claude-cortex/>
> 🎬 **Presentations:** [Intro Overview](docs/presentations/claude-ctx-overview.html) • [Technical Deep Dive](docs/presentations/claude-ctx-technical-deep-dive.html) • [Executive Roadmap](docs/presentations/claude-ctx-executive-roadmap.html) • [Feature Catalog](docs/presentations/tui-showcase.html)

## What's inside

- `commands/` – slash command definitions that surface curated behavioural prompts
- `agents/` and `inactive/agents/` – Claude subagents with dependency metadata (move files into `inactive/agents` to park them)
- `modes/` – opinionated context modules that toggle workflow defaults (activation tracked in `.active-modes`, managed via CLI/TUI)
- `rules/` – reusable rule sets referenced by the CLI and plugin commands
- `flags/` – modular context packs toggled via `FLAGS.md`
- `hooks/` – optional automation hooks for command workflows
- `profiles/`, `scenarios/`, `workflows/` – higher-level orchestration templates for complex workstreams
- `claude_ctx_py/` and `claude-ctx-py` – Python CLI entrypoint mirroring the original `cortex`
- `schema/` and `scripts/` – validation schemas and helper scripts

### 🆕 Latest Updates

- **Template guardrails** – The TUI detects missing `templates/` files in the active `CLAUDE_PLUGIN_ROOT` and offers to initialize them or run the setup wizard.
- **Multi-LLM consult skill** – Ask Gemini, OpenAI (Codex), or Qwen for a second opinion; configure provider API keys via the TUI Command Palette -> "Configure LLM Providers".
- **Asset Manager reliability** – “Update All” and “Install All in Category” now behave consistently with clearer prompts.
- **Flag toggles restored** – Spacebar toggling works again in the Flag Explorer and Flag Manager, updating `FLAGS.md` immediately.

### ✅ Stability Update: AI + Context Management

We’ve fixed major issues across AI recommendations and context state tracking. Auto-activation and watch mode are more reliable, and context activation now uses `.active-*` state files with `cortex doctor` and `cortex setup migrate` to keep everything consistent.

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

### 📦 New: Asset Manager

Install, diff, and update plugin assets directly from the TUI:

- Discover hooks, commands, agents, skills, modes, workflows, and flags
- Install/uninstall to any detected `.claude` directory
- Diff installed vs source, bulk install by category, update outdated assets

**Quick start:**

```bash
cortex tui
# Press 'A' for Asset Manager
# i=install, u=uninstall, d=diff, U=update all, I=bulk install, T=target dir
```

### 🌿 New: Worktree Manager

Manage git worktrees from the CLI or TUI.

**CLI:**

```bash
cortex worktree list
cortex worktree add my-branch --path ../worktrees/my-branch
cortex worktree remove my-branch
cortex worktree prune --dry-run
cortex worktree dir ../worktrees
cortex worktree dir --clear
```

**TUI:**

```bash
cortex tui
# Press 'C' for Worktrees
# Ctrl+N add, Ctrl+O open, Ctrl+W remove, Ctrl+K prune, Ctrl+B set base dir
```

### 🧭 New: Setup, Init & Migration

The installer and setup tooling have been overhauled to keep projects consistent across upgrades.

```bash
# Detect your project and recommend a profile
cortex init detect

# Apply a profile directly
cortex init profile backend

# Check init status
cortex init status

# Migrate CLAUDE.md comment activation → .active-* files
cortex setup migrate
```

### 🤖 New: AI Intelligence & Automation

**Stay in Claude Code flow** - Let AI manage the framework for you with context-aware intelligence, pattern learning, and auto-activation:

- **Context Detection** – Automatically analyzes changed files, detects auth/API/tests/frontend/backend
- **Pattern Learning** – Learns from successful sessions, recommends optimal agent combinations
- **Workflow Prediction** – Predicts agent sequences based on similar past work
- **Auto-Activation** – High-confidence agents activate automatically (≥80%)
- **Watch Mode** – Real-time monitoring with instant recommendations (no daemon required)
- **TUI AI Assistant** – Interactive view with recommendations and predictions (press `0`)
- **Skill Palette Shortcuts** – `Ctrl+P` → type “Skill…” to run info, versions, deps, analytics, trending, or community install/validate/rate/search commands without leaving the TUI
- **Multi-Reviewer Auto-Activation** – Code changes can auto-activate multiple reviewers (quality, code, TS/React/UX, DB/SQL, performance, architecture)

**Quick start:**

```bash
# Get AI recommendations for current context
cortex ai recommend

# Auto-activate high-confidence agents
cortex ai auto-activate

# Start watch mode (real-time monitoring)
cortex ai watch

# Interactive TUI with AI assistant
cortex tui
# Press '0' for AI Assistant view
# Press 'A' to auto-activate recommendations

# Record successful sessions for learning
cortex ai record-success --outcome "feature complete"
```

**Multi-review output example:**

```
1. 🔵 quality-engineer [AUTO]
   Confidence: 85%
   Reason: Changes detected - quality review recommended

2. 🔵 code-reviewer [AUTO]
   Confidence: 75%
   Reason: Changes detected - code review recommended

3. 🔵 typescript-pro [AUTO]
   Confidence: 85%
   Reason: TypeScript changes detected - review recommended

4. 🔵 react-specialist [AUTO]
   Confidence: 80%
   Reason: React/UI component changes detected - review recommended

5. 🔵 ui-ux-designer [AUTO]
   Confidence: 80%
   Reason: User-facing UI changes detected - UX review recommended
```

**Watch Mode Example:**

```
══════════════════════════════════════════════════════════════════════
🤖 AI WATCH MODE - Real-time Intelligence
══════════════════════════════════════════════════════════════════════

[10:33:12] 🔍 Context detected: Backend, Auth
  3 files changed

  💡 Recommendations:
     🔵 quality-engineer [AUTO]
        85% - Changes detected - quality review recommended
     🔵 code-reviewer [AUTO]
        75% - Changes detected - code review recommended
     🔴 security-auditor [AUTO]
        95% - Auth code detected

[10:33:12] ⚡ Auto-activating 3 agents...
     ✓ quality-engineer
     ✓ code-reviewer
     ✓ security-auditor
```

See [AI Intelligence Guide](docs/guides/development/AI_INTELLIGENCE_GUIDE.md) and [Watch Mode Guide](docs/guides/development/WATCH_MODE_GUIDE.md) for complete documentation.

### ⭐ New: Skill Ratings & Auto-Feedback Loops

**Phase 5** introduces a first-class feedback engine so skills can improve themselves:

- **Ratings & Reviews** – `cortex skills rate <skill>` stores star ratings, helpful/not-helpful votes, and optional text feedback in `~/.claude/data/skill-ratings.db`.
- **Quality Metrics** – `cortex skills ratings <skill>` shows averages, distributions, success correlation, and token efficiency; `skills top-rated`, `skills export-ratings`, and `skills analytics` expose the aggregate view.
- **TUI Surfacing** – The Skills table now includes a **Rating** column (press `5`). Select a skill and press `Ctrl+R` to launch an inline rating dialog without leaving the terminal.
- **Auto Prompts** – Recent skill activations trigger modal prompts shortly after the TUI launches. The prompt explains why the skill was selected (usage count, task types, success rate) and offers to collect feedback on the spot. Dismiss once to snooze for 24 h; rating it clears future prompts until another burst of usage.
- **Recommendation Feedback Loop** – Ratings feed back into the AI recommender, so highly rated skills are prioritized and low-signal ones get demoted automatically (Feature 2 of the Phase 5 roadmap).

```bash
# Record a rating and optional review
cortex skills rate owasp-top-10 --stars 5 --review "Still the best security checklist"

# Inspect ratings/metrics
cortex skills ratings owasp-top-10
cortex skills top-rated --limit 5

# Export for analysis
cortex skills export-ratings --format csv > skill-feedback.csv
```

Within the TUI:

```
cortex tui
# Press 5 for Skills view, highlight a skill, press Ctrl+R to rate
# Auto prompts appear when the assistant detects a frequently used skill that lacks fresh feedback
```

See [Phase 5 Roadmap](docs/guides/development/PHASE5_ROADMAP.md) for the broader Intelligence + Feedback plan.

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
cortex mcp list

# Show server details and validation
cortex mcp show context7

# View curated documentation
cortex mcp docs serena

# Diagnose all servers
cortex mcp diagnose

# Generate config snippet
cortex mcp snippet playwright
```

**TUI Interface:**

```
cortex tui
# Press '7' for MCP Servers view
# t=test, d=docs, c=copy, v=validate
```

See [MCP Management Guide](docs/guides/mcp/MCP_MANAGEMENT.md) for complete documentation.

### ⚙️ New: Token-Efficient Flag Management

**Smart flag management** - Control Claude's behavior flags with surgical precision and save tokens:

- **Modular Flag Categories** – 22 flag categories split into focused files (mode-activation, testing, debugging, etc.)
- **Token Analytics** – Real-time token counting shows savings per category (~100-250 tokens each)
- **TUI Flag Manager** – Visual interface for enabling/disabling flags (press `Ctrl+G`)
- **Profile Integration** – Flags auto-configure when switching profiles
- **Config Auto-Update** – Changes persist immediately to `FLAGS.md`

**Flag Categories (3,380 tokens total):**

| Category | Tokens | Purpose |
|----------|--------|---------|
| Mode Activation | 120 | Core behavioral flags (brainstorm, introspect, orchestrate) |
| MCP Servers | 160 | MCP server control (context7, sequential, magic, etc.) |
| Thinking Budget | 140 | Reasoning budget controls and cost-aware tuning |
| Analysis Depth | 130 | Thinking depth control (--think, --ultrathink) |
| Execution Control | 150 | Delegation, concurrency, iteration control |
| Visual Excellence | 250 | Super Saiyan, UI polish, design system |
| Output Optimization | 120 | Scope, focus, compression flags |
| Testing & Quality | 170 | TDD, coverage, mutation testing |
| Learning & Education | 160 | Educational modes, explanations |
| Cost Management | 120 | Budget limits, cost awareness |
| Refactoring Safety | 140 | Safe refactoring, behavior preservation |
| Domain Presets | 150 | Frontend, backend, fullstack presets |
| Debugging & Trace | 110 | Verbose logging, execution tracing |
| Interactive Control | 130 | Confirmation, pair programming modes |
| CI/CD | 100 | Headless, JSON output, automation |
| Auto-Escalation | 180 | Automatic reasoning depth adjustment |
| Performance Optimization | 180 | Profiling, benchmarking, scaling guidance |
| Security Hardening | 190 | Security-first workflows, threat modeling |
| Documentation Generation | 170 | Doc-driven workflows, reference output |
| Git Workflow | 160 | PR hygiene, commits, release steps |
| Migration & Upgrade | 170 | Version upgrades, compatibility guarantees |
| Database Operations | 180 | Schema changes, data safety, migrations |

**Quick start:**

```bash
# Open Flag Manager in TUI
cortex tui
# Press Ctrl+G for Flag Manager
# Use ↑↓ to select, Space to toggle

# Apply profile with flags
cortex profile apply frontend
# Auto-enables: visual-excellence, testing-quality, debugging-trace
# Saves: ~1,120 tokens (52% savings!)
```

**Example: Frontend Profile**

Example configuration enables 6/22 categories (930 tokens):

- mode-activation, mcp-servers, analysis-depth
- execution-control, visual-excellence, output-optimization

When you switch to **frontend** profile:

- **Auto-enables**: testing-quality, domain-presets, debugging-trace
- **Loads**: 1,110 tokens (7 categories)
- **Saves**: 2,270 tokens (15 categories disabled)
- **Savings**: 67% reduction in flag overhead

**All Profile Configurations:**

| Profile | Active Flags | Tokens Loaded | Tokens Saved | Savings |
|---------|--------------|---------------|--------------|---------|
| minimal | 3 categories | 430 | 2,950 | 87% |
| frontend | 7 categories | 1,110 | 2,270 | 67% |
| backend | 7 categories | 980 | 2,400 | 71% |
| devops | 5 categories | 640 | 2,740 | 81% |
| documentation | 3 categories | 430 | 2,950 | 87% |
| quality | 7 categories | 980 | 2,400 | 71% |
| full | 22 categories | 3,380 | 0 | 0% |

**Flag Manager Interface:**

```
⚙️ Flag Manager

Status  Flag Category                    Tokens  File
──────  ────────────────────────────────  ──────  ─────────────────────────────
Summary 6/22 active                       930/3380 Saving 72% tokens (2450 tokens)
──────  ────────────────────────────────  ──────  ─────────────────────────────
✓ ON    ▸ Mode Activation Flags           120     mode-activation.md
✓ ON    MCP Server Flags                  160     mcp-servers.md
✗ OFF   Testing Quality Flags             170     testing-quality.md
✗ OFF   Learning Education Flags          160     learning-education.md
...

Controls: ↑↓ Select    Space Toggle    Changes saved to FLAGS.md
```

**Location:** Flag files live in `~/.claude/flags/` and are referenced in `~/.claude/FLAGS.md` (which is included by `CLAUDE.md`)

See [Flag Management Guide](docs/guides/FLAGS_MANAGEMENT.md) for complete documentation.

The plugin manifest lives in `.claude-plugin/plugin.json` so Claude Code detects commands and agents automatically when the marketplace entry points to this repository.

## Installing via Claude Code

1. Add the marketplace that references this repository (see the companion [`NickCrew/claude-marketplace`](https://github.com/NickCrew/claude-marketplace) project).
2. Install the plugin with `/plugin install cortex@<marketplace-name>`.
3. Restart Claude Code so the new commands and agents load.

After installation, the `/plugin` browser will list the bundled commands, and the `/agents` panel will show all active agents from the `agents/` directory.

## Installing the CLI

### Legacy Installer (Deprecated)

The legacy install scripts live under `scripts/deprecated/`. They are still available,
but new installs should use the CLI flow below.

```bash
./scripts/deprecated/install.sh
```

This will:

- Install `claude-ctx-py` in editable mode with dev dependencies
- Set up shell completions for your shell (bash/zsh/fish)
- Install the manpage system-wide

**Options (legacy):**

```bash
./scripts/deprecated/install.sh --help              # Show all options
./scripts/deprecated/install.sh --no-completions    # Skip completions
./scripts/deprecated/install.sh --system-install    # Install system-wide (not editable)
./scripts/deprecated/install.sh --shell zsh         # Specify shell for completions
```

### CLI Post-Install (after any pip/uv/pipx install)

If you install the package manually, you can finish setup with the CLI:

```bash
cortex install post
```

This installs shell completions, manpages, and local architecture docs.

### Using Just

```bash
just install        # Full installation
just install-dev    # Development installation
just help           # Show all targets
```

### Manual Installation

```bash
python3 -m pip install .
cortex mode list
cortex agent graph --export dependency-map.md
```

Optional post-install steps:

```bash
cortex install post
```

You can also install the package via the CLI:

```bash
cortex install package --manager uv --editable --dev
cortex install package --manager pipx
```

Running the CLI directly will operate on the directories in this repository, which mirror the layout expected inside `~/.claude`.

> **Tip:** The CLI resolves its data folder in this order: `CLAUDE_CTX_SCOPE` (project/global/plugin), `CLAUDE_PLUGIN_ROOT` (set automatically when Claude Code runs plugin commands), then `~/.claude`. To point the standalone CLI at the plugin cache (or a local checkout), set:
>
> ```bash
> export CLAUDE_PLUGIN_ROOT="$HOME/.claude/plugins/cache/cortex"
> ```
>
> or:
>
> ```bash
> export CLAUDE_PLUGIN_ROOT="$HOME/Developer/personal/claude-cortex"
> ```
>
> To target a project-local scope or a specific plugin root:
>
> ```bash
> cortex --scope project status
> cortex --plugin-root /path/to/claude-cortex status
> ```

### Shell completion

Shell completions are automatically installed when using the legacy installer (`./scripts/deprecated/install.sh`). For manual setup:

**Automatic (recommended):**

```bash
# Generate and install completions for your shell
cortex completion bash > ~/.bash_completion.d/cortex
cortex completion zsh > ~/.zsh/completions/_cortex
cortex completion fish > ~/.config/fish/completions/cortex.fish

# Show installation instructions
cortex completion bash --install
```

**Using argcomplete (legacy method):**

```bash
# Bash
register-python-argcomplete cortex > ~/.local/share/bash-completion/completions/cortex

# Zsh
register-python-argcomplete --shell zsh cortex > ~/.local/share/zsh/site-functions/_cortex

# Fish
register-python-argcomplete --shell fish cortex > ~/.config/fish/completions/cortex.fish
```

See [Shell Completions Guide](docs/guides/COMPLETIONS.md) for detailed instructions.

### Manual page (manpage)

A comprehensive manual page is available in `docs/reference/cortex.1` and is automatically installed when using the legacy installer (`./scripts/deprecated/install.sh`).

**View locally:**

```bash
man docs/reference/cortex.1
```

Dedicated entries are also available for the TUI (`man cortex-tui`) and the
workflow/scenario orchestration commands (`man cortex-workflow`).

**Manual installation:**

```bash
./scripts/deprecated/install-manpage.sh
```

**After installation:**

```bash
man cortex
```

The manpage documents all commands, subcommands, options, file locations, environment variables, and includes practical examples. It follows standard Unix manual page conventions and can be searched with `/` when viewing.

### Advanced Features

For more advanced features, see the following guides:

- [Warp AI & Terminal AI Integration](docs/guides/integrations.md)
- [Hooks and Auto-Suggestions](docs/guides/hooks.md)

## License & Attribution

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### Credits

Cortex builds upon ideas and patterns from several excellent projects in the Claude Code ecosystem:

- **[obra/superpowers](https://github.com/obra/superpowers)** - Systematic debugging and quality gate patterns (MIT License)
- **[VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents)** - Specialized agent architecture and modular design (MIT License)
- **[SuperClaude-Org/SuperClaude_Framework](https://github.com/SuperClaude-Org/SuperClaude_Framework)** - Behavioral modes, slash commands, and MCP integration patterns (MIT License)
- **[just-every/code](https://github.com/just-every/code)** - Multi-agent orchestration and reasoning control concepts (Apache-2.0 License)

See [CREDITS.md](CREDITS.md) for detailed attribution and a complete list of inspirations and dependencies.

## Development notes

- Update the version in `.claude-plugin/plugin.json` whenever you publish a new release.
- Keep semantic changes to commands or agents alongside changelog entries in `CLAUDE.md` or `RULES.md`.
- Use `claude plugin validate .` to confirm the manifest structure prior to publishing.
- **Run strict type checks before opening a PR.**
  - `python3 -m mypy --strict claude_ctx_py`
  - The CI harness also drops the latest failure output in `/tmp/mypy.log`; keep that file around when iterating locally so you can jump directly to errors with your editor.
  - New modules should prefer `TypedDict`/`Protocol` over raw `dict`/`Any`, and Textual mixins need explicit state attributes so the UI keeps passing `--strict`.

For marketplace configuration examples, see `../claude-private-marketplace`.

## Preview the docs locally

The documentation site under `docs/` now uses the default GitHub Pages **minima** theme with custom styling. To run it locally:

```bash
cd docs
bundle install
bundle exec jekyll serve --source . --livereload
```

Then open <http://127.0.0.1:4000>. Changes to Markdown or assets refresh automatically.
