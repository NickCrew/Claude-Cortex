"""Tmux operations package for Cortex CLI.

Provides agent-friendly tmux window management and output capture.
"""

from __future__ import annotations

from .commands import tmux_interrupt, tmux_keys, tmux_send, tmux_type
from .justfile import tmux_justfile
from .output import tmux_dump, tmux_read, tmux_running, tmux_status, tmux_wait, tmux_watch
from .run import resolve_session, run_tmux
from .windows import tmux_kill, tmux_list, tmux_new

__all__ = [
    # run
    "run_tmux",
    "resolve_session",
    # windows
    "tmux_list",
    "tmux_new",
    "tmux_kill",
    # commands
    "tmux_send",
    "tmux_type",
    "tmux_keys",
    "tmux_interrupt",
    # output
    "tmux_read",
    "tmux_dump",
    "tmux_status",
    "tmux_running",
    "tmux_wait",
    "tmux_watch",
    # generation
    "tmux_justfile",
]
