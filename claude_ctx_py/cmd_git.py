"""CLI parser and handler for ``cortex git`` subcommands.

Delegates to :mod:`claude_ctx_py.git` for all domain logic.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any


def build_git_parser(subparsers: argparse._SubParsersAction[Any]) -> None:
    """Register the ``cortex git`` parser tree."""
    git_parser = subparsers.add_parser("git", help="Safe git operations")
    git_sub = git_parser.add_subparsers(dest="git_command")

    # --- commit ---
    commit_parser = git_sub.add_parser(
        "commit", help="Stage files and commit atomically"
    )
    commit_parser.add_argument("message", help="Commit message")
    commit_parser.add_argument("files", nargs="+", help="Files to stage and commit")
    commit_parser.add_argument(
        "--force",
        action="store_true",
        help="Remove stale git lock files and retry",
    )

    # --- patch ---
    patch_parser = git_sub.add_parser(
        "patch", help="Apply diff hunks to the index and commit"
    )
    patch_parser.add_argument("message", help="Commit message")
    patch_parser.add_argument(
        "--diff",
        dest="diff_files",
        action="append",
        required=True,
        help="Diff file path (use - for stdin; repeatable)",
    )
    patch_parser.add_argument(
        "files", nargs="+", help="Files allowed in the patch"
    )
    patch_parser.add_argument(
        "--force",
        action="store_true",
        help="Remove stale git lock files and retry",
    )

    # --- push ---
    push_parser = git_sub.add_parser("push", help="Push with safety checks")
    push_parser.add_argument(
        "remote", nargs="?", help="Remote name (default: tracking remote)"
    )
    push_parser.add_argument(
        "branch", nargs="?", help="Branch name (default: current branch)"
    )
    push_parser.add_argument(
        "--force",
        action="store_true",
        help="Force push (blocked on protected branches)",
    )

    # --- stash ---
    stash_parser = git_sub.add_parser("stash", help="Safe stash operations")
    stash_sub = stash_parser.add_subparsers(dest="stash_command")

    stash_save = stash_sub.add_parser("save", help="Stash current changes")
    stash_save.add_argument(
        "stash_message", nargs="?", help="Optional stash message"
    )

    stash_apply = stash_sub.add_parser(
        "apply", help="Apply a stash entry (keeps the stash)"
    )
    stash_apply.add_argument(
        "stash_index", nargs="?", type=int, default=0, help="Stash index (default: 0)"
    )

    stash_sub.add_parser("list", help="List stash entries")

    stash_drop = stash_sub.add_parser("drop", help="Drop a stash entry")
    stash_drop.add_argument(
        "stash_index", nargs="?", type=int, default=0, help="Stash index (default: 0)"
    )
    stash_drop.add_argument(
        "--confirm",
        action="store_true",
        help="Required to actually drop the entry",
    )

    # --- branch ---
    branch_parser = git_sub.add_parser("branch", help="Safe branch operations")
    branch_sub = branch_parser.add_subparsers(dest="branch_command")

    branch_create = branch_sub.add_parser(
        "create", help="Create a new branch (does not switch)"
    )
    branch_create.add_argument("name", help="Branch name")
    branch_create.add_argument(
        "--from",
        dest="from_ref",
        help="Base ref to branch from (default: HEAD)",
    )

    branch_switch = branch_sub.add_parser(
        "switch", help="Switch branch (refuses on dirty tree)"
    )
    branch_switch.add_argument("name", help="Branch name to switch to")

    # --- worktree ---
    wt_parser = git_sub.add_parser("worktree", help="Git worktree management")
    wt_sub = wt_parser.add_subparsers(dest="wt_command")

    wt_sub.add_parser("list", help="List git worktrees")

    wt_add = wt_sub.add_parser("add", help="Add a new worktree")
    wt_add.add_argument("wt_branch", metavar="branch", help="Branch name")
    wt_add.add_argument(
        "--path", dest="wt_path", help="Target path for the worktree"
    )
    wt_add.add_argument(
        "--base", dest="wt_base", help="Base ref for a new branch (default: HEAD)"
    )
    wt_add.add_argument(
        "--force", action="store_true", help="Force even if branch is checked out"
    )
    wt_add.add_argument(
        "--no-gitignore",
        dest="wt_gitignore",
        action="store_false",
        help="Skip updating .gitignore",
    )

    wt_remove = wt_sub.add_parser("remove", help="Remove a worktree")
    wt_remove.add_argument("target", help="Worktree path or branch name")
    wt_remove.add_argument(
        "--force", action="store_true", help="Force removal of dirty worktree"
    )

    wt_prune = wt_sub.add_parser("prune", help="Prune stale worktrees")
    wt_prune.add_argument(
        "--dry-run", dest="wt_dry_run", action="store_true", help="Show only"
    )
    wt_prune.add_argument(
        "--verbose", dest="wt_verbose", action="store_true", help="Verbose output"
    )

    wt_dir = wt_sub.add_parser("dir", help="Show or set worktree base directory")
    wt_dir.add_argument("path", nargs="?", help="Set base directory")
    wt_dir.add_argument(
        "--clear", action="store_true", help="Clear configured base directory"
    )


def _print(text: str) -> None:
    sys.stdout.write(text + "\n")


def handle_git_command(args: argparse.Namespace) -> int:
    """Dispatch ``cortex git <subcommand>``."""
    from . import git

    cmd = getattr(args, "git_command", None)

    if cmd == "commit":
        code, msg = git.git_commit(
            args.message,
            args.files,
            force_lock=getattr(args, "force", False),
        )
        _print(msg)
        return code

    if cmd == "patch":
        diff_content = _read_diff_inputs(getattr(args, "diff_files", []))
        if diff_content is None:
            return 1
        code, msg = git.git_patch(
            args.message,
            args.files,
            diff_content,
            force_lock=getattr(args, "force", False),
        )
        _print(msg)
        return code

    if cmd == "push":
        code, msg = git.git_push(
            getattr(args, "remote", None),
            getattr(args, "branch", None),
            force=getattr(args, "force", False),
        )
        _print(msg)
        return code

    if cmd == "stash":
        return _handle_stash(args)

    if cmd == "branch":
        return _handle_branch(args)

    if cmd == "worktree":
        return _handle_worktree(args)

    _print("Git subcommand required. Use 'cortex git --help' for options.")
    return 1


def _read_diff_inputs(diff_files: list[str]) -> str | None:
    """Read and concatenate diff file content.  Returns ``None`` on error."""
    parts: list[str] = []
    for path in diff_files:
        if path == "-":
            if sys.stdin.isatty():
                sys.stderr.write("Error: --diff - requires piped input, not a terminal\n")
                return None
            parts.append(sys.stdin.read())
        else:
            try:
                parts.append(Path(path).read_text(encoding="utf-8"))
            except OSError as exc:
                sys.stderr.write(f"Error: Cannot read diff file: {exc}\n")
                return None
    return "\n".join(parts)


def _handle_stash(args: argparse.Namespace) -> int:
    from . import git

    sub = getattr(args, "stash_command", None)

    if sub == "save":
        code, msg = git.git_stash_save(
            message=getattr(args, "stash_message", None),
        )
        _print(msg)
        return code

    if sub == "apply":
        code, msg = git.git_stash_apply(
            index=getattr(args, "stash_index", 0),
        )
        _print(msg)
        return code

    if sub == "list":
        code, msg = git.git_stash_list()
        _print(msg)
        return code

    if sub == "drop":
        code, msg = git.git_stash_drop(
            index=getattr(args, "stash_index", 0),
            confirm=getattr(args, "confirm", False),
        )
        _print(msg)
        return code

    _print("Stash subcommand required. Use 'cortex git stash --help' for options.")
    return 1


def _handle_branch(args: argparse.Namespace) -> int:
    from . import git

    sub = getattr(args, "branch_command", None)

    if sub == "create":
        code, msg = git.git_branch_create(
            args.name,
            from_ref=getattr(args, "from_ref", None),
        )
        _print(msg)
        return code

    if sub == "switch":
        code, msg = git.git_branch_switch(args.name)
        _print(msg)
        return code

    _print("Branch subcommand required. Use 'cortex git branch --help' for options.")
    return 1


def _handle_worktree(args: argparse.Namespace) -> int:
    from . import git

    sub = getattr(args, "wt_command", None)

    if sub == "list":
        code, msg = git.worktree_list()
        _print(msg)
        return code

    if sub == "add":
        code, msg = git.worktree_add(
            args.wt_branch,
            path=getattr(args, "wt_path", None),
            base=getattr(args, "wt_base", None),
            force=getattr(args, "force", False),
            ensure_gitignore=getattr(args, "wt_gitignore", True),
        )
        _print(msg)
        return code

    if sub == "remove":
        code, msg = git.worktree_remove(
            args.target,
            force=getattr(args, "force", False),
        )
        _print(msg)
        return code

    if sub == "prune":
        code, msg = git.worktree_prune(
            dry_run=getattr(args, "wt_dry_run", False),
            verbose=getattr(args, "wt_verbose", False),
        )
        _print(msg)
        return code

    if sub == "dir":
        if getattr(args, "clear", False):
            code, msg = git.worktree_clear_base_dir()
            _print(msg)
            return code
        path = getattr(args, "path", None)
        if path:
            code, msg = git.worktree_set_base_dir(path)
            _print(msg)
            return code
        base_dir, source, error = git.worktree_get_base_dir()
        if error:
            _print(error)
            return 1
        if base_dir:
            _print(f"{base_dir} ({source})")
            return 0
        _print("No worktree base directory configured")
        return 0

    _print("Worktree subcommand required. Use 'cortex git worktree --help'.")
    return 1
