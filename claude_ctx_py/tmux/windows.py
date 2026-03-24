"""Tmux window management: list, create, kill."""

from __future__ import annotations

from typing import Optional, Tuple

from .run import _target, ensure_session, ensure_window, run_tmux


def tmux_list(session: Optional[str] = None) -> Tuple[int, str]:
    """List windows in the session."""
    sess, err = ensure_session(session)
    if err:
        return 1, err

    code, out, tmux_err = run_tmux(
        [
            "list-windows",
            "-t",
            sess,
            "-F",
            "#{window_index}: #{window_name} #{?window_active,(active),}",
        ]
    )
    if code != 0:
        return 1, f"Failed to list windows: {(tmux_err or out).strip()}"
    return 0, out.strip()


def tmux_new(window: str, session: Optional[str] = None) -> Tuple[int, str]:
    """Create a new window."""
    if not window or not window.strip():
        return 1, "Window name required"

    sess, err = ensure_session(session)
    if err:
        return 1, err

    code, _out, tmux_err = run_tmux(
        ["new-window", "-t", sess, "-n", window]
    )
    if code != 0:
        return 1, f"Failed to create window: {tmux_err.strip()}"
    return 0, f"Created window: {window}"


def tmux_kill(window: str, session: Optional[str] = None) -> Tuple[int, str]:
    """Kill a window."""
    if not window or not window.strip():
        return 1, "Window name required"

    sess, err = ensure_window(window, session)
    if err:
        return 1, err

    code, _out, tmux_err = run_tmux(
        ["kill-window", "-t", _target(sess, window)]
    )
    if code != 0:
        return 1, f"Failed to kill window: {tmux_err.strip()}"
    return 0, f"Killed window: {window}"
