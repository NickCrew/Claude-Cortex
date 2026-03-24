"""Backward-compatibility shim.

The canonical module is :mod:`claude_ctx_py.git.worktree`.
"""

from __future__ import annotations

from ..git.worktree import (  # noqa: F401
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
    "WorktreeInfo",
    "worktree_add",
    "worktree_clear_base_dir",
    "worktree_default_path",
    "worktree_discover",
    "worktree_get_base_dir",
    "worktree_list",
    "worktree_prune",
    "worktree_remove",
    "worktree_set_base_dir",
]
