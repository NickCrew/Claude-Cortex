"""CLI parser and handler for ``cortex tmux`` subcommands.

Delegates to :mod:`claude_ctx_py.tmux` for all domain logic.
"""

from __future__ import annotations

import argparse
import sys
from typing import Any


def build_tmux_parser(subparsers: argparse._SubParsersAction[Any]) -> None:
    """Register the ``cortex tmux`` parser tree."""
    tmux_parser = subparsers.add_parser(
        "tmux", help="Tmux window management for agents"
    )
    tmux_sub = tmux_parser.add_subparsers(dest="tmux_command")

    # --- list ---
    tmux_sub.add_parser("list", help="List windows in session")

    # --- new ---
    new_parser = tmux_sub.add_parser("new", help="Create a new window")
    new_parser.add_argument("window", help="Window name")

    # --- kill ---
    kill_parser = tmux_sub.add_parser("kill", help="Kill a window")
    kill_parser.add_argument("window", help="Window name")

    # --- send ---
    send_parser = tmux_sub.add_parser(
        "send", help="Send command to window (presses Enter)"
    )
    send_parser.add_argument("window", help="Window name")
    send_parser.add_argument(
        "command_parts",
        nargs="+",
        metavar="command",
        help="Command to send",
    )

    # --- type ---
    type_parser = tmux_sub.add_parser(
        "type", help="Type text without pressing Enter"
    )
    type_parser.add_argument("window", help="Window name")
    type_parser.add_argument("text", nargs="*", default=[], help="Text to type")

    # --- keys ---
    keys_parser = tmux_sub.add_parser(
        "keys", help="Send key sequence (e.g. C-c, Enter, Up)"
    )
    keys_parser.add_argument("window", help="Window name")
    keys_parser.add_argument("key_sequence", nargs="+", help="Keys to send")

    # --- interrupt ---
    int_parser = tmux_sub.add_parser("interrupt", help="Send Ctrl-C to window")
    int_parser.add_argument("window", help="Window name")

    # --- read / tail ---
    read_parser = tmux_sub.add_parser(
        "read", aliases=["tail"], help="Capture last N lines (default: 50)"
    )
    read_parser.add_argument("window", help="Window name")
    read_parser.add_argument(
        "lines", nargs="?", type=int, default=50, help="Number of lines"
    )

    # --- dump ---
    dump_parser = tmux_sub.add_parser("dump", help="Dump entire scrollback buffer")
    dump_parser.add_argument("window", help="Window name")

    # --- status ---
    status_parser = tmux_sub.add_parser(
        "status", help="Check window exists and show last lines"
    )
    status_parser.add_argument("window", help="Window name")

    # --- running ---
    running_parser = tmux_sub.add_parser(
        "running", help="Exit 0 if command running, 1 if at prompt"
    )
    running_parser.add_argument("window", help="Window name")

    # --- wait ---
    wait_parser = tmux_sub.add_parser(
        "wait", help="Wait for command to complete (default: 60s)"
    )
    wait_parser.add_argument("window", help="Window name")
    wait_parser.add_argument(
        "timeout", nargs="?", type=int, default=60, help="Timeout in seconds"
    )

    # --- watch ---
    watch_parser = tmux_sub.add_parser(
        "watch", help="Wait for pattern to appear (or prompt if no pattern)"
    )
    watch_parser.add_argument("window", help="Window name")
    watch_parser.add_argument("pattern", nargs="?", help="Pattern to match")
    watch_parser.add_argument(
        "--timeout", type=int, default=120, help="Timeout in seconds (default: 120)"
    )

    # --- justfile ---
    jf_parser = tmux_sub.add_parser(
        "justfile",
        help="Generate Justfile service targets for this project",
    )
    jf_parser.add_argument(
        "--dir",
        "-d",
        default=None,
        help="Project directory (default: current directory)",
    )
    jf_parser.add_argument(
        "--prefix",
        "-p",
        default="svc",
        help="Target name prefix (default: svc)",
    )


def _print(text: str) -> None:
    sys.stdout.write(text + "\n")


def handle_tmux_command(args: argparse.Namespace) -> int:
    """Dispatch ``cortex tmux <subcommand>``."""
    from . import tmux

    cmd = getattr(args, "tmux_command", None)

    if cmd == "list":
        code, msg = tmux.tmux_list()
        _print(msg)
        return code

    if cmd == "new":
        code, msg = tmux.tmux_new(args.window)
        _print(msg)
        return code

    if cmd == "kill":
        code, msg = tmux.tmux_kill(args.window)
        _print(msg)
        return code

    if cmd == "send":
        command_str = " ".join(args.command_parts)
        code, msg = tmux.tmux_send(args.window, command_str)
        _print(msg)
        return code

    if cmd == "type":
        text_str = " ".join(args.text)
        code, msg = tmux.tmux_type(args.window, text_str)
        _print(msg)
        return code

    if cmd == "keys":
        keys_str = " ".join(args.key_sequence)
        code, msg = tmux.tmux_keys(args.window, keys_str)
        _print(msg)
        return code

    if cmd == "interrupt":
        code, msg = tmux.tmux_interrupt(args.window)
        _print(msg)
        return code

    if cmd in ("read", "tail"):
        code, msg = tmux.tmux_read(args.window, lines=args.lines)
        _print(msg)
        return code

    if cmd == "dump":
        code, msg = tmux.tmux_dump(args.window)
        _print(msg)
        return code

    if cmd == "status":
        code, msg = tmux.tmux_status(args.window)
        _print(msg)
        return code

    if cmd == "running":
        code, msg = tmux.tmux_running(args.window)
        _print(msg)
        return code

    if cmd == "wait":
        code, msg = tmux.tmux_wait(args.window, timeout=args.timeout)
        _print(msg)
        return code

    if cmd == "watch":
        code, msg = tmux.tmux_watch(
            args.window,
            pattern=getattr(args, "pattern", None),
            timeout=getattr(args, "timeout", 120),
        )
        _print(msg)
        return code

    if cmd == "justfile":
        code, msg = tmux.tmux_justfile(
            directory=getattr(args, "dir", None),
            prefix=getattr(args, "prefix", "svc"),
        )
        _print(msg)
        return code

    _print("Tmux subcommand required. Use 'cortex tmux --help' for options.")
    return 1
