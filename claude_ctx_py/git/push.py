"""Safe git push with protected-branch enforcement.

Blocks ``--force`` on protected branches (main, master by default).
Resolves remote and branch defaults when not specified.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple

from .run import (
    get_current_branch,
    get_tracking_remote,
    is_protected_branch,
    resolve_repo_root,
    run_git,
)


def git_push(
    remote: Optional[str] = None,
    branch: Optional[str] = None,
    *,
    force: bool = False,
    cwd: Optional[Path] = None,
) -> Tuple[int, str]:
    """Push to remote with safety checks.

    Returns ``(exit_code, result_message)``.

    Safety:
    - Refuses ``--force`` on protected branches (main, master).
    - Resolves *remote* from tracking config when not given.
    - Resolves *branch* from current branch when not given.
    """
    repo_root, err = resolve_repo_root(cwd)
    if err or repo_root is None:
        return 1, err or "Not a git repository"

    work_cwd = cwd or repo_root

    # Resolve current branch
    current = get_current_branch(work_cwd)
    if not current:
        return 1, "Cannot determine current branch (detached HEAD?)"

    push_branch = branch or current

    # Block force-push to protected branches
    if force and is_protected_branch(push_branch):
        return 1, f"Refusing to force-push to protected branch: {push_branch}"

    # Resolve remote
    push_remote = remote
    if not push_remote:
        push_remote = get_tracking_remote(current, work_cwd)
    if not push_remote:
        return 1, (
            f"No tracking remote for branch '{current}'. "
            f"Try: git push -u origin {current}"
        )

    # Build command
    args: List[str] = ["push"]
    if force:
        args.append("--force")
    args.extend([push_remote, push_branch])

    code, out, push_err = run_git(args, work_cwd)
    if code != 0:
        detail = (push_err or out or "").strip()
        return 1, f"Push failed: {detail}"

    return 0, f"Pushed {push_branch} to {push_remote}"
