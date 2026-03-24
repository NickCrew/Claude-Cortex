"""Unit tests for claude_ctx_py.git.stash."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from claude_ctx_py.git.stash import (
    git_stash_apply,
    git_stash_drop,
    git_stash_list,
    git_stash_save,
)

_MOD = "claude_ctx_py.git.stash"


@pytest.mark.unit
class TestGitStashSave:
    @patch(f"{_MOD}.run_git", return_value=(0, "Saved working directory\n", ""))
    @patch(f"{_MOD}.resolve_repo_root", return_value=(Path("/repo"), None))
    def test_save_success(self, _root, _run):
        code, msg = git_stash_save("wip")
        assert code == 0

    @patch(f"{_MOD}.run_git", return_value=(0, "No local changes to save\n", ""))
    @patch(f"{_MOD}.resolve_repo_root", return_value=(Path("/repo"), None))
    def test_no_changes(self, _root, _run):
        code, msg = git_stash_save()
        assert code == 0
        assert "no local" in msg.lower()

    @patch(f"{_MOD}.resolve_repo_root", return_value=(None, "Not a git repository"))
    def test_not_in_repo(self, _root):
        code, msg = git_stash_save()
        assert code == 1


@pytest.mark.unit
class TestGitStashApply:
    @patch(f"{_MOD}.run_git", return_value=(0, "", ""))
    @patch(f"{_MOD}.resolve_repo_root", return_value=(Path("/repo"), None))
    def test_apply_success(self, _root, _run):
        code, msg = git_stash_apply(0)
        assert code == 0
        assert "stash@{0}" in msg

    @patch(f"{_MOD}.run_git", return_value=(1, "", "conflict"))
    @patch(f"{_MOD}.resolve_repo_root", return_value=(Path("/repo"), None))
    def test_apply_conflict(self, _root, _run):
        code, msg = git_stash_apply(0)
        assert code == 1


@pytest.mark.unit
class TestGitStashList:
    @patch(f"{_MOD}.run_git", return_value=(0, "stash@{0}: WIP\nstash@{1}: fix\n", ""))
    @patch(f"{_MOD}.resolve_repo_root", return_value=(Path("/repo"), None))
    def test_has_entries(self, _root, _run):
        code, msg = git_stash_list()
        assert code == 0
        assert "stash@{0}" in msg

    @patch(f"{_MOD}.run_git", return_value=(0, "", ""))
    @patch(f"{_MOD}.resolve_repo_root", return_value=(Path("/repo"), None))
    def test_empty(self, _root, _run):
        code, msg = git_stash_list()
        assert code == 0
        assert "no stash" in msg.lower()


@pytest.mark.unit
class TestGitStashDrop:
    def test_drop_without_confirm_refused(self):
        code, msg = git_stash_drop(0, confirm=False)
        assert code == 1
        assert "--confirm" in msg

    @patch(f"{_MOD}.run_git", return_value=(0, "", ""))
    @patch(f"{_MOD}.resolve_repo_root", return_value=(Path("/repo"), None))
    def test_drop_with_confirm(self, _root, _run):
        code, msg = git_stash_drop(0, confirm=True)
        assert code == 0
        assert "stash@{0}" in msg

    @patch(f"{_MOD}.run_git", return_value=(1, "", "not exist"))
    @patch(f"{_MOD}.resolve_repo_root", return_value=(Path("/repo"), None))
    def test_drop_invalid_index(self, _root, _run):
        code, msg = git_stash_drop(99, confirm=True)
        assert code == 1
