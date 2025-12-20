---
layout: default
title: Getting Started
nav_order: 2
---

# Getting Started

This repository packages the `claude-ctx` context management toolkit as a Claude Code plugin. It bundles the curated agents, commands, modes, rules, and supporting Python CLI so teams can install the complete experience through the plugin system or keep using the standalone `claude-ctx` script.

## What’s inside

- `commands/` – slash command definitions that surface curated behavioural prompts
- `agents/` and `inactive/agents/` – Claude subagents with dependency metadata
- `modes/` and `inactive/modes/` – opinionated context modules that toggle workflow defaults
- `rules/` – reusable rule sets referenced by the CLI and plugin commands
- `profiles/`, `scenarios/`, `workflows/` – higher-level orchestration templates for complex workstreams
- `claude_ctx_py/` and `claude-ctx-py` – Python CLI entrypoint mirroring the original `claude-ctx`
- `schema/` and `scripts/` – validation schemas and helper scripts

The plugin manifest lives in `.claude-plugin/plugin.json` so Claude Code detects commands and agents automatically when the marketplace entry points to this repository.

## Installing via Claude Code

1. Add the marketplace that references this repository (see the companion [`NickCrew/claude-marketplace`](https://github.com/NickCrew/claude-marketplace) project).
2. Install the plugin with `/plugin install claude-ctx@<marketplace-name>`.
3. Restart Claude Code so the new commands and agents load.

After installation, the `/plugin` browser will list the bundled commands, and the `/agents` panel will show all active agents from the `agents/` directory.

## Using the bundled CLI

```
python3 -m pip install .
claude-ctx mode list
claude-ctx agent graph --export dependency-map.md
```

Running the CLI directly will operate on the directories in this repository, which mirror the layout expected inside `~/.claude`.

> **Tip:** The CLI resolves its data folder in this order: `CLAUDE_CTX_HOME` (explicit path), `CLAUDE_CTX_SCOPE` (project/global/plugin), `CLAUDE_PLUGIN_ROOT` (set automatically when Claude Code runs plugin commands), then `~/.claude`. To point the standalone CLI at the plugin cache (or a local checkout), set:
>
> ```bash
> export CLAUDE_PLUGIN_ROOT="$HOME/.claude/plugins/cache/claude-ctx"
> ```
>
> or, if you work from another checkout:
>
> ```bash
> export CLAUDE_PLUGIN_ROOT="$HOME/Developer/personal/claude-ctx-plugin"
>
> To target a project-local scope or an explicit directory:
>
> ```bash
> claude-ctx --scope project status
> claude-ctx --claude-dir /path/to/.claude status
> ```
> ```
>
> Set that once (for example in `~/.zshrc`) and the standalone CLI will use the same cached plugin copy without reinstalling.

### Shell completion

`claude-ctx` ships with optional [argcomplete](https://github.com/kislyuk/argcomplete) support. Install the project (editable installs work too), then register the completer:

```
# editable install via pipx
pipx install --include-deps --editable .

# one-time registration for the active shell session
eval "$(~/.local/pipx/venvs/claude-ctx-py/bin/register-python-argcomplete claude-ctx)"

# add the same eval line to ~/.zshrc or ~/.bashrc for persistence
```

If you install the package with a different toolchain, point `register-python-argcomplete` at the virtual environment where `claude-ctx` lives.

## Development notes

- Update the version in `.claude-plugin/plugin.json` whenever you publish a new release.
- Keep semantic changes to commands or agents alongside changelog entries in `CLAUDE.md` or `RULES.md`.
- Use `claude plugin validate .` to confirm the manifest structure prior to publishing.

For marketplace configuration examples, see `../claude-private-marketplace`.
