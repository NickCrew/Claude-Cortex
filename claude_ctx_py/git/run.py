"""Shared git subprocess infrastructure.

Provides the low-level helpers that all other ``git/*`` modules build on:
a unified subprocess runner, repo-root resolution, and common safety checks.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import FrozenSet, List, Optional, Tuple

_DEFAULT_PROTECTED_BRANCHES: FrozenSet[str] = frozenset({"main", "master"})


def run_git(args: List[str], cwd: Optional[Path] = None) -> Tuple[int, str, str]:
    """Run a git command and return ``(returncode, stdout, stderr)``.

    *cwd* defaults to :func:`Path.cwd` when ``None``.
    """
    target = cwd or Path.cwd()
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=str(target),
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return 127, "", "git not found"
    except OSError as exc:
        return 1, "", str(exc)
    return result.returncode, result.stdout, result.stderr


def resolve_repo_root(cwd: Optional[Path] = None) -> Tuple[Optional[Path], Optional[str]]:
    """Resolve the git repository root.

    Returns ``(root_path, None)`` on success or ``(None, error_message)`` on failure.
    """
    base = cwd or Path.cwd()
    code, out, err = run_git(["rev-parse", "--show-toplevel"], base)
    if code != 0:
        message = (err or out or "Not a git repository").strip()
        return None, message
    root = out.strip()
    if not root:
        return None, "Failed to resolve git root"
    return Path(root), None


def is_protected_branch(
    branch: str,
    protected: Optional[FrozenSet[str]] = None,
) -> bool:
    """Return ``True`` if *branch* is in the protected set (default: main, master)."""
    return branch in (protected or _DEFAULT_PROTECTED_BRANCHES)


def check_dirty_tree(cwd: Optional[Path] = None) -> Tuple[bool, List[str]]:
    """Check for uncommitted changes.

    Returns ``(is_dirty, list_of_dirty_files)``.
    """
    code, out, _err = run_git(["status", "--porcelain"], cwd)
    if code != 0:
        return False, []
    files = [line[3:] for line in out.splitlines() if line.strip()]
    return bool(files), files


def get_current_branch(cwd: Optional[Path] = None) -> Optional[str]:
    """Return the current branch name, or ``None`` if detached / not in a repo."""
    code, out, _err = run_git(["branch", "--show-current"], cwd)
    if code != 0:
        return None
    branch = out.strip()
    return branch or None


def get_tracking_remote(branch: str, cwd: Optional[Path] = None) -> Optional[str]:
    """Return the remote name for *branch*'s tracking configuration, or ``None``."""
    code, out, _err = run_git(
        ["config", "--get", f"branch.{branch}.remote"], cwd
    )
    if code != 0:
        return None
    remote = out.strip()
    return remote or None
