# Tmux Orchestration Guide

`cortex tmux` is the agent-facing primitive for driving processes in
sibling tmux windows: dev servers, REPLs, and other Claude/Codex
instances. This guide covers the patterns that turn it from a thin
`tmux send-keys` wrapper into something an orchestrator agent can rely
on, plus the small set of TUI-driving gotchas that bite anyone who
hasn't hit them before.

For the full subcommand reference, see the manpage: `man cortex-tmux`.

## Driving a shell vs. talking to a TUI

There are two send paths and they are not interchangeable.

### `cortex tmux send` — for shells

```bash
cortex tmux send build "cargo test"
```

Sends `C-c` to clear any partial input, waits 100ms, then sends the
command and `Enter` in a single `send-keys` call. Use this whenever
the target window is sitting at a shell prompt.

### `cortex tmux say` — for TUIs

```bash
cortex tmux say claude-frontend "what's your progress on the login form?"
```

Sends the message text and the submit keystroke as **two separate**
`send-keys` calls with a 0.5-second pause between them, and does *not*
prepend `C-c`.

Two reasons that pause matters:

1. **TUIs debounce input.** Claude Code, Codex, and similar apps render
   their input box on a render loop that re-evaluates after keystrokes
   land. If `text` and `Enter` arrive in the same `send-keys` call, the
   submit can race the render and you end up sending an empty (or
   truncated) message. The pause gives the TUI time to commit the text
   to its input state before the submit fires.
2. **`C-c` would interrupt the TUI.** Whatever the agent in the target
   window was doing — running a tool, drafting a response — `C-c`
   cancels it. `say` deliberately omits the clear so it's safe to
   interrupt a thinking agent with a message rather than a kill signal.

If a TUI feels twitchy on a slow box, raise the settle:

```bash
cortex tmux say claude-frontend "..." --settle 1.0
```

### Quick mental model

| Target is… | Use      | C-c clear? | Text & Enter combined? |
|------------|----------|------------|-------------------------|
| Shell      | `send`   | yes        | yes (one `send-keys`)   |
| TUI        | `say`    | no         | no (two, with settle)   |

## Surveying the box

When you don't know what every other agent is doing, ask the box.

### `cortex tmux sessions`

```text
main (attached): 4 windows
side (detached): 1 windows
```

One line per session. Useful as a first pass: are the sessions you
expected even running?

### `cortex tmux snapshot`

```text
=== main (attached) ===
  [0] claude-frontend *
    | Working on the login form…
    | Added /api/v1/auth integration
    | Running tests
  [1] dev-server
    | Listening on :3000
  [2] claude-backend
    | Reviewing schema changes

=== side (detached) ===
  [0] notes
    | (empty)
```

Multi-session digest with the last 10 lines per window (configurable
via `--lines N`). The active window in each session is marked with a
trailing `*`. Designed to be piped into an LLM context — small enough
to skim, structured enough to reason about.

```bash
# Just one session
cortex tmux snapshot --session main

# More history per window
cortex tmux snapshot --lines 30
```

The orchestrator pattern this enables: a coordinator agent runs
`cortex tmux snapshot` periodically, decides who to message, then uses
`cortex tmux say` to talk to whichever sibling needs attention.

## Session lifecycle

The whole module is window-centric, but every project has its own
session that needs to come up before windows can land in it.

```bash
# Idempotently create the project's session (resolved name if no arg)
cortex tmux session-new
cortex tmux session-new my-project --cwd /path/to/project

# Tear down the whole session (and every window in it)
cortex tmux session-kill my-project

# Land in the session — switch-client if you're already inside tmux,
# attach-session if you're at a bare shell. --window selects a
# starting window first.
cortex tmux attach my-project --window shell
```

Two asymmetries worth knowing:

- **`session-new` is idempotent by default.** Re-running returns
  success with an "already exists" message, so it's safe as a
  recipe dependency that fires on every invocation.
- **`session-kill` errors loudly on a missing session.** Kill is
  destructive; silent failure is the wrong default. Append
  `2>/dev/null || true` for fire-and-forget.

`attach` defers to your context: `tmux switch-client` when `$TMUX`
is set, `tmux attach-session` when it isn't. The latter takes over
the terminal until you detach.

