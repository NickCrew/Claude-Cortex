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
- inspect recent output from another window
- wait for a command to finish
- watch for a success or failure pattern in output

This is especially useful when an agent needs multiple long-running terminals
without mixing their output together.

## Core Window Management

List windows:

```bash
cortex tmux list
```

Create a new window:

```bash
cortex tmux new review
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

## When To Prefer Raw Tmux

Use raw tmux when you need layout management, pane splitting, or other fully
interactive terminal behavior. Use `cortex tmux` when you want a stable
automation-friendly control plane for named windows.

## Related

- [Git Workflow]({% link guides/git-workflow.md %}) -- pair isolated worktrees with isolated tmux windows
- [Agent Activation]({% link guides/agent-activation.md %}) -- load the right agents before kicking off background work
- [Export Context]({% link guides/export.md %}) -- hand the right context to another session or model
