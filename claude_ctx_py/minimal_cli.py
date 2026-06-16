"""Minimal Cortex CLI surface.

This entrypoint intentionally exposes only the operational commands agents need
in lightweight environments: git, tmux, statusline, hooks, and completions.
The command implementations stay shared with the full ``cortex`` CLI.
"""

from __future__ import annotations

import argparse
import importlib
import os
import sys
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Protocol, cast


class HookRunner(Protocol):
    def __call__(self) -> int: ...


HOOK_MANAGEMENT_COMMANDS = frozenset({"install"})


def _enable_argcomplete(parser: argparse.ArgumentParser) -> None:
    """Integrate argcomplete if it is available."""

    try:  # pragma: no cover - optional dependency
        import argcomplete
    except ImportError:  # pragma: no cover
        return

    argcomplete.autocomplete(parser)


def _print(text: str) -> None:
    sys.stdout.write(text + "\n")


def _build_completions_parser(subparsers: argparse._SubParsersAction[Any]) -> None:
    completions_parser = subparsers.add_parser(
        "completions",
        help="Print shell completion script to stdout",
    )
    completions_parser.add_argument(
        "shell",
        choices=["bash", "zsh", "fish"],
        help="Target shell",
    )


def _build_hooks_parser(subparsers: argparse._SubParsersAction[Any]) -> None:
    hooks_parser = subparsers.add_parser("hooks", help="Hook commands")
    hooks_sub = hooks_parser.add_subparsers(dest="hooks_command")

    from .hooks import HOOK_SUBCOMMANDS

    collisions = HOOK_MANAGEMENT_COMMANDS.intersection(HOOK_SUBCOMMANDS)
    if collisions:
        names = ", ".join(sorted(collisions))
        raise ValueError(f"Hook names collide with management commands: {names}")

    for hook_name, hook_meta in HOOK_SUBCOMMANDS.items():
        hooks_sub.add_parser(hook_name, help=hook_meta["help"])

    # Retired hook kept as a no-op so a stale registration exits cleanly.
    hooks_sub.add_parser(
        "skill-suggest",
        help="(retired no-op — run 'cortex hooks uninstall skill-suggest')",
    )

    hooks_install = hooks_sub.add_parser(
        "install",
        help="Register a cortex-minimal hook subcommand with a harness's hooks config",
    )
    hooks_install.add_argument(
        "name",
        choices=sorted(HOOK_SUBCOMMANDS.keys()),
        help="Hook subcommand to install",
    )
    hooks_install.add_argument(
        "--target",
        choices=["claude", "codex"],
        default="claude",
        help=(
            "Where to register the hook (default: claude -> ~/.claude/settings.json; "
            "codex -> ~/.codex/hooks.json)"
        ),
    )


def _build_statusline_parser(
    subparsers: argparse._SubParsersAction[Any],
) -> None:
    from . import statusline

    statusline_parser = subparsers.add_parser(
        "statusline", help="Render Claude Code status line"
    )
    statusline.add_statusline_arguments(statusline_parser)


def build_parser() -> argparse.ArgumentParser:
    """Build the ``cortex-minimal`` parser."""

    parser = argparse.ArgumentParser(
        prog="cortex-minimal",
        description=(
            "Minimal Cortex CLI: git, tmux, statusline, hooks, and completions"
        ),
    )
    parser.add_argument(
        "--cortex-root",
        dest="cortex_root",
        type=Path,
        help="Explicit path to the cortex package root (for development)",
    )

    subparsers = parser.add_subparsers(dest="command")

    from .cmd_git import build_git_parser
    from .cmd_tmux import build_tmux_parser

    build_git_parser(subparsers)
    build_tmux_parser(subparsers)
    _build_statusline_parser(subparsers)
    _build_hooks_parser(subparsers)
    _build_completions_parser(subparsers)

    return parser


def _handle_completions_command(
    args: argparse.Namespace,
    parser: argparse.ArgumentParser,
) -> int:
    from . import completions

    sys.stdout.write(completions.get_completion_script(args.shell, parser))
    return 0


def _run_hook_subcommand(subcommand: str) -> int:
    module_name = subcommand.replace("-", "_")
    package_name = __package__ or "claude_ctx_py"
    try:
        module = importlib.import_module(f".hooks.{module_name}", package=package_name)
    except ImportError as exc:
        _print(f"Hook implementation failed to import: {subcommand}: {exc}")
        return 1
    runner_obj = getattr(module, "run", None)
    if not callable(runner_obj):
        _print(f"Hook implementation missing: {subcommand}")
        return 1
    runner = cast(HookRunner, runner_obj)
    return runner()


def _handle_hooks_command(args: argparse.Namespace) -> int:
    from .hooks import HOOK_SUBCOMMANDS, install_hook_command

    # Retired hook: silent no-op (see cli._handle_hooks_command).
    if args.hooks_command == "skill-suggest":
        return 0

    if args.hooks_command in HOOK_SUBCOMMANDS:
        return _run_hook_subcommand(args.hooks_command)

    if args.hooks_command == "install":
        if args.name not in HOOK_SUBCOMMANDS:
            _print(f"Unknown hook: {args.name}")
            return 1
        meta = HOOK_SUBCOMMANDS[args.name]
        ok, message = install_hook_command(
            subcommand=args.name,
            event=meta["event"],
            matcher=meta["matcher"],
            target=args.target,
            command_prefix="cortex-minimal hooks",
        )
        _print(message)
        return 0 if ok else 1

    _print("Hooks command required. Use 'cortex-minimal hooks --help' for options.")
    return 1


def _handle_statusline_command(args: argparse.Namespace) -> int:
    from . import statusline

    return cast(int, statusline.render_statusline(args))


def _handle_git_command(args: argparse.Namespace) -> int:
    from .cmd_git import handle_git_command

    return cast(int, handle_git_command(args))


def _handle_tmux_command(args: argparse.Namespace) -> int:
    from .cmd_tmux import handle_tmux_command

    return cast(int, handle_tmux_command(args))


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    _enable_argcomplete(parser)
    args = parser.parse_args(list(argv) if argv is not None else None)

    if getattr(args, "cortex_root", None):
        os.environ["CORTEX_ROOT"] = str(args.cortex_root)

    handlers: Dict[str, Callable[[argparse.Namespace], int]] = {
        "git": _handle_git_command,
        "tmux": _handle_tmux_command,
        "statusline": _handle_statusline_command,
        "hooks": _handle_hooks_command,
        "completions": lambda ns: _handle_completions_command(ns, parser),
    }

    handler = handlers.get(args.command)
    if handler is None:
        parser.print_help()
        return 1

    return handler(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