## Window self-labeling

`cortex tmux rename <old> <new>` lets an agent claim and label its
window. Without this, `cortex tmux snapshot` shows you a wall of
`zsh`, `node`, and `bash` — useless for figuring out who's who. With
it, you get readable views of the box.

A naming convention that scales:

| Pattern              | Example              | Used for                 |
|----------------------|----------------------|--------------------------|
| `Claude-<role>`      | `Claude-Frontend`    | Claude/Codex agents      |
| `<runtime>-Dev`      | `NextJS-Dev`         | Dev servers              |
| `<service>-Server`   | `Uvicorn-Server`     | Long-running services    |
| `<role>-Shell`       | `Backend-Shell`      | Plain shells             |
| `TEMP-<task>`        | `TEMP-CodeReview`    | Short-lived helpers      |

The `TEMP-` prefix gives orchestrators a cheap way to spot windows
that should be reaped after a task completes.

## Working-directory inheritance

`cortex tmux new <name>` defaults `--cwd` to your current working
directory. Without that, new windows inherit the directory the tmux
*server* was started in — usually `$HOME`, occasionally the path of
some long-forgotten `tmux new-session` call. Agents that didn't know
this would land in the wrong project root and start running tests
against the wrong codebase.

If you want a window in a specific path, pass it explicitly:

```bash
cortex tmux new api-server --cwd /Users/nick/Developer/api
```

## Pane-aware addressing

All targeting subcommands accept `window.pane` syntax for split panes:

```bash
cortex tmux say claude-frontend.0 "..."   # left pane
cortex tmux send build.1 "cargo test"      # right pane
cortex tmux read claude-frontend.2 50      # third pane
```

The validator only checks the window-name half against the session's
window list. Pane indexing is forwarded to tmux unchanged. The
`.<digits>` parse is conservative: a window literally named
`my.config` is not stripped, because the suffix isn't numeric.

## Verification habits

### Always confirm the result of a `send` or `say`

`tmux send-keys` returns success when the keys *were dispatched*, not
when the command *succeeded*. Pair every meaningful send with a read:

```bash
cortex tmux send build "cargo test"
sleep 2
cortex tmux read build 50
```

For longer-running commands, wait for a prompt before reading:

```bash
cortex tmux send build "cargo test"
cortex tmux wait build 300         # block up to 5 minutes
cortex tmux read build 80
```

Or watch for a specific marker:

```bash
cortex tmux watch build "test result:" --timeout 300
```

### Don't double-start a TUI

If a window already has Claude (or any TUI) running, sending `claude`
again will type "claude" into the input box, not start a new instance.
Check first:

```bash
cortex tmux read claude-frontend 5
# If output looks like a TUI, use `say` to talk to it.
# If it looks like a shell prompt, use `send` to launch.
```

`cortex tmux running <window>` is the programmatic version of this
check: exits 0 if the pane looks busy, 1 if it's at a prompt.

### Plan Mode toggle (Claude TUI)

Claude's plan mode is bound to `Shift+Tab Shift+Tab` and isn't
discoverable through any visible UI. Driven over tmux:

```bash
cortex tmux keys claude-frontend "S-Tab S-Tab"
sleep 1
cortex tmux read claude-frontend 5 | grep -q "plan mode on" \
  || cortex tmux keys claude-frontend "S-Tab"
```

The verification step matters: the keystroke occasionally drops, and
without confirming you'll send a planning prompt to a Claude that's
not in plan mode and get implementation back instead of a plan.

## Putting it together

A minimal orchestration loop, written as shell pseudo-code:

```bash
# 1. See who's on the box
cortex tmux snapshot --lines 5

# 2. Pick a window and check it's still working
cortex tmux running claude-frontend && \
  cortex tmux say claude-frontend "status update please?"

# 3. Wait for a response, then read it
sleep 8
cortex tmux read claude-frontend 30

# 4. Spawn a helper if needed
cortex tmux new code-review --cwd "$(pwd)"
cortex tmux send code-review "claude"
sleep 5
cortex tmux say code-review "review the diff in claude-frontend's window"
```

The same primitives compose into recurring sweeps, hub-and-spoke
coordinators, or one-shot helper deployments — the shape is up to the
agent driving them.
