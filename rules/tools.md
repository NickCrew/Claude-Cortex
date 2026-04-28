# Tools

> _Tool selection and escalation. Git operations themselves live in
> `git-rules.md`; file-level rules (deletion, scratch, naming) live in
> `files.md`._

## CLI

- For git commits, use `cortex git commit` (files) and `cortex git
  patch` (hunks). Commit policy lives in `git-rules.md`. **If a
  `cortex git` sub-command is not available, fails, or lacks
  capabilities, escalate to the user; do not work around with other
  git commands.**
- Use `trash` to delete files. This moves them to `~/.Trash` where
  they're recoverable in an emergency. Never delete with `rm`.
- Use `cortex tmux` to manage local processes in a dedicated tmux
  window. Long-running processes (dev servers, watchers, builds)
  belong there rather than in foreground shells where output is lost
  on interruption.

## MCP Servers

When an MCP server fits the task, prefer it over a Bash equivalent —
MCP tools are purpose-built for their domain and return structured
output that's cheaper for downstream reasoning to consume.

- **backlog.md** — task tracking. Use in projects with a `backlog/`
  directory (the folder is tracked in git). Read the
  `backlog://workflow/overview` resource before creating tasks if you
  haven't this session.
- **codanna** — codebase exploration via semantic search, call
  graphs, and impact analysis. Use in projects with a `.codanna/`
  directory. Prefer over `grep` and `find` for symbol-level questions
  when codanna is available.
- **Dash** — up-to-date third-party documentation lookup. Prefer
  over WebSearch for library, framework, and SDK reference questions.

## When an MCP tool fails

- A failed MCP call is a signal, not a dead end. Retry once if the
  failure looks transient (network, timeout). If it's a configuration
  or permission error, surface it to the user.
- Do not silently switch to Bash to accomplish the same task when an
  MCP tool fails. The MCP exists for a reason; if it's unavailable,
  the user needs to know so they can fix the configuration.
- If an MCP tool returns a result that contradicts what you can
  observe directly (e.g. codanna says a symbol doesn't exist but
  `grep` finds it), report the contradiction rather than choosing
  one silently. Stale indexes and config drift produce these.

<!-- @hooks/skill_auto_suggester.py -->
