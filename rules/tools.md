# Tools

## CLI

- Use `cortex get commit` (file-based) to commit your changes. To commit hunks/lines, use `cortex git patch`. If a `cortex git` sub-command is not available, fails, or lacks capabilities, escalate to the user; do not work around with other git commands.
- Use `trash` to delete files. This moves the files to `~/.Trash` where it is recoverable in case of emergency Never delete with `rm`.
- Use `cortex tmux` to manage local processes in a dedicated tmux window.

## MCP Servers

- Use the **backlog.md** MCP server for task tracking (in projects with a `backlog/` directory). The `backlog/` folder is tracked in git.
- Use the **codanna** MCP server for codebase exploration (in projects with a `.codanna/` directory)
- Use the **Dash** MCP server for update-to-date third-party documentation

<!-- @hooks/skill_auto_suggester.py -->
