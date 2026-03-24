"""Safe git branch operations.

``switch`` refuses when the working tree is dirty.
``create`` does not switch — agents stay on their current branch.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple

from .run import check_dirty_tree, resolve_repo_root, run_git


def git_branch_create(
    name: str,
    *,
    from_ref: Optional[str] = None,
    cwd: Optional[Path] = None,
) -> Tuple[int, str]:
    """Create a new branch without switching to it.

    If *from_ref* is given the branch starts from that ref, otherwise from HEAD.
    """
    repo_root, err = resolve_repo_root(cwd)
    if err or repo_root is None:
        return 1, err or "Not a git repository"

    work_cwd = cwd or repo_root
    name = name.strip()
    if not name:
        return 1, "Branch name is required"

    args: List[str] = ["branch", name]
    if from_ref:
        args.append(from_ref)

    code, out, branch_err = run_git(args, work_cwd)
    if code != 0:
        detail = (branch_err or out or "").strip()
        return 1, f"Branch creation failed: {detail}"

    if from_ref:
        return 0, f"Created branch '{name}' from {from_ref}"
    return 0, f"Created branch '{name}'"


def git_branch_switch(
    name: str,
    *,
    cwd: Optional[Path] = None,
) -> Tuple[int, str]:
    """Switch to *name*.  Refuses if the working tree has uncommitted changes."""
    repo_root, err = resolve_repo_root(cwd)
    if err or repo_root is None:
        return 1, err or "Not a git repository"

    work_cwd = cwd or repo_root
    name = name.strip()
    if not name:
        return 1, "Branch name is required"

    # Safety: refuse on dirty tree
    dirty, dirty_files = check_dirty_tree(work_cwd)
    if dirty:
        file_list = "\n  ".join(dirty_files[:10])
        suffix = ""
        if len(dirty_files) > 10:
            suffix = f"\n  ... and {len(dirty_files) - 10} more"
        return 1, (
            "Working tree has uncommitted changes:\n"
            f"  {file_list}{suffix}\n"
            "Commit or stash before switching."
        )

    code, out, switch_err = run_git(["switch", name], work_cwd)
    if code != 0:
        detail = (switch_err or out or "").strip()
        return 1, f"Switch failed: {detail}"

    return 0, f"Switched to branch '{name}'"
