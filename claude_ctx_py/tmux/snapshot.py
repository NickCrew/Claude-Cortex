"""Multi-session listing and orchestrator-style snapshots.

Where the rest of ``tmux/*`` operates on one window at a time,
this module surveys every session on the box. ``tmux_snapshot`` is
designed to be piped into an LLM context so an orchestrator agent
can answer "what is every other agent doing right now?" in one read.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from .run import run_tmux


def _list_sessions() -> Tuple[int, List[Tuple[str, bool, int]]]:
    """Return ``(rc, [(name, attached, windows), ...])``."""
    code, out, _err = run_tmux(
        [
            "list-sessions",
            "-F",
            "#{session_name}:#{session_attached}:#{session_windows}",
        ]
    )
    if code != 0:
        return code, []

    sessions: List[Tuple[str, bool, int]] = []
    for line in out.strip().splitlines():
        if not line:
            continue
        parts = line.split(":", 2)
        if len(parts) != 3:
            continue
        name, attached, windows = parts
        sessions.append((name, attached == "1", int(windows or 0)))
    return 0, sessions


def _list_windows(session: str) -> List[Tuple[int, str, bool]]:
    """Return ``[(index, name, active), ...]`` for *session*."""
    code, out, _err = run_tmux(
        [
            "list-windows",
            "-t",
            session,
            "-F",
            "#{window_index}:#{window_name}:#{window_active}",
        ]
    )
    if code != 0:
        return []

    windows: List[Tuple[int, str, bool]] = []
    for line in out.strip().splitlines():
        if not line:
            continue
        parts = line.split(":", 2)
        if len(parts) != 3:
            continue
        idx, name, active = parts
        try:
            windows.append((int(idx), name, active == "1"))
        except ValueError:
            continue
    return windows


def _capture(session: str, window_index: int, lines: int) -> str:
    code, out, _err = run_tmux(
        [
            "capture-pane",
            "-t",
            f"{session}:{window_index}",
            "-p",
            "-S",
            f"-{lines}",
        ]
    )
    return out if code == 0 else ""


def tmux_sessions() -> Tuple[int, str]:
    """List every tmux session with attached state and window count."""
    code, sessions = _list_sessions()
    if code != 0:
        return 1, "Failed to list sessions (is tmux running?)"
    if not sessions:
        return 0, "No tmux sessions"

    rows = [
        f"{name} ({'attached' if attached else 'detached'}): {n} windows"
        for name, attached, n in sessions
    ]
    return 0, "\n".join(rows)


def tmux_snapshot(
    lines: int = 10,
    session: Optional[str] = None,
) -> Tuple[int, str]:
    """Format a digest of every session/window with the last *lines* of output.

    If *session* is given, scope the snapshot to that session only.
    The output is plain text with section headers, intended for an
    LLM context window — small enough to skim, structured enough to
    reason about which window needs attention.
    """
    code, sessions = _list_sessions()
    if code != 0:
        return 1, "Failed to list sessions (is tmux running?)"

    if session is not None:
        sessions = [s for s in sessions if s[0] == session]
        if not sessions:
            return 1, f"Session '{session}' not found"

    if not sessions:
        return 0, "No tmux sessions"

    parts: List[str] = []
    for name, attached, _ in sessions:
        parts.append(
            f"=== {name} ({'attached' if attached else 'detached'}) ==="
        )
        windows = _list_windows(name)
        if not windows:
            parts.append("  (no windows)")
            continue
        for idx, win_name, active in windows:
            marker = " *" if active else ""
            parts.append(f"  [{idx}] {win_name}{marker}")
            content = _capture(name, idx, lines)
            recent = [ln for ln in content.splitlines() if ln.strip()][-lines:]
            if not recent:
                parts.append("    (empty)")
            else:
                for ln in recent:
                    parts.append(f"    | {ln}")
        parts.append("")

    return 0, "\n".join(parts).rstrip()
