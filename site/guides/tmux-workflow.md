---
layout: default
title: Tmux Workflow
parent: Guides
nav_order: 14
---

# Tmux Workflow

`cortex tmux` gives agents a small, scriptable control surface for named tmux
windows. It is meant for orchestration: start work in a window, inspect output,
wait for completion, and interrupt safely when needed.

## Session Model

`cortex tmux` operates inside one tmux session:

- if `TMUX_SESSION` is set, Cortex uses that
- otherwise it derives the session name from the current directory name

If the session does not exist, Cortex returns a helpful error instead of
guessing.

## What It Is For

Use `cortex tmux` when you want to:

- create dedicated windows for build, test, review, or watch tasks
- send commands without manually attaching to tmux
- talk to a TUI agent (Claude Code, Codex) running in another window
- inspect recent output from another window
- survey every session and window on the box at once
- wait for a command to finish
- watch for a success or failure pattern in output

This is especially useful when an agent needs multiple long-running terminals
without mixing their output together.

## Core Window Management

List windows:

```bash
cortex tmux list
```

Create a new window. By default the window starts in your current
working directory; pass `--cwd` to override it:

```bash
cortex tmux new review
cortex tmux new api-server --cwd /path/to/api
```

Without `--cwd`, tmux falls back to whatever directory the *server*
was started in — usually `$HOME`, almost never what you want.

Rename a window after an agent claims it, so `sessions` and
`snapshot` stay readable:

```bash
cortex tmux rename review Claude-Review
```

Kill a window when the task is done:

```bash
cortex tmux kill review
```

## Sending Commands vs Typing Text

Run a command and press Enter:

```bash
cortex tmux send review "pytest -m unit"
```

Type text without submitting it:

```bash
cortex tmux type review "pytest -m unit -k export"
```

Send a key sequence directly:

```bash
cortex tmux keys review C-c
cortex tmux keys review Up Enter
```

Or use the explicit interrupt helper:

```bash
cortex tmux interrupt review
```

One important behavior: `cortex tmux send` sends `Ctrl-C` first to clear any
partial input before it submits the new command. That makes it safer for agent
automation than blindly typing into a possibly half-edited shell line.

## Talking to TUI Agents

`send` is for shells. When the target window is running a TUI — Claude
Code, Codex, vim, fzf — use `say`:

```bash
cortex tmux say claude-frontend "what's your progress on the login form?"
```

`say` differs from `send` in two important ways:

- **No `Ctrl-C` clear.** That would interrupt whatever the agent in the
  target window is doing. `say` is safe to use against a thinking agent.
- **The text and the submit key are sent as two separate `send-keys`
  calls** with a 0.5-second pause between them. TUIs render their input
  on a debounced loop; if text and `Enter` arrive in the same call, the
  submit can race the render and you end up sending an empty or
  truncated message.

If a TUI is twitchy on a slow box, raise the settle:

```bash
cortex tmux say claude-frontend "..." --settle 1.0
```

Quick mental model:

| Target is… | Use      | `Ctrl-C` clear? | Text + Enter combined? |
|------------|----------|-----------------|-------------------------|
| Shell      | `send`   | yes             | yes                     |
| TUI        | `say`    | no              | no (two calls + settle) |

## Targeting Split Panes

All targeting subcommands accept `window.pane` syntax for split panes:

```bash
cortex tmux say claude-frontend.0 "..."   # left pane
cortex tmux send build.1 "cargo test"      # right pane
cortex tmux read claude-frontend.2 50      # third pane
```

Only the window-name half is validated; the pane number is forwarded
to tmux unchanged. A window literally named `my.config` is left alone
because the parser only treats purely numeric suffixes as pane indices.

## Reading Output

Read the last lines from a window:

```bash
cortex tmux read review
cortex tmux read review 100
```

Dump the entire scrollback buffer:

```bash
cortex tmux dump review
```

Get a compact status view:

```bash
cortex tmux status review
```

`status` is useful when you want a lightweight "does this window exist and what
did it print most recently?" check.

## Surveying All Sessions

`list` only shows windows in the current session. To see every session
on the box:

```bash
cortex tmux sessions
```

```text
main (attached): 4 windows
side (detached): 1 windows
```

For a deeper view — every session, every window, with the last N lines
of output per window — use `snapshot`:

```bash
cortex tmux snapshot
cortex tmux snapshot --lines 30
cortex tmux snapshot --session main
```

```text
=== main (attached) ===
  [0] Claude-Frontend *
    | Working on the login form…
    | Added /api/v1/auth integration
  [1] dev-server
    | Listening on :3000
```

The active window in each session is marked with a trailing `*`. The
output is plain text designed to be piped into an LLM context, so an
orchestrator agent can answer "what is every other agent doing right
now?" in one read.

## Waiting and Watching

Check whether the window looks busy:

```bash
cortex tmux running review
```

This exits with status `0` when a command appears to be running and `1` when
the pane looks idle at a shell prompt.

Wait for the command to finish:

```bash
cortex tmux wait review
cortex tmux wait review 180
```

Watch for a specific pattern:

```bash
cortex tmux watch review "FAILED"
cortex tmux watch review "Build succeeded" --timeout 300
```

If you call `watch` without a pattern, it waits for the prompt to return.

## Recommended Agent Pattern

A reliable workflow looks like this:

```bash
# create a dedicated window
cortex tmux new review

# start the job
cortex tmux send review "pytest -m unit"

# follow along without attaching
cortex tmux read review 80

# wait for completion
cortex tmux wait review 180

# inspect the tail again
cortex tmux status review
```

For watch-mode or dev servers, use pattern-based watching instead:

```bash
cortex tmux new docs
cortex tmux send docs "bundle exec jekyll serve --livereload"
cortex tmux watch docs "Server address:"
```

For a multi-agent orchestration loop, combine `snapshot` and `say`:

```bash
# 1. See who's on the box
cortex tmux snapshot --lines 5

# 2. Pick a window and check it's still active
cortex tmux running claude-frontend && \
  cortex tmux say claude-frontend "status update please?"

# 3. Wait a beat, then read the response
sleep 8
cortex tmux read claude-frontend 30
```

## When To Prefer Raw Tmux

Use raw tmux when you need full layout management — splitting new
panes, resizing, or attaching interactively. `cortex tmux` can drive
existing split panes via `window.pane` syntax but won't create them
for you. For day-to-day automation against named windows it remains
the more stable control plane.

## Related

- [Git Workflow]({% link guides/git-workflow.md %}) -- pair isolated worktrees with isolated tmux windows
- [Agent Activation]({% link guides/agent-activation.md %}) -- load the right agents before kicking off background work
- [Export Context]({% link guides/export.md %}) -- hand the right context to another session or model
