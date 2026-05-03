"""Tmux session lifecycle: session-new, session-kill, attach.

Where ``windows.py`` owns per-window CRUD, this module owns the
session it lives in. The two are kept apart because every project in
the project's convention gets its own tmux session — created by
``tmux session-new``, attached to via ``tmux attach``, torn down via
``tmux session-kill`` — and that lifecycle is independent of any
particular window's lifecycle.
"""

from __future__ import annotations

import os
import subprocess
from typing import Optional, Tuple

from .run import resolve_session, run_tmux


def tmux_session_new(
    name: Optional[str] = None,
    cwd: Optional[str] = None,
    window: str = "shell",
) -> Tuple[int, str]:
    """Idempotently create a tmux session.

    Returns success with an "already exists" message when *name*
    already resolves to a live session — safe to call from setup
    recipes that may run repeatedly. The session is created detached
    with one initial *window* (default ``shell``); subsequent
    ``cortex tmux new`` calls add to it.
    """
    sess = name.strip() if name and name.strip() else resolve_session()
    if not sess:
        return 1, "Session name required"

    code, _out, _err = run_tmux(["has-session", "-t", sess])
    if code == 0:
        return 0, f"Session '{sess}' already exists"

    args = ["new-session", "-d", "-s", sess, "-n", window]
    if cwd:
        args.extend(["-c", cwd])

    code, _out, tmux_err = run_tmux(args)
    if code != 0:
        return 1, f"Failed to create session: {tmux_err.strip()}"
    return 0, f"Created session: {sess}"


def tmux_session_kill(name: Optional[str] = None) -> Tuple[int, str]:
    """Kill a tmux session and every window in it.

    Errors loudly if the session does not exist — kill is destructive,
    silent failure is the wrong default. Callers that want
    fire-and-forget semantics should use ``2>/dev/null || true``.
    """
    sess = name.strip() if name and name.strip() else resolve_session()
    if not sess:
        return 1, "Session name required"

    code, _out, _err = run_tmux(["has-session", "-t", sess])
    if code != 0:
        return 1, f"Session '{sess}' not found"

    code, _out, tmux_err = run_tmux(["kill-session", "-t", sess])
    if code != 0:
        return 1, f"Failed to kill session: {tmux_err.strip()}"
    return 0, f"Killed session: {sess}"


def tmux_attach(
    name: Optional[str] = None,
    window: Optional[str] = None,
) -> Tuple[int, str]:
    """Attach to a session, or switch-client if already inside tmux.

    If *window* is provided, that window is selected before the
    attach/switch so the user lands on a known starting window.

    When the caller is already inside tmux (``$TMUX`` is set), this
    runs ``tmux switch-client`` and returns immediately. When called
    from a bare shell, ``tmux attach-session`` takes over the
    terminal until the user detaches; this function blocks for that
    duration and then returns.
    """
    sess = name.strip() if name and name.strip() else resolve_session()
    if not sess:
        return 1, "Session name required"

    code, _out, _err = run_tmux(["has-session", "-t", sess])
    if code != 0:
        return 1, f"Session '{sess}' not found"

    if window:
        target = f"{sess}:{window}"
        code, _out, tmux_err = run_tmux(["select-window", "-t", target])
        if code != 0:
            return 1, f"Failed to select window: {tmux_err.strip()}"

    if os.environ.get("TMUX"):
        code, _out, tmux_err = run_tmux(["switch-client", "-t", sess])
        if code != 0:
            return 1, f"Failed to switch: {tmux_err.strip()}"
        return 0, f"Switched to {sess}"

    try:
        result = subprocess.run(
            ["tmux", "attach-session", "-t", sess],
            check=False,
        )
    except FileNotFoundError:
        return 127, "tmux not found"
    return result.returncode, f"Detached from {sess}"
