# Claude CTX Plugin

This repository packages the `claude-ctx` context management toolkit as a Claude Code plugin. It bundles the curated agents, commands, modes, rules, and supporting Python CLI so teams can install the complete experience through the plugin system or keep using the standalone `claude-ctx` script.

## What’s inside

- `commands/` – slash command definitions that surface curated behavioural prompts
- `agents/` and `agents-disabled/` – Claude subagents with dependency metadata
- `modes/` and `modes-inactive/` – opinionated context modules that toggle workflow defaults
- `rules/` – reusable rule sets referenced by the CLI and plugin commands
- `profiles/`, `scenarios/`, `workflows/` – higher-level orchestration templates for complex workstreams
- `claude_ctx_py/` and `claude-ctx-py` – Python CLI entrypoint mirroring the original `claude-ctx`
- `schema/`, `scripts/`, `shareable/` – validation schemas, helper scripts, and distribution assets

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

## Development notes

- Update the version in `.claude-plugin/plugin.json` whenever you publish a new release.
- Keep semantic changes to commands or agents alongside changelog entries in `CLAUDE.md` or `RULES.md`.
- Use `claude plugin validate .` to confirm the manifest structure prior to publishing.

For marketplace configuration examples, see `../claude-private-marketplace`.
