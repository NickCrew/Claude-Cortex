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


def tmux_new(
    window: str,
    session: Optional[str] = None,
    cwd: Optional[str] = None,
) -> Tuple[int, str]:
    """Create a new window.

    If *cwd* is provided, pass it as ``-c`` so the new window's shell
    starts there. Otherwise tmux falls back to the directory where the
    tmux *server* was started, which is rarely what callers want — the
    CLI handler defaults *cwd* to the current working directory to
    prevent that surprise.
    """
    if not window or not window.strip():
        return 1, "Window name required"

    sess, err = ensure_session(session)
    if err:
        return 1, err

    args = ["new-window", "-t", sess, "-n", window]
    if cwd:
        args.extend(["-c", cwd])

    code, _out, tmux_err = run_tmux(args)
    if code != 0:
        return 1, f"Failed to create window: {tmux_err.strip()}"
    return 0, f"Created window: {window}"


def tmux_rename(
    old: str,
    new: str,
    session: Optional[str] = None,
) -> Tuple[int, str]:
    """Rename window *old* to *new*.

    Useful for self-labeling: an agent that takes over a window can
    relabel it (e.g. ``Claude-Frontend``) so a sibling agent surveying
    sessions via ``tmux snapshot`` knows what each window is for.
    """
    if not old or not old.strip():
        return 1, "Old window name required"
    if not new or not new.strip():
        return 1, "New window name required"

    sess, err = ensure_window(old, session)
    if err:
        return 1, err

    code, _out, tmux_err = run_tmux(
        ["rename-window", "-t", _target(sess, old), new]
    )
    if code != 0:
        return 1, f"Failed to rename window: {tmux_err.strip()}"
    return 0, f"Renamed {old} -> {new}"


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
