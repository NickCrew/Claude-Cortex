# Hooks

This directory contains hook scripts that Cortex installs into
`~/.claude/hooks/` and registers in `~/.claude/settings.json`. Each script
reacts to a Claude Code lifecycle event (prompt submit, tool use, session
end, etc.) to add quality gates, suggestions, or automation.

## Where the user-facing doc lives

The canonical install and reference guide is published at:

- **Hooks guide** — `site/guides/hooks.md` (installation, registration,
  environment variables, per-hook details)
- **Working with Skills** — `site/guides/working-with-skills.md` (the
  end-to-end story for the `skill_auto_suggester` hook specifically)

Install hooks through the TUI (`cortex tui` → press `7` for the Hooks view)
rather than editing `~/.claude/settings.json` by hand. The TUI validates
the event name, resolves script paths, and writes the correct JSON shape.

## Scripts in this directory

Hook scripts here are plain files -- they are not activated until you
install them through the TUI or `~/.claude/settings.json`. The install path
uses the `CORTEX_ROOT` environment variable to locate them at runtime.

For per-hook behavior and what each one checks, see the Hooks guide above.

Cortex used to be distributed as a Claude Code plugin, which registered
hooks through a `hooks.json` manifest in this directory. That manifest has
been removed -- registration now lives exclusively in
`~/.claude/settings.json` and is managed through the TUI Hooks view.
