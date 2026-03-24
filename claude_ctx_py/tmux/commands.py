"""Tmux command sending: send, type, keys, interrupt."""

from __future__ import annotations

import time
from typing import Optional, Tuple

from .run import _target, ensure_window, run_tmux


def tmux_send(
    window: str,
    command: str,
    session: Optional[str] = None,
) -> Tuple[int, str]:
    """Send a command to *window* (presses Enter).

    Sends ``C-c`` first to clear any partial input.
    """
    if not window or not window.strip():
        return 1, "Window name required"
    if not command:
        return 1, "Command required"

    sess, err = ensure_window(window, session)
    if err:
        return 1, err

    target = _target(sess, window)

    # Clear partial input
    run_tmux(["send-keys", "-t", target, "C-c"])
    time.sleep(0.1)

    code, _out, tmux_err = run_tmux(
        ["send-keys", "-t", target, command, "Enter"]
    )
    if code != 0:
        return 1, f"Failed to send command: {tmux_err.strip()}"
    return 0, f"Sent to {window}: {command}"


def tmux_type(
    window: str,
    text: str,
    session: Optional[str] = None,
) -> Tuple[int, str]:
    """Type text into *window* without pressing Enter."""
    if not window or not window.strip():
        return 1, "Window name required"

    sess, err = ensure_window(window, session)
    if err:
        return 1, err

    code, _out, tmux_err = run_tmux(
        ["send-keys", "-t", _target(sess, window), text]
    )
    if code != 0:
        return 1, f"Failed to type text: {tmux_err.strip()}"
    return 0, f"Typed to {window}"


def tmux_keys(
    window: str,
    keys: str,
    session: Optional[str] = None,
) -> Tuple[int, str]:
    """Send a key sequence to *window* (e.g. ``C-c``, ``Enter``, ``Up``)."""
    if not window or not window.strip():
        return 1, "Window name required"
    if not keys:
        return 1, "Keys required"

    sess, err = ensure_window(window, session)
    if err:
        return 1, err

    # Split keys so tmux receives them as separate arguments
    key_args = keys.split()
    code, _out, tmux_err = run_tmux(
        ["send-keys", "-t", _target(sess, window), *key_args]
    )
    if code != 0:
        return 1, f"Failed to send keys: {tmux_err.strip()}"
    return 0, f"Sent keys to {window}: {keys}"


def tmux_interrupt(
    window: str,
    session: Optional[str] = None,
) -> Tuple[int, str]:
    """Send ``Ctrl-C`` to *window*."""
    if not window or not window.strip():
        return 1, "Window name required"

    sess, err = ensure_window(window, session)
    if err:
        return 1, err

    code, _out, tmux_err = run_tmux(
        ["send-keys", "-t", _target(sess, window), "C-c"]
    )
    if code != 0:
        return 1, f"Failed to send interrupt: {tmux_err.strip()}"
    return 0, f"Sent interrupt to: {window}"
