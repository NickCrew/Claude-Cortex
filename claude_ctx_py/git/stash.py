"""Safe git stash operations.

Defaults to ``apply`` over ``pop`` (keeps the stash entry).
``drop`` requires an explicit ``confirm=True`` to prevent accidental loss.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple

from .run import resolve_repo_root, run_git


def git_stash_save(
    message: Optional[str] = None,
    *,
    cwd: Optional[Path] = None,
) -> Tuple[int, str]:
    """Stash current changes with an optional message."""
    repo_root, err = resolve_repo_root(cwd)
    if err or repo_root is None:
        return 1, err or "Not a git repository"

    work_cwd = cwd or repo_root
    args: List[str] = ["stash", "push"]
    if message:
        args.extend(["-m", message])

    code, out, stash_err = run_git(args, work_cwd)
    if code != 0:
        detail = (stash_err or out or "").strip()
        return 1, f"Stash failed: {detail}"

    result = (out or "").strip()
    if "No local changes" in result:
        return 0, "No local changes to stash"
    return 0, result or "Changes stashed"


def git_stash_apply(
    index: int = 0,
    *,
    cwd: Optional[Path] = None,
) -> Tuple[int, str]:
    """Apply stash entry at *index* (keeps the stash)."""
    repo_root, err = resolve_repo_root(cwd)
    if err or repo_root is None:
        return 1, err or "Not a git repository"

    work_cwd = cwd or repo_root
    code, out, apply_err = run_git(
        ["stash", "apply", f"stash@{{{index}}}"], work_cwd
    )
    if code != 0:
        detail = (apply_err or out or "").strip()
        return 1, f"Stash apply failed: {detail}"

    return 0, f"Applied stash@{{{index}}}"


def git_stash_list(*, cwd: Optional[Path] = None) -> Tuple[int, str]:
    """List all stash entries."""
    repo_root, err = resolve_repo_root(cwd)
    if err or repo_root is None:
        return 1, err or "Not a git repository"

    work_cwd = cwd or repo_root
    code, out, list_err = run_git(["stash", "list"], work_cwd)
    if code != 0:
        detail = (list_err or out or "").strip()
        return 1, f"Stash list failed: {detail}"

    result = out.strip()
    if not result:
        return 0, "No stash entries"
    return 0, result


def git_stash_drop(
    index: int = 0,
    *,
    confirm: bool = False,
    cwd: Optional[Path] = None,
) -> Tuple[int, str]:
    """Drop stash entry at *index*.

    Requires ``confirm=True`` as a safety gate to prevent accidental loss.
    """
    if not confirm:
        return 1, "Use --confirm to drop stash entries"

    repo_root, err = resolve_repo_root(cwd)
    if err or repo_root is None:
        return 1, err or "Not a git repository"

    work_cwd = cwd or repo_root
    code, out, drop_err = run_git(
        ["stash", "drop", f"stash@{{{index}}}"], work_cwd
    )
    if code != 0:
        detail = (drop_err or out or "").strip()
        return 1, f"Stash drop failed: {detail}"

    return 0, f"Dropped stash@{{{index}}}"
