# Service patterns (svc-* family)

The `svc-*` family is what makes these justfiles agent-friendly: every
long-running local service has a tmux-backgrounded sibling so an agent can
start it, read its output, and kill it without holding a foreground
process. This file documents the full surface area.

## The two-recipe pattern

For every long-lived service, emit **two parallel recipes**:

| Foreground (humans)         | Background (agents)                        |
| --------------------------- | ------------------------------------------ |
| `dev`        — Vite/Next/…  | `svc-dev`        — same, in tmux window    |
| `dev-proxy`  — proxy server | `svc-proxy`      — same, in tmux window    |
| `dev-worker` — queue worker | `svc-worker`     — same, in tmux window    |

The foreground variant is a one-liner that runs the package script. The
background variant delegates to `_svc-start` with the window name and
either the same package script or a `scripts/tx-start-<role>.sh` wrapper
(preferred when env activation is needed — see below).

## The internal helpers (`_svc-start`, `_svc-stop`)

These are private (underscore-prefixed) parameterized recipes that contain
the tmux logic. Every public `svc-*` recipe delegates to them so the tmux
boilerplate lives in exactly one place.

```just
_svc-start window cmd: tmux-new
    @session="{{ svc_session }}"; window="{{ window }}"; cmd="{{ cmd }}"; \
    if tmux list-windows -t "$session" -F "#{window_name}" | grep -qx "$window"; then \
        if cortex tmux running "$window" >/dev/null 2>&1; then \
            echo "$window is already running"; \
        else \
            tmux send-keys -t "$session:$window" "cd \"$PWD\" && $cmd" C-m; \
        fi; \
    else \
        tmux new-window -d -t "$session:" -n "$window"; \
        tmux send-keys -t "$session:$window" "cd \"$PWD\" && $cmd" C-m; \
    fi
    @cortex tmux read {{ window }} 20
```

A new svc recipe is a one-liner:

```just
svc-worker:
    @just _svc-start {{ tmux_worker_window }} "./scripts/tx-start-worker.sh"
```

## The full svc-* surface

Every justfile that has any service should expose this complete surface,
not just `svc-up`/`svc-down`. The orthogonal verbs are what make these
recipes agent-callable — an agent often needs to `svc-status` before
deciding whether to `svc-restart` something.

| Recipe                  | What it does                                          |
| ----------------------- | ----------------------------------------------------- |
| `tmux-new`              | Idempotently create the session.                      |
| `svc-<role>`            | Start one service window.                             |
| `svc-stop-<role>`       | Stop one service window.                              |
| `svc-restart-<role>`    | Stop then start one service window.                   |
| `svc-up`                | Start every service window. Deps: every `svc-<role>`. |
| `svc-stop` / `svc-down` | Stop every service window. Deps: every stop recipe.   |
| `svc-restart`           | Stop every service window, then start them all.       |
| `svc-reset`             | Kill the whole session and recreate it (the nuke).    |
| `svc-list`              | `cortex tmux list` — show every window.               |
| `svc-status`            | Per-service status block (loop, don't grep).          |
| `svc-read-<role>`       | Tail recent output (`cortex tmux read <window> 50`).  |
| `svc-session`           | Echo the session name (script-friendly).              |
| `svc-shell`             | Switch/attach to the session's shell window.          |
| `svc-attach`            | Alias for `svc-shell`.                                |

## The cortex tmux CLI

`cortex tmux` is the project-standard wrapper around raw tmux. Always use
it instead of `tmux capture-pane` / `tmux kill-window` / etc. — it gives
consistent error handling and stays compatible with future cortex changes.

| Command                          | Use case                                        |
| -------------------------------- | ----------------------------------------------- |
| `cortex tmux read <win> [N]`     | Tail last N lines of the window (default 30).   |
| `cortex tmux status <win>`       | Pid + run state of the process in the window.   |
| `cortex tmux running <win>`      | Exit 0 iff the window's process is running.     |
| `cortex tmux kill <win>`         | Stop the window's process and close the window. |
| `cortex tmux list`               | List all windows in the active service session. |

When wrapping or extending svc recipes, prefer these over `tmux send-keys
'kill-pane'` and friends.

## The tx-start-<role>.sh wrapper

The wrapper script in `scripts/tx-start-<role>.sh` exists to keep
**machine-specific runtime activation** out of the justfile. The justfile
should be portable across machines and CI; the wrapper is where nvm /
asdf / venv activation lives.

A wrapper script:

1. Resolves the project root from its own location, so the recipe can call
   it with any cwd.
2. Activates the runtime (nvm/asdf/uv/etc.) if applicable.
3. Sets env defaults (`PORT`, `DATABASE_URL`, …) using `${VAR:-default}`
   so the parent shell wins.
4. `exec`s the actual service command, so the wrapper PID becomes the
   service PID and `cortex tmux running` reflects reality.

See `assets/tx-start.sh.tmpl`.

## When to add a new service

A new `svc-*` recipe is justified when:

- The process is long-running (more than ~10s).
- A developer would otherwise want a dedicated terminal tab for it.
- It has logs an agent might need to read.

Skip the svc treatment for:

- One-shot tasks (migrations, seeders, codegen) — keep them as plain recipes.
- Things that already daemonize themselves (e.g., `brew services`-managed
  postgres, docker-compose services). Add a comment noting how to start
  them but do not wrap them in `svc-*`.

## When to add a TMUX_SESSION env override

The env override (`svc_session := env("TMUX_SESSION", project)`) is for
two cases:

1. A developer wants to run two checkouts of the same repo simultaneously
   without their tmux windows colliding.
2. CI or a test harness wants an isolated session per job.

Document the env var in the project README so contributors know it exists,
but do NOT set it in the justfile, .env, or shell rc — leave it unset by
default so the project slug wins.
