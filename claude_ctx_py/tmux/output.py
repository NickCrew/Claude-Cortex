"""Tmux output capture and monitoring: read, dump, status, running, wait, watch."""

from __future__ import annotations

import re
import time
from typing import Optional, Tuple

from .run import DEFAULT_LINES, _target, ensure_window, run_tmux

_PROMPT_RE = re.compile(r"[$❯›>#]\s*$")


def tmux_read(
    window: str,
    lines: int = DEFAULT_LINES,
    session: Optional[str] = None,
) -> Tuple[int, str]:
    """Capture the last *lines* lines from *window*."""
    if not window or not window.strip():
        return 1, "Window name required"

    sess, err = ensure_window(window, session)
    if err:
        return 1, err

    code, out, tmux_err = run_tmux(
        ["capture-pane", "-t", _target(sess, window), "-p", "-S", f"-{lines}"]
    )
    if code != 0:
        return 1, f"Failed to capture pane: {tmux_err.strip()}"
    return 0, out


def tmux_dump(
    window: str,
    session: Optional[str] = None,
) -> Tuple[int, str]:
    """Dump the entire scrollback buffer from *window*."""
    if not window or not window.strip():
        return 1, "Window name required"

    sess, err = ensure_window(window, session)
    if err:
        return 1, err

    code, out, tmux_err = run_tmux(
        ["capture-pane", "-t", _target(sess, window), "-p", "-S", "-"]
    )
    if code != 0:
        return 1, f"Failed to dump pane: {tmux_err.strip()}"
    return 0, out


def tmux_status(
    window: str,
    session: Optional[str] = None,
) -> Tuple[int, str]:
    """Show window name and last few lines of output."""
    if not window or not window.strip():
        return 1, "Window name required"

    sess, err = ensure_window(window, session)
    if err:
        return 1, err

    code, out, _err = run_tmux(
        ["capture-pane", "-t", _target(sess, window), "-p", "-S", "-3"]
    )
    if code != 0:
        return 1, "Failed to capture pane"

    # Take only the last 3 non-empty lines
    recent = [l for l in out.splitlines() if l.strip()][-3:]
    body = "\n".join(recent)
    return 0, f"window: {window}\nlast output:\n{body}"


def tmux_running(
    window: str,
    session: Optional[str] = None,
) -> Tuple[int, str]:
    """Check if a command appears to be running in *window*.

    Returns ``(0, "running")`` if a command seems active, or
    ``(1, "at prompt")`` if the pane looks idle at a shell prompt.
    """
    if not window or not window.strip():
        return 1, "Window name required"

    sess, err = ensure_window(window, session)
    if err:
        return 1, err

    code, out, _err = run_tmux(
        ["capture-pane", "-t", _target(sess, window), "-p"]
    )
    if code != 0:
        return 1, "Failed to capture pane"

    # Find the last non-empty line
    lines = [l for l in out.splitlines() if l.strip()]
    if not lines:
        return 0, "running"

    last_line = lines[-1]
    if _PROMPT_RE.search(last_line):
        return 1, "at prompt"
    return 0, "running"


def tmux_wait(
    window: str,
    timeout: int = 60,
    session: Optional[str] = None,
) -> Tuple[int, str]:
    """Wait for a command in *window* to complete (return to prompt).

    Polls every second up to *timeout* seconds.
    """
    if not window or not window.strip():
        return 1, "Window name required"

    sess, err = ensure_window(window, session)
    if err:
        return 1, err

    elapsed = 0
    while elapsed < timeout:
        rc, _msg = tmux_running(window, sess)
        if rc != 0:
            # rc == 1 means "at prompt" → command finished
            return 0, f"Command completed in {elapsed}s"
        time.sleep(1)
        elapsed += 1

    return 1, f"Timeout after {timeout}s (command may still be running)"


def tmux_watch(
    window: str,
    pattern: Optional[str] = None,
    timeout: int = 120,
    session: Optional[str] = None,
) -> Tuple[int, str]:
    """Wait for *pattern* to appear in *window* output, or for a prompt.

    If *pattern* is ``None``, waits for the command to finish (prompt detection).
    Polls every second up to *timeout* seconds.
    """
    if not window or not window.strip():
        return 1, "Window name required"

    sess, err = ensure_window(window, session)
    if err:
        return 1, err

    elapsed = 0
    target = _target(sess, window)

    while elapsed < timeout:
        if pattern:
            code, out, _err = run_tmux(
                ["capture-pane", "-t", target, "-p", "-S", "-20"]
            )
            if code == 0 and pattern in out:
                return 0, f"Pattern '{pattern}' found after {elapsed}s"
        else:
            rc, _msg = tmux_running(window, sess)
            if rc != 0:
                return 0, f"Prompt detected after {elapsed}s"

        time.sleep(1)
        elapsed += 1

    return 1, f"Timeout after {timeout}s"
