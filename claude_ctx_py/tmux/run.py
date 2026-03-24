"""Shared tmux subprocess infrastructure.

Provides the low-level runner and session/window validation
that all other ``tmux/*`` modules build on.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

DEFAULT_LINES = 50


def resolve_session() -> str:
    """Derive the tmux session name.

    Uses ``$TMUX_SESSION`` if set, otherwise derives from the current
    working directory basename — lowercased with spaces replaced by hyphens.
    """
    env_session = os.environ.get("TMUX_SESSION", "").strip()
    if env_session:
        return env_session
    return Path.cwd().name.lower().replace(" ", "-")


def run_tmux(args: List[str]) -> Tuple[int, str, str]:
    """Run a tmux command and return ``(returncode, stdout, stderr)``."""
    try:
        result = subprocess.run(
            ["tmux", *args],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return 127, "", "tmux not found"
    except OSError as exc:
        return 1, "", str(exc)
    return result.returncode, result.stdout, result.stderr


def _target(session: str, window: str) -> str:
    """Build a tmux target string ``session:window``."""
    return f"{session}:{window}"


def ensure_session(session: Optional[str] = None) -> Tuple[str, Optional[str]]:
    """Verify that *session* exists.

    Returns ``(session_name, None)`` on success or
    ``(session_name, error_message)`` on failure.
    """
    sess = session or resolve_session()
    code, _out, _err = run_tmux(["has-session", "-t", sess])
    if code != 0:
        return sess, (
            f"Session '{sess}' not found. "
            "Hint: start one or set TMUX_SESSION."
        )
    return sess, None


def ensure_window(
    window: str,
    session: Optional[str] = None,
) -> Tuple[str, Optional[str]]:
    """Verify that *window* exists in *session*.

    Calls :func:`ensure_session` first, then checks the window list.
    Returns ``(session_name, None)`` on success or
    ``(session_name, error_message)`` on failure.
    """
    sess, err = ensure_session(session)
    if err:
        return sess, err

    code, out, _err = run_tmux(
        ["list-windows", "-t", sess, "-F", "#{window_name}"]
    )
    if code != 0:
        return sess, f"Failed to list windows in session '{sess}'"

    windows = [line.strip() for line in out.splitlines() if line.strip()]
    if window not in windows:
        avail = ", ".join(windows) if windows else "(none)"
        return sess, (
            f"Window '{window}' not found in session '{sess}'. "
            f"Available: {avail}"
        )
    return sess, None
