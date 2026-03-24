"""Git operations package for Cortex CLI.

Provides safe, agent-friendly git commands with validation and atomicity checks.
"""

from __future__ import annotations

from .branch import git_branch_create, git_branch_switch
from .commit import git_commit
from .patch import git_patch
from .push import git_push
from .run import (
    check_dirty_tree,
    get_current_branch,
    get_tracking_remote,
    is_protected_branch,
    resolve_repo_root,
    run_git,
)
from .stash import git_stash_apply, git_stash_drop, git_stash_list, git_stash_save
from .validate import check_atomicity, validate_commit_message
from .worktree import (
    WorktreeInfo,
    worktree_add,
    worktree_clear_base_dir,
    worktree_default_path,
    worktree_discover,
    worktree_get_base_dir,
    worktree_list,
    worktree_prune,
    worktree_remove,
    worktree_set_base_dir,
)

__all__ = [
    # run
    "run_git",
    "resolve_repo_root",
    "is_protected_branch",
    "check_dirty_tree",
    "get_current_branch",
    "get_tracking_remote",
    # validate
    "validate_commit_message",
    "check_atomicity",
    # commit / patch
    "git_commit",
    "git_patch",
    # push
    "git_push",
    # stash
    "git_stash_save",
    "git_stash_apply",
    "git_stash_list",
    "git_stash_drop",
    # branch
    "git_branch_create",
    "git_branch_switch",
    # worktree
    "WorktreeInfo",
    "worktree_discover",
    "worktree_list",
    "worktree_add",
    "worktree_remove",
    "worktree_prune",
    "worktree_default_path",
    "worktree_get_base_dir",
    "worktree_set_base_dir",
    "worktree_clear_base_dir",
]
